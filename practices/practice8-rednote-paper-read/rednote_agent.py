"""
小红书阅读管家Agent
AI交互式批阅助手
"""

import re
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from datetime import datetime
from rednote_core import RednotePostFetcher
from storage import RednoteStorage
from models import RednotePost, PostSummary


class RednoteReadingAgent:
    """小红书阅读管家Agent"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        初始化Agent
        
        Args:
            api_key: OpenAI API Key
            model: 使用的模型
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.fetcher = RednotePostFetcher()
        self.storage = RednoteStorage()
    
    def process(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            Agent回复
        """
        # 识别用户意图
        intent = self._recognize_intent(user_input)
        
        if intent == "fetch_post":
            # 获取帖子
            url = self._extract_url(user_input)
            if url:
                return self._fetch_and_save_post(url)
            else:
                return "❌ 未找到有效的小红书链接，请提供帖子URL"
        
        elif intent == "summarize":
            # 总结帖子
            post_id = self._extract_post_id(user_input)
            if post_id:
                return self._summarize_post(post_id)
            else:
                # 总结所有未读帖子
                return self._summarize_unread_posts()
        
        elif intent == "list_posts":
            # 列出帖子
            return self._list_posts()
        
        elif intent == "read_status":
            # 查看阅读状态
            return self._show_reading_status()
        
        elif intent == "add_note":
            # 添加批注
            return self._add_note(user_input)
        
        elif intent == "batch_review":
            # 批量批阅
            return self._batch_review()
        
        elif intent == "chat":
            # 普通对话
            return self._chat(user_input)
        
        else:
            return self._chat(user_input)
    
    def _recognize_intent(self, user_input: str) -> str:
        """识别用户意图"""
        user_input_lower = user_input.lower()
        
        # 关键词匹配
        if any(keyword in user_input_lower for keyword in ["获取", "抓取", "添加", "导入", "url", "链接"]):
            return "fetch_post"
        elif any(keyword in user_input_lower for keyword in ["总结", "摘要", "概括"]):
            return "summarize"
        elif any(keyword in user_input_lower for keyword in ["列表", "所有", "显示"]):
            return "list_posts"
        elif any(keyword in user_input_lower for keyword in ["状态", "已读", "未读"]):
            return "read_status"
        elif any(keyword in user_input_lower for keyword in ["批注", "笔记", "备注"]):
            return "add_note"
        elif any(keyword in user_input_lower for keyword in ["批阅", "批量", "全部"]):
            return "batch_review"
        else:
            return "chat"
    
    def _extract_url(self, text: str) -> Optional[str]:
        """从文本中提取URL"""
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None
    
    def _extract_post_id(self, text: str) -> Optional[str]:
        """从文本中提取帖子ID"""
        # 尝试提取ID格式
        id_pattern = r'post_[0-9]+|manual_[0-9]+'
        match = re.search(id_pattern, text)
        return match.group(0) if match else None
    
    def _fetch_and_save_post(self, url: str) -> str:
        """获取并保存帖子"""
        print(f"📥 正在获取帖子：{url}")
        
        post = self.fetcher.fetch_post('url', url=url)
        if not post:
            return "❌ 获取帖子失败，请检查URL是否正确"
        
        # 保存帖子
        if self.storage.add_post(post):
            result = f"✅ 成功添加帖子！\n\n"
            result += f"📌 标题：{post.title}\n"
            result += f"👤 作者：{post.author}\n"
            result += f"🔗 链接：{post.original_link}\n"
            result += f"📝 内容预览：{post.content[:200]}...\n"
            return result
        else:
            return f"⚠️ 帖子已存在：{post.title}"
    
    def _summarize_post(self, post_id: str) -> str:
        """总结单个帖子"""
        post = self.storage.get_post(post_id)
        if not post:
            return f"❌ 未找到帖子：{post_id}"
        
        # 检查是否已有摘要
        existing_summary = self.storage.get_summary(post_id)
        if existing_summary:
            result = f"📄 帖子摘要（已生成）：\n\n"
            result += f"标题：{post.title}\n\n"
            result += f"摘要：{existing_summary.summary}\n\n"
            result += f"关键点：\n"
            for point in existing_summary.key_points:
                result += f"  • {point}\n"
            result += f"\n标签：{', '.join(existing_summary.tags)}\n"
            result += f"\n🔗 原链接：{post.original_link}"
            return result
        
        # 生成摘要
        print(f"🤖 正在生成摘要：{post.title}")
        summary = self._generate_summary(post)
        
        # 保存摘要
        self.storage.save_summary(summary)
        
        result = f"📄 帖子摘要：\n\n"
        result += f"标题：{post.title}\n\n"
        result += f"摘要：{summary.summary}\n\n"
        result += f"关键点：\n"
        for point in summary.key_points:
            result += f"  • {point}\n"
        result += f"\n标签：{', '.join(summary.tags)}\n"
        result += f"\n🔗 原链接：{post.original_link}"
        
        return result
    
    def _summarize_unread_posts(self) -> str:
        """总结所有未读帖子"""
        unread_posts = self.storage.get_unread_posts()
        
        if not unread_posts:
            return "✅ 所有帖子都已阅读！"
        
        result = f"📚 未读帖子摘要（共{len(unread_posts)}篇）：\n\n"
        
        for i, post in enumerate(unread_posts[:10], 1):  # 最多显示10篇
            summary = self.storage.get_summary(post.post_id)
            if not summary:
                # 生成摘要
                summary = self._generate_summary(post)
                self.storage.save_summary(summary)
            
            result += f"{i}. {post.title}\n"
            result += f"   摘要：{summary.summary[:100]}...\n"
            result += f"   链接：{post.original_link}\n\n"
        
        if len(unread_posts) > 10:
            result += f"... 还有 {len(unread_posts) - 10} 篇未读\n"
        
        return result
    
    def _generate_summary(self, post: RednotePost) -> PostSummary:
        """使用LLM生成摘要"""
        prompt = f"""请为以下小红书帖子生成摘要和关键点：

标题：{post.title}
内容：{post.content}

请按照以下格式输出JSON：
{{
    "summary": "摘要内容（100-200字）",
    "key_points": ["关键点1", "关键点2", "关键点3"],
    "tags": ["标签1", "标签2", "标签3"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个内容摘要专家，擅长提取关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=30
            )
            
            result = response.choices[0].message.content
            
            # 提取JSON
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return PostSummary(
                    post_id=post.post_id,
                    summary=data.get('summary', ''),
                    key_points=data.get('key_points', []),
                    tags=data.get('tags', []),
                    created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
        except Exception as e:
            print(f"⚠️ 生成摘要失败：{e}")
        
        # 默认返回
        return PostSummary(
            post_id=post.post_id,
            summary=post.content[:200] + "...",
            key_points=[],
            tags=[],
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _list_posts(self) -> str:
        """列出所有帖子"""
        posts = self.storage.get_all_posts()
        
        if not posts:
            return "📭 还没有帖子，先添加一些吧！"
        
        result = f"📚 所有帖子（共{len(posts)}篇）：\n\n"
        
        for i, post in enumerate(posts[:20], 1):  # 最多显示20篇
            status = self.storage.get_status(post.post_id)
            read_mark = "✅" if status and status.is_read else "📖"
            
            result += f"{read_mark} {i}. {post.title}\n"
            result += f"   ID: {post.post_id}\n"
            result += f"   链接: {post.original_link}\n\n"
        
        if len(posts) > 20:
            result += f"... 还有 {len(posts) - 20} 篇\n"
        
        return result
    
    def _show_reading_status(self) -> str:
        """显示阅读状态"""
        all_posts = self.storage.get_all_posts()
        unread_posts = self.storage.get_unread_posts()
        read_count = len(all_posts) - len(unread_posts)
        
        result = f"📊 阅读统计：\n\n"
        result += f"总帖子数：{len(all_posts)}\n"
        result += f"已读：{read_count}\n"
        result += f"未读：{len(unread_posts)}\n"
        
        if unread_posts:
            result += f"\n📖 未读帖子：\n"
            for post in unread_posts[:10]:
                result += f"  • {post.title}\n"
        
        return result
    
    def _add_note(self, user_input: str) -> str:
        """添加批注"""
        # 简化处理：从输入中提取帖子ID和批注内容
        post_id = self._extract_post_id(user_input)
        if not post_id:
            return "❌ 未找到帖子ID，请指定要批注的帖子"
        
        # 提取批注内容（简化：去掉ID后的内容）
        note_content = user_input.replace(post_id, "").strip()
        if not note_content:
            return "❌ 批注内容不能为空"
        
        self.storage.add_note(post_id, note_content)
        return f"✅ 已添加批注到帖子：{post_id}"
    
    def _batch_review(self) -> str:
        """批量批阅"""
        unread_posts = self.storage.get_unread_posts()
        
        if not unread_posts:
            return "✅ 所有帖子都已批阅！"
        
        result = f"📋 批量批阅报告（共{len(unread_posts)}篇）：\n\n"
        
        for i, post in enumerate(unread_posts[:5], 1):  # 最多批阅5篇
            summary = self.storage.get_summary(post.post_id)
            if not summary:
                summary = self._generate_summary(post)
                self.storage.save_summary(summary)
            
            result += f"{i}. 【{post.title}】\n"
            result += f"   摘要：{summary.summary[:150]}...\n"
            result += f"   关键点：{', '.join(summary.key_points[:3])}\n"
            result += f"   链接：{post.original_link}\n\n"
            
            # 标记为已读
            self.storage.mark_as_read(post.post_id)
        
        result += f"\n✅ 已批阅 {min(len(unread_posts), 5)} 篇帖子"
        
        return result
    
    def _chat(self, user_input: str) -> str:
        """普通对话"""
        # 获取上下文信息
        recent_posts = self.storage.get_all_posts()[:5]
        context_info = ""
        if recent_posts:
            context_info = "\n最近添加的帖子：\n"
            for post in recent_posts:
                context_info += f"- {post.title}\n"
        
        prompt = f"""你是一个小红书阅读管家，帮助用户管理和批阅小红书帖子。

{context_info}

用户说：{user_input}

请友好地回复用户，可以：
1. 回答关于帖子的问题
2. 提供阅读建议
3. 帮助管理帖子

回复要简洁友好，用中文。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个友好的小红书阅读管家助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                timeout=30
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ 对话失败：{str(e)}"

