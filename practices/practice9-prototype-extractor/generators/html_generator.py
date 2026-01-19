"""
HTML生成器

根据 PrototypeSpec 生成 HTML 原型。
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
import re
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from specs import PrototypeSpec, LayoutSpec
from prompts import PromptLoader

load_dotenv()


@dataclass
class GenerationResult:
    """生成结果"""
    success: bool
    html_code: str = ""
    output_path: str = ""
    error: Optional[str] = None


class HTMLGenerator:
    """
    HTML生成器
    
    输入：PrototypeSpec（或其中的 LayoutSpec）
    输出：HTML 文件
    """
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.7):
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=8000,
            request_timeout=180
        )
        self.prompt_loader = PromptLoader()
        self.output_dir = Path(__file__).parent.parent / "data" / "prototypes"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, spec: PrototypeSpec = None, 
                 layout: LayoutSpec = None,
                 raw_analysis: Dict = None) -> GenerationResult:
        """
        生成HTML原型
        
        Args:
            spec: 完整的原型规格
            layout: 仅布局规格
            raw_analysis: 原始分析结果字典（兼容旧接口）
        
        Returns:
            GenerationResult
        """
        # 构建布局描述
        if spec and spec.has_layout():
            layout_description = json.dumps(spec.layout.to_dict(), ensure_ascii=False, indent=2)
        elif layout:
            layout_description = json.dumps(layout.to_dict(), ensure_ascii=False, indent=2)
        elif raw_analysis:
            layout_description = json.dumps(raw_analysis, ensure_ascii=False, indent=2)
        else:
            return GenerationResult(success=False, error="未提供布局信息")
        
        # 加载提示词
        try:
            system_prompt = self.prompt_loader.load("原型生成")
        except KeyError:
            system_prompt = self._get_default_prompt()
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请根据以下布局分析结果生成HTML原型：\n\n{layout_description}"}
        ]
        
        try:
            print("🎨 生成HTML原型...")
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # 提取HTML代码
            html_code = self._extract_html(content)
            
            # 保存文件
            output_path = self._save_html(html_code)
            
            print(f"   ✓ HTML已保存到：{output_path}")
            
            return GenerationResult(
                success=True,
                html_code=html_code,
                output_path=str(output_path)
            )
            
        except Exception as e:
            return GenerationResult(success=False, error=str(e))
    
    def _extract_html(self, content: str) -> str:
        """从响应中提取HTML代码"""
        patterns = [
            r'```html\s*([\s\S]*?)\s*```',
            r'```\s*(<!DOCTYPE[\s\S]*?)\s*```',
            r'```\s*(<html[\s\S]*?)\s*```',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
            return content.strip()
        
        return content
    
    def _save_html(self, html_code: str) -> Path:
        """保存HTML文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prototype_{timestamp}.html"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_code)
        
        return output_path
    
    def _get_default_prompt(self) -> str:
        """获取默认提示词"""
        return """你是一个专业的前端开发专家。你的任务是根据布局分析结果生成一个完整的HTML原型页面。

## 技术要求

1. **Tailwind CSS**：使用Tailwind CSS进行样式设计
   - 通过CDN引入：`<script src="https://cdn.tailwindcss.com"></script>`

2. **shadcn/ui风格**：模仿shadcn/ui的设计风格
   - 简洁现代的设计
   - 适当的圆角（rounded-lg, rounded-md）
   - 合适的阴影效果（shadow-sm, shadow-md）
   - 中性色调为主

3. **Lucide Icons**：使用Lucide图标
   - 通过CDN引入：`<script src="https://unpkg.com/lucide@latest"></script>`
   - 使用`<i data-lucide="icon-name"></i>`方式引用图标

## 输出要求

1. 生成完整的HTML文件，包含<!DOCTYPE html>声明
2. 所有样式使用Tailwind CSS实用类
3. 根据布局分析结果还原结构和样式
4. 使用语义化的HTML标签
5. 确保响应式设计

请直接输出HTML代码，不要有其他说明文字。"""

