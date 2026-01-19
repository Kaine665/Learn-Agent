"""
提取器基类

定义所有提取器的通用接口和能力：
1. 多次采样 + 合并
2. 重试机制
3. 进度追踪
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import json


@dataclass
class ExtractionResult:
    """提取结果"""
    success: bool
    data: Any = None                    # 提取到的数据
    confidence: float = 0.0             # 置信度
    merge_decisions: List[Dict] = field(default_factory=list)  # 合并决策
    error: Optional[str] = None         # 错误信息
    elapsed_time: float = 0.0           # 耗时（秒）


class SampleTracker:
    """采样状态追踪器"""
    
    def __init__(self, count: int):
        self.count = count
        self.lock = threading.Lock()
        self.states = {
            i: {"status": "等待中", "attempt": 0, "error": None, 
                "start_time": None, "end_time": None} 
            for i in range(count)
        }
    
    def update(self, idx: int, status: str, attempt: int = None, error: str = None):
        with self.lock:
            self.states[idx]["status"] = status
            if attempt is not None:
                self.states[idx]["attempt"] = attempt
            if error is not None:
                self.states[idx]["error"] = error
            if status == "分析中" and self.states[idx]["start_time"] is None:
                self.states[idx]["start_time"] = time.time()
            if status in ["完成", "失败"]:
                self.states[idx]["end_time"] = time.time()
            self._print_status()
    
    def get_elapsed(self, idx: int) -> str:
        s = self.states[idx]
        if s["start_time"] is None:
            return ""
        end = s["end_time"] or time.time()
        elapsed = int(end - s["start_time"])
        return f"{elapsed}s"
    
    def _print_status(self):
        parts = []
        for i in range(self.count):
            s = self.states[i]
            elapsed = self.get_elapsed(i)
            if s["status"] == "完成":
                parts.append(f"[{i+1}:✓{elapsed}]")
            elif s["status"] == "失败":
                parts.append(f"[{i+1}:✗{elapsed}]")
            elif s["status"] == "分析中":
                retry = f"r{s['attempt']}" if s['attempt'] > 1 else ""
                parts.append(f"[{i+1}:⏳{retry}{elapsed}]")
            else:
                parts.append(f"[{i+1}:·]")
        print(f"\r   状态: {' '.join(parts)}    ", end="", flush=True)


class BaseExtractor(ABC):
    """
    提取器基类
    
    子类需要实现：
    - _extract_once(): 单次提取逻辑
    - _merge_samples(): 合并多次采样结果
    - name: 提取器名称
    """
    
    name: str = "base"
    
    def __init__(self, sample_count: int = 3, max_retries: int = 3):
        self.sample_count = sample_count
        self.max_retries = max_retries
    
    @abstractmethod
    def _extract_once(self, image_path: str = None, image_base64: str = None) -> Dict[str, Any]:
        """
        单次提取（子类实现）
        
        Returns:
            {"success": bool, "data": dict, "error": str}
        """
        pass
    
    @abstractmethod
    def _merge_samples(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        合并多次采样结果（子类实现）
        
        Returns:
            {"success": bool, "data": dict, "merge_decisions": list, "confidence": float}
        """
        pass
    
    def extract(self, image_path: str = None, image_base64: str = None, 
                on_progress: Callable = None) -> ExtractionResult:
        """
        执行提取（多次采样 + 合并）
        
        Args:
            image_path: 图片路径
            image_base64: 图片base64编码
            on_progress: 进度回调 (step, progress, message)
        
        Returns:
            ExtractionResult
        """
        start_time = time.time()
        
        print(f"\n🔄 {self.name}：并行采样（{self.sample_count}次，每次最多重试{self.max_retries}次）")
        tracker = SampleTracker(self.sample_count)
        
        # 定义带重试的采样任务
        def do_sample_with_retry(idx: int):
            for attempt in range(1, self.max_retries + 1):
                tracker.update(idx, "分析中", attempt)
                try:
                    result = self._extract_once(
                        image_path=image_path,
                        image_base64=image_base64
                    )
                    if result.get("success"):
                        tracker.update(idx, "完成", attempt)
                        return idx, result, attempt
                except Exception as e:
                    if attempt == self.max_retries:
                        tracker.update(idx, "失败", attempt, str(e))
                        return idx, {"success": False, "error": str(e)}, attempt
            tracker.update(idx, "失败", self.max_retries, "重试次数用尽")
            return idx, {"success": False, "error": "重试次数用尽"}, self.max_retries
        
        # 并行执行采样
        samples = []
        with ThreadPoolExecutor(max_workers=self.sample_count) as executor:
            futures = [executor.submit(do_sample_with_retry, i) for i in range(self.sample_count)]
            for future in as_completed(futures):
                idx, result, attempts = future.result()
                if result.get("success"):
                    samples.append(result.get("data"))
        
        # 打印最终结果
        print()
        for i in range(self.sample_count):
            s = tracker.states[i]
            elapsed = tracker.get_elapsed(i)
            if s["status"] == "完成":
                retry_info = f"，重试{s['attempt']-1}次" if s['attempt'] > 1 else ""
                print(f"   ✓ 采样 {i+1} 完成（{elapsed}{retry_info}）")
            else:
                print(f"   ✗ 采样 {i+1} 失败（{elapsed}，重试{s['attempt']}次）: {s['error'] or '未知错误'}")
        
        # 检查有效采样数
        if len(samples) < 2:
            return ExtractionResult(
                success=False,
                error="有效采样数不足",
                elapsed_time=time.time() - start_time
            )
        
        # 合并采样结果
        print(f"\n🔀 {self.name}：合并 {len(samples)} 次采样结果...")
        merge_start = time.time()
        print(f"   状态: [合并:⏳0s]", end="", flush=True)
        
        merge_result = self._merge_samples(samples)
        merge_elapsed = int(time.time() - merge_start)
        
        if merge_result.get("success"):
            print(f"\r   状态: [合并:✓{merge_elapsed}s]    ")
            return ExtractionResult(
                success=True,
                data=merge_result.get("data"),
                confidence=merge_result.get("confidence", 0.0),
                merge_decisions=merge_result.get("merge_decisions", []),
                elapsed_time=time.time() - start_time
            )
        else:
            print(f"\r   状态: [合并:✗{merge_elapsed}s]    ")
            return ExtractionResult(
                success=False,
                error=merge_result.get("error", "合并失败"),
                elapsed_time=time.time() - start_time
            )

