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
    version="1.1", # 版本号更新
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

        # ▼▼▼▼▼ 【核心优化】使用一个更稳定、更清晰的Prompt ▼▼▼▼▼
        prompt = f"""
扮演一位深刻且风趣的“汉语新解”大师。

你的任务是为中文词语“{keyword}”创作一个辛辣、一针见血的现代定义，并将其呈现为一张设计精美的SVG卡片。

请严格遵循以下步骤和要求：

**第一步：创作定义**
- **定义风格**：语言必须简洁、辛辣、讽刺，直击词语在当代社会中的本质。
- **定义格式**：必须是**一句完整的话**。

**第二步：生成SVG卡片**
- 在给出上面创作的定义后，请另起一行，生成一张SVG卡片。
- **SVG代码要求**：
    1.  **必须是完整且语法正确的SVG代码**，从 `<svg ...>` 开始，到 `</svg>` 结束。
    2.  **必须是结构良好 (well-formed) 的XML**，所有标签必须正确闭合，属性值必须用引号包裹。
    3.  **设计风格**：现代、简约、典雅，有设计感。
    4.  **字体**：请在SVG代码中使用通用的中文字体名，例如 `KaiTi`, `SimHei`, `sans-serif`。
    5.  **内容**：SVG卡片中必须包含“{keyword}”这个词和你的新定义。

请直接开始创作，不要有任何额外的对话或解释。
"""
        # ▲▲▲▲▲ 【优化结束】 ▲▲▲▲▲

        # 用新构建的指令替换掉用户原始内容
        e_context["context"].content = prompt
        
        # 【关键】让事件继续，以便后续的AI处理器能够接收并处理这个新指令
        e_context.action = EventAction.CONTINUE
        logger.debug(f"[ChineseNewDef] Context content has been rewritten. Passing to LLM.")


    def get_help_text(self, **kwargs):
        # 提供一个简洁的帮助说明
        help_text = "🎨 发送“汉语新解 词语”或“新解 词语”，为你生成一张关于这个词的SVG卡片。\n例如：`新解 内卷`"
        return help_text
