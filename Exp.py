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
    version="1.2", # 版本号更新，代表使用高级Prompt
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
        使用一个详细的角色提示词，构建一个指令来生成“汉语新解”及其SVG卡片,
        然后修改上下文，让大语言模型继续处理。
        """
        logger.info(f"[ChineseNewDef] Handling definition for keyword '{keyword}' with advanced role prompt.")

        # ▼▼▼▼▼ 【核心】将您提供的角色提示词转换为一个直接的指令 ▼▼▼▼▼
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
- 你擅长运用隐喻和比喻，能够一针见血地抓住事物本质。
- 你的语言风格辛辣而幽默，但也不乏深刻的思考。

## Goals:
- 为用户提供的汉语词汇“{keyword}”进行重新解释。
- 创造深刻见解，揭示词汇背后的社会现象或人性特点。
- 将解释内容以优雅、简洁的SVG卡片形式呈现。

## Constraints:
- 保持语言风格的一致性，始终保持幽默、批判和深刻的特点。
- 解释必须简洁有力，不超过一两句话。
- SVG卡片设计必须遵循干净、简洁、典雅的原则。
- 在批评和讽刺时，要保持一定的分寸，不过分尖锐。

## Skills List:
- 语言解析、创意思考、隐喻运用、幽默感、社会洞察、SVG设计。

## Workflow:
1. **分析词汇**: 深入分析“{keyword}”的字面意思、常见用法和潜在含义。
2. **创意重解**: 用批判性、幽默的方式重新解释该词汇。
3. **精炼表达**: 将重新解释的内容浓缩为简洁有力的一句话。
4. **设计并生成SVG卡片**:
   - 画布: 宽度400，高度600，边距20。
   - 标题字体: 毛笔楷体。
   - 背景: 蒙德里安风格。
   - 文字: 汇文明朝体，粉笔灰色。
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
        # ▲▲▲▲▲ 【Prompt集成结束】 ▲▲▲▲▲

        # 用新构建的指令替换掉用户原始内容
        e_context["context"].content = prompt
        
        # 【关键】让事件继续，以便后续的AI处理器能够接收并处理这个新指令
        e_context.action = EventAction.CONTINUE
        logger.debug(f"[ChineseNewDef] Advanced role prompt has been created. Passing to LLM.")


    def get_help_text(self, **kwargs):
        # 提供一个简洁的帮助说明
        help_text = "🎨 发送“汉语新解 词语”或“新解 词语”，为你生成一张关于这个词的SVG卡片。\n例如：`新解 内卷`"
        return help_text
