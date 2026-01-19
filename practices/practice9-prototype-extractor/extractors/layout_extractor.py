"""
布局提取器

从图片中提取布局结构信息。
基于视觉模型（GPT-4o）进行分析。
"""

from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import os
import sys
import base64
import json
import re

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base import BaseExtractor
from specs import LayoutSpec
from prompts import PromptLoader

load_dotenv()


class LayoutExtractor(BaseExtractor):
    """
    布局提取器
    
    从图片中提取：
    - 整体布局结构
    - 区域划分
    - 组件识别
    - CSS实现建议
    """
    
    name = "布局分析"
    
    def __init__(self, 
                 model: str = "gpt-4o",
                 temperature: float = 0.3,
                 sample_count: int = 3,
                 max_retries: int = 3):
        super().__init__(sample_count=sample_count, max_retries=max_retries)
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY"),
            request_timeout=180
        )
        self.prompt_loader = PromptLoader()
    
    def _encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _extract_once(self, image_path: str = None, image_base64: str = None) -> Dict[str, Any]:
        """单次提取"""
        # 获取图片内容
        if image_base64:
            image_content = image_base64
        elif image_path:
            try:
                image_content = self._encode_image(image_path)
            except Exception as e:
                return {"success": False, "error": f"图片读取失败: {e}"}
        else:
            return {"success": False, "error": "未提供图片"}
        
        # 构建消息
        system_prompt = self.prompt_loader.load("布局分析")
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请分析这张原型图片的整体布局结构。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_content}"}}
                ]
            }
        ]
        
        # 调用视觉模型
        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # 解析JSON
            parsed = self._parse_json(content)
            if parsed:
                return {"success": True, "data": parsed}
            else:
                return {"success": False, "error": "JSON解析失败"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """解析JSON响应"""
        json_parser = JsonOutputParser()
        
        try:
            return json_parser.parse(content)
        except:
            # 手动提取和修复
            try:
                json_text = content
                if "```json" in json_text:
                    json_text = json_text.split("```json")[1].split("```")[0].strip()
                elif "```" in json_text:
                    json_text = json_text.split("```")[1].split("```")[0].strip()
                
                # 修复常见错误
                json_text = re.sub(r',\s*]', ']', json_text)
                json_text = re.sub(r',\s*}', '}', json_text)
                json_text = re.sub(r'//.*?\n', '\n', json_text)
                
                return json.loads(json_text)
            except:
                return None
    
    def _merge_samples(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并多次采样结果"""
        # 加载合并提示词
        merge_prompt = self.prompt_loader.load("结果合并")
        
        # 构建采样结果文本
        samples_text = ""
        for i, sample in enumerate(samples, 1):
            samples_text += f"\n\n=== 第 {i} 次采样结果 ===\n"
            samples_text += json.dumps(sample, ensure_ascii=False, indent=2)
        
        messages = [
            {"role": "system", "content": merge_prompt},
            {"role": "user", "content": f"请合并以下 {len(samples)} 次布局分析结果：{samples_text}"}
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            parsed = self._parse_json(content)
            if not parsed:
                return {"success": False, "error": "合并结果解析失败"}
            
            # 提取 merged_result
            if "merged_result" in parsed and parsed["merged_result"]:
                merged = parsed["merged_result"]
            elif "overall_layout" in parsed or "main_regions" in parsed:
                merged = parsed
            else:
                merged = parsed
            
            return {
                "success": True,
                "data": merged,
                "merge_decisions": parsed.get("merge_decisions", []),
                "confidence": parsed.get("confidence", {}).get("overall", 0.0) if isinstance(parsed.get("confidence"), dict) else 0.0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_to_spec(self, image_path: str = None, image_base64: str = None) -> LayoutSpec:
        """
        提取并转换为 LayoutSpec
        
        Returns:
            LayoutSpec 数据模型
        """
        result = self.extract(image_path=image_path, image_base64=image_base64)
        
        if result.success:
            spec = LayoutSpec.from_raw(result.data)
            spec.confidence = result.confidence
            return spec
        else:
            return LayoutSpec()

