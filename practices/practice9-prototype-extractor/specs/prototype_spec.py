"""
原型规格数据模型

这是所有提取器输出和生成器输入的统一数据结构。
设计原则：
1. 各维度独立，可单独提取和使用
2. 支持序列化/反序列化（JSON）
3. 包含置信度信息
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import json


@dataclass
class ComponentSpec:
    """组件规格"""
    name: str                           # 组件名称（中文）
    type: str                           # 组件类型
    internal: Dict[str, Any] = None     # 组件内部CSS实现
    external: Dict[str, Any] = None     # 组件在父容器中的表现
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RegionSpec:
    """区域规格"""
    name: str                           # 区域名称（中文）
    level: int = 1                      # 层级深度
    parent: Optional[str] = None        # 父容器名称
    layout_structure: str = ""          # 布局结构描述
    sizing_behavior: str = ""           # 尺寸行为
    arrangement: str = ""               # 排列方式
    spacing: str = ""                   # 间距设置
    positioning: str = ""               # 定位方式
    components: List[ComponentSpec] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d["components"] = [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.components]
        return d


@dataclass
class DeviceSpec:
    """设备规格"""
    type: str = "Mobile"                # Mobile / Tablet / Desktop
    screen_size: str = "375x812"        # 屏幕尺寸
    viewport_split: str = "单一通栏"    # 视口切分方式
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LayoutSpec:
    """布局规格 - 布局提取器的输出"""
    device: DeviceSpec = None
    root_container: Dict[str, Any] = None       # 根容器配置
    sizing_strategy: Dict[str, Any] = None      # 尺寸策略
    regions: List[RegionSpec] = field(default_factory=list)
    summary: Dict[str, str] = None              # 总结
    confidence: float = 0.0                     # 置信度
    
    def to_dict(self) -> dict:
        return {
            "device": self.device.to_dict() if self.device else None,
            "root_container": self.root_container,
            "sizing_strategy": self.sizing_strategy,
            "regions": [r.to_dict() if hasattr(r, 'to_dict') else r for r in self.regions],
            "summary": self.summary,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_raw(cls, raw: dict) -> "LayoutSpec":
        """从原始JSON结构创建LayoutSpec"""
        if not raw:
            return cls()
        
        # 解析device
        overall = raw.get("overall_layout", {})
        device = DeviceSpec(
            type=overall.get("device_type", "Mobile"),
            screen_size=overall.get("screen_size", ""),
            viewport_split=overall.get("viewport_split", "")
        )
        
        # 解析regions
        regions = []
        for r in raw.get("main_regions", []):
            components = []
            for c in r.get("components", []):
                components.append(ComponentSpec(
                    name=c.get("name", ""),
                    type=c.get("type", ""),
                    internal=c.get("internal"),
                    external=c.get("external")
                ))
            
            regions.append(RegionSpec(
                name=r.get("name", ""),
                level=r.get("level", 1),
                parent=r.get("parent"),
                layout_structure=r.get("layout_structure", ""),
                sizing_behavior=r.get("sizing_behavior", ""),
                arrangement=r.get("arrangement", ""),
                spacing=r.get("spacing", ""),
                positioning=r.get("positioning", ""),
                components=components
            ))
        
        return cls(
            device=device,
            root_container=overall.get("root_container"),
            sizing_strategy=overall.get("sizing_strategy"),
            regions=regions,
            summary=raw.get("summary")
        )


@dataclass
class ColorSpec:
    """色彩规格 - 色彩提取器的输出（预留）"""
    primary: str = ""                   # 主色
    secondary: str = ""                 # 辅色
    background: str = ""                # 背景色
    text: str = ""                      # 文字色
    accent: str = ""                    # 强调色
    palette: List[str] = field(default_factory=list)  # 调色板
    confidence: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PrototypeSpec:
    """
    原型规格 - 统一的中间表示
    
    包含从图片提取的所有维度信息，作为生成器的输入。
    各维度可独立存在，按需填充。
    """
    # 核心维度
    layout: Optional[LayoutSpec] = None
    colors: Optional[ColorSpec] = None
    # 未来扩展
    # typography: Optional[TypographySpec] = None
    # interactions: Optional[InteractionSpec] = None
    
    # 元信息
    source_image: str = ""              # 源图片路径
    extraction_time: str = ""           # 提取时间
    
    def to_dict(self) -> dict:
        return {
            "layout": self.layout.to_dict() if self.layout else None,
            "colors": self.colors.to_dict() if self.colors else None,
            "source_image": self.source_image,
            "extraction_time": self.extraction_time
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    def has_layout(self) -> bool:
        return self.layout is not None
    
    def has_colors(self) -> bool:
        return self.colors is not None

