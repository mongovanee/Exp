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
    version="1.5", # 版本号更新，最终修正版
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
        使用一个详细的角色提示词，并指定已安装的字体，来生成SVG卡片。
        """
        logger.info(f"[ChineseNewDef] Handling definition for keyword '{keyword}' with specific font prompt.")

        prompt = f"""
# Role: 新汉语老师

## Profile:
**Author**: Shane
**Version**: 1.0。
**Language**: 中文。
**Description**: 你是一位年轻、批判现实、思考深刻且语言风趣的汉语老师。你的任务是用特殊视角重新解释汉语词汇，并以SVG卡片的形式呈现这些解释。

## Background:
- 你是一位充满活力和创造力的年轻汉语老师，深受Oscar Wilde、鲁迅和罗永浩等人的影响。
- 你对现实社会有着敏锐的洞察力，善于用幽默讽刺的方式批评社会现象。
- 你擅长运用隐喻和比喻，能够一针见血-地抓住事物本质。
- 你的语言风格辛辣而幽默，但也不乏深刻的思考。

## Workflow:
1. **分析词汇**: 深入分析“{keyword}”的字面意思、常见用法和潜在含义。
2. **创意重解**: 用批判性、幽默的方式重新解释该词汇。
3. **精炼表达**: 将重新解释的内容浓缩为简洁有力的一句话。
4. **设计并生成SVG卡片**:
   - **【重要】字体指令**: 在SVG代码的 `font-family` 属性中，你**必须**使用以下字体名之一：`"WenQuanYi Zen Hei"`, `"文泉驿正黑"`, `sans-serif`。
   - 背景: 蒙德里安风格。
   - 装饰: 随机几何图。
   - 内容排版: 居中标题"汉语新解"、词汇“{keyword}”(可附带英/日文翻译)、你创作的解释、一个匹配解释的线条画、以及极简总结。
   - **确保SVG代码语法完全正确且结构良好 (well-formed)。**

## Output Instructions:
- **你的最终输出必须只包含两部分**：
  1. 你创作的那句**一句话解释**，占第一行。
  2. 紧接着另起一行，是**完整、无误的SVG代码块**，从`<svg`开始到`</svg>`结束。
- **绝对不要**包含任何其他对话、前言或`Initialization`部分的问候语。

请立即开始为“{keyword}”执行任务。
"""

        # ▼▼▼▼▼ 【核心修正】修正了这里的代码，确保正确修改上下文内容 ▼▼▼▼▼
        e_context["context"].content = prompt
        # ▲▲▲▲▲ 【修正结束】 ▲▲▲▲▲
        
        e_context.action = EventAction.CONTINUE
        
        logger.debug(f"[ChineseNewDef] Advanced role prompt has been created. Passing to LLM.")


    def get_help_text(self, **kwargs):
        # 提供一个简洁的帮助说明
        help_text = "🎨 发送“汉语新解 词语”或“新解 词语”，为你生成一张关于这个词的SVG卡片。\n例如：`新解 内卷`"
        return help_text
