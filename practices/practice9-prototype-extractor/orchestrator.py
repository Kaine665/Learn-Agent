"""
原型工作流编排器

负责协调各层组件，执行完整的原型提取-生成流程。
支持：
1. 单独执行某个阶段
2. 执行完整流程
3. 流程状态追踪（为前端展示预留）
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from pathlib import Path
import json

from specs import PrototypeSpec, LayoutSpec
from extractors import LayoutExtractor, ExtractionResult
from generators import HTMLGenerator, GenerationResult


@dataclass
class WorkflowState:
    """工作流状态（面向前端展示）"""
    # 当前阶段
    current_stage: str = "idle"  # idle -> extracting -> merging -> generating -> done
    
    # 各阶段状态
    stages: Dict[str, Dict] = field(default_factory=lambda: {
        "extracting": {"status": "pending", "progress": 0, "message": ""},
        "merging": {"status": "pending", "progress": 0, "message": ""},
        "generating": {"status": "pending", "progress": 0, "message": ""}
    })
    
    # 结果数据
    spec: Optional[PrototypeSpec] = None
    html_path: str = ""
    error: Optional[str] = None
    
    def update_stage(self, stage: str, status: str, progress: int = 0, message: str = ""):
        if stage in self.stages:
            self.stages[stage] = {
                "status": status,
                "progress": progress,
                "message": message
            }
    
    def to_dict(self) -> Dict:
        return {
            "current_stage": self.current_stage,
            "stages": self.stages,
            "spec": self.spec.to_dict() if self.spec else None,
            "html_path": self.html_path,
            "error": self.error
        }


class PrototypeOrchestrator:
    """
    原型工作流编排器
    
    工作流程：
    图片输入 → 布局提取（多次采样+合并）→ HTML生成 → 输出
    """
    
    def __init__(self,
                 sample_count: int = 3,
                 max_retries: int = 3,
                 model: str = "gpt-4o"):
        """
        初始化编排器
        
        Args:
            sample_count: 采样次数
            max_retries: 最大重试次数
            model: 使用的模型
        """
        self.layout_extractor = LayoutExtractor(
            model=model,
            sample_count=sample_count,
            max_retries=max_retries
        )
        self.html_generator = HTMLGenerator(model=model)
        self.state = WorkflowState()
        self.record_dir = Path(__file__).parent / "data" / "extraction-logs"
        self.record_dir.mkdir(exist_ok=True)
    
    def run(self, 
            image_path: str = None,
            image_base64: str = None,
            skip_generation: bool = False,
            on_state_change: Callable[[WorkflowState], None] = None) -> WorkflowState:
        """
        执行完整工作流
        
        Args:
            image_path: 图片路径
            image_base64: 图片base64编码
            skip_generation: 是否跳过HTML生成
            on_state_change: 状态变化回调（用于前端更新）
        
        Returns:
            WorkflowState
        """
        print("\n" + "=" * 60)
        print("🚀 原型提取工作流")
        print("=" * 60)
        
        # 阶段1：布局提取
        self.state.current_stage = "extracting"
        self.state.update_stage("extracting", "running", 0, "开始布局分析...")
        self._notify(on_state_change)
        
        extraction_result = self.layout_extractor.extract(
            image_path=image_path,
            image_base64=image_base64
        )
        
        if not extraction_result.success:
            self.state.error = extraction_result.error
            self.state.update_stage("extracting", "failed", 100, extraction_result.error)
            self._notify(on_state_change)
            return self.state
        
        self.state.update_stage("extracting", "completed", 100, 
                                f"提取完成，置信度: {extraction_result.confidence:.0%}")
        
        # 构建规格
        layout_spec = LayoutSpec.from_raw(extraction_result.data)
        layout_spec.confidence = extraction_result.confidence
        
        self.state.spec = PrototypeSpec(
            layout=layout_spec,
            source_image=image_path or "base64",
            extraction_time=datetime.now().isoformat()
        )
        
        # 保存记录
        self._save_record(extraction_result)
        
        # 阶段2：HTML生成
        if not skip_generation:
            self.state.current_stage = "generating"
            self.state.update_stage("generating", "running", 0, "生成HTML原型...")
            self._notify(on_state_change)
            
            gen_result = self.html_generator.generate(spec=self.state.spec)
            
            if gen_result.success:
                self.state.html_path = gen_result.output_path
                self.state.update_stage("generating", "completed", 100, "生成完成")
            else:
                self.state.update_stage("generating", "failed", 100, gen_result.error)
        
        self.state.current_stage = "done"
        self._notify(on_state_change)
        
        # 打印结果摘要
        self._print_summary()
        
        return self.state
    
    def extract_only(self, image_path: str = None, image_base64: str = None) -> ExtractionResult:
        """仅执行提取阶段"""
        return self.layout_extractor.extract(
            image_path=image_path,
            image_base64=image_base64
        )
    
    def generate_only(self, spec: PrototypeSpec = None, 
                      raw_analysis: Dict = None) -> GenerationResult:
        """仅执行生成阶段"""
        return self.html_generator.generate(spec=spec, raw_analysis=raw_analysis)
    
    def _notify(self, callback: Callable = None):
        """通知状态变化"""
        if callback:
            callback(self.state)
    
    def _save_record(self, result: ExtractionResult):
        """保存提取记录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        record_path = self.record_dir / f"extraction_{timestamp}.txt"
        
        with open(record_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("📊 布局分析结果\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"⏱️ 耗时: {result.elapsed_time:.1f}秒\n")
            f.write(f"📈 置信度: {result.confidence:.0%}\n\n")
            
            if result.merge_decisions:
                f.write("🔀 合并决策:\n")
                for decision in result.merge_decisions:
                    f.write(f"   - {decision.get('位置', '')}: {decision.get('决策', '')}\n")
                f.write("\n")
            
            f.write("-" * 60 + "\n")
            f.write("📋 结构化结果:\n")
            f.write("-" * 60 + "\n")
            f.write(json.dumps(result.data, ensure_ascii=False, indent=2))
        
        print(f"\n📝 记录已保存: {record_path.name}")
    
    def _print_summary(self):
        """打印结果摘要"""
        print("\n" + "=" * 60)
        print("📋 工作流完成摘要")
        print("=" * 60)
        
        if self.state.error:
            print(f"\n❌ 错误: {self.state.error}")
            return
        
        if self.state.spec and self.state.spec.layout:
            layout = self.state.spec.layout
            print(f"\n✅ 布局提取:")
            print(f"   - 设备类型: {layout.device.type if layout.device else 'N/A'}")
            print(f"   - 区域数量: {len(layout.regions)}")
            print(f"   - 置信度: {layout.confidence:.0%}")
        
        if self.state.html_path:
            print(f"\n✅ HTML生成:")
            print(f"   - 输出文件: {self.state.html_path}")
        
        print("\n" + "=" * 60)


# 快捷函数
def extract_prototype(image_path: str, sample_count: int = 3) -> PrototypeSpec:
    """快捷函数：从图片提取原型规格"""
    orchestrator = PrototypeOrchestrator(sample_count=sample_count)
    state = orchestrator.run(image_path=image_path, skip_generation=True)
    return state.spec


def generate_prototype(image_path: str, sample_count: int = 3) -> str:
    """快捷函数：从图片生成HTML原型，返回文件路径"""
    orchestrator = PrototypeOrchestrator(sample_count=sample_count)
    state = orchestrator.run(image_path=image_path)
    return state.html_path

