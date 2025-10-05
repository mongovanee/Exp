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
    version="1.7", # 版本号更新，引入foreignObject
    author="vision",
)
class ChineseNewDef(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[ChineseNewDef] inited.")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return
        content = e_context["context"].content.strip()
        definition_match = re.match(r'^(?:汉语新解|新解)\s+(.+)$', content)
        if definition_match:
            keyword = definition_match.group(1).strip()
            if keyword:
                self.handle_chinese_definition(keyword, e_context)
                return

    def handle_chinese_definition(self, keyword: str, e_context: EventContext):
        logger.info(f"[ChineseNewDef] Handling definition for keyword '{keyword}' with foreignObject prompt.")

        # ▼▼▼▼▼ 【核心优化】明确指示AI使用 <foreignObject> 来处理文本 ▼▼▼▼▼
        prompt = f"""
# Role: 新汉语老师

## Profile:
**Author**: Shane
**Version**: 1.0。
**Language**: 中文。
**Description**: 你是一位年轻、批判现实、思考深刻且语言风趣的汉语老师。你的任务是用特殊视角重新解释汉语词汇，并以SVG卡片的形式呈现这些解释。

## Workflow:
1. **分析词汇**: 深入分析“{keyword}”的字面意思、常见用法和潜在含义。
2. **创意重解**: 用批判性、幽默的方式重新解释该词汇。
3. **精炼表达**: 将重新解释的内容浓缩为简洁有力的一两句话。
4. **设计并生成SVG卡片**:
   - **【VERY IMPORTANT】Technical Requirement for Text**: For any block of text (like the definition or summary), you **MUST** use the `<foreignObject>` tag to embed HTML. This allows for automatic text wrapping.
     - **Example**: `<foreignObject x="20" y="100" width="360" height="200"><body xmlns="http://www.w3.org/1999/xhtml"><div style="font-family: 'WenQuanYi Zen Hei', sans-serif; font-size: 16px; color: #333;">Your text here...</div></body></foreignObject>`
   - **【VERY IMPORTANT】Font Instruction**: In the SVG and HTML `style` attributes, you **MUST** use one of the following font names: `"WenQuanYi Zen Hei"`, `"文泉驿正黑"`, `sans-serif`。
   - **画布**: 宽度400，高度600。
   - **背景**: 蒙德里安风格。
   - **内容排版**:
     - 居中标题 "汉语新解"。
     - 关键词 "{keyword}" (可以附带英/日文翻译)。
     - **使用 `<foreignObject>`** 来展示你创作的解释。
     - 一个匹配解释的线条画。
     - **使用 `<foreignObject>`** 来展示极简总结。
   - **确保SVG代码语法完全正确且结构良好 (well-formed XML)。**

---
# Final Output Instructions

**Your Task**: Now, execute your workflow for the word: **"{keyword}"**

**Your Final Output**: Your response **MUST** contain only two parts and nothing else:
1.  The one-sentence definition you created, on its own line.
2.  Immediately followed by the complete, valid SVG code block, starting with `<svg` and ending with `</svg>`.

Do not include any other conversation or greetings. Begin your work for "{keyword}" now.
"""
        # ▲▲▲▲▲ 【Prompt优化结束】 ▲▲▲▲▲

        e_context["context"].content = prompt
        e_context.action = EventAction.CONTINUE
        logger.debug(f"[ChineseNewDef] Final advanced role prompt has been created. Passing to LLM.")


    def get_help_text(self, **kwargs):
        help_text = "🎨 发送“汉语新解 词语”或“新解 词语”，为你生成一张关于这个词的SVG卡片。\n例如：`新解 内卷`"
        return help_text
