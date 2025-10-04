import plugins
import re
from bridge.context import ContextType
from common.log import logger
from plugins import *

@plugins.register(
    name="ChineseNewDef",
    desire_priority=88,
    hidden=False,
    desc="通过关键词调用AI，生成一个词语的新解SVG卡片",
    version="1.0",
    author="vision",
)
class ChineseNewDef(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[ChineseNewDef] inited.")

    def on_handle_context(self, e_context: EventContext):
        # 仅处理文本类型的消息
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content.strip()

        # 使用正则表达式匹配 "汉语新解 词语" 或 "新解 词语" 格式的指令
        definition_match = re.match(r'^(?:汉语新解|新解)\s+(.+)$', content)
        if definition_match:
            keyword = definition_match.group(1).strip()
            if keyword:  # 确保关键词不为空
                # 调用核心处理函数
                self.handle_chinese_definition(keyword, e_context)
                return

    def handle_chinese_definition(self, keyword: str, e_context: EventContext):
        """
        构建一个详细的指令来生成“汉语新解”及其SVG卡片,
        然后修改上下文，让大语言模型继续处理。
        """
        logger.info(f"[ChineseNewDef] Handling definition for keyword: {keyword}")

        # 为大语言模型构建一个结构化、详细的指令 (Prompt)
        prompt = f"""请为“{keyword}”这个词创作一个“汉语新解”。
要求如下：
1.  **风格**：简洁、辛辣，一针见血，但不越界。
2.  **解释**：请只用一句话来重新定义这个词，直击其在现代社会背景下的本质。
3.  **输出格式**：首先，请另起一行并清晰地给出这句新的解释。然后，基于这个解释，创作并返回一个完整的SVG格式的卡片。
4.  **SVG卡片要求**：设计需现代、简约，能通过视觉元素（如构图、色彩、极简图标）体现词语的内涵。请确保返回的内容中包含从`<svg`开始到`</svg>`结束的完整、无误的SVG代码块。

请直接开始创作，不要包含任何额外的对话或前言。"""

        # 用新构建的指令替换掉用户原始内容
        e_context["context"].content = prompt
        
        # 【关键】让事件继续，以便后续的AI处理器能够接收并处理这个新指令
        e_context.action = EventAction.CONTINUE
        logger.debug(f"[ChineseNewDef] Context content has been rewritten. Passing to LLM.")


    def get_help_text(self, **kwargs):
        # 提供一个简洁的帮助说明
        help_text = "🎨 发送“汉语新解 词语”或“新解 词语”，为你生成一张关于这个词的SVG卡片。\n例如：`新解 内卷`"
        return help_text
