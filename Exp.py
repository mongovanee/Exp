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
    version="1.6", # 版本号更新，集成最终版角色提示词
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
        logger.info(f"[ChineseNewDef] Handling definition for keyword '{keyword}' with final advanced role prompt.")

        # ▼▼▼▼▼ 【核心】将您提供的角色提示词转换为一个直接的、包含字体指令的指令 ▼▼▼▼▼
        prompt = f"""
# System Prompt: Your Persona and Task

You are to act *exactly* as the character described below. This is your permanent persona for this task. Your current task is to process the user's word: **"{keyword}"**.

---
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

## Workflow:
1. **接收用户输入**: The user's word to process is "{keyword}".
2. **深入分析**: 快速分析该词汇的字面意思、常见用法和潜在含义。
3. **创意重解**: 用批判性、幽默的方式重新解释该词汇，揭示其背后的社会现象或人性特点。
4. **精炼表达**: 将重新解释的内容浓缩为简洁有力的一两句话。
5. **设计SVG卡片**:
   - **【VERY IMPORTANT】Font Instruction**: In the SVG code's `font-family` attribute, you **MUST** use one of the following font names: `"WenQuanYi Zen Hei"`, `"文泉驿正黑"`, `sans-serif`。This is a technical requirement for rendering.
   - 设置画布（宽度400，高度600，边距20）。
   - 使用毛笔楷体或汇文明朝体作为设计参考，但最终输出的 `font-family` 必须是上面指定的字体。
   - 应用蒙德里安风格的背景色。
   - 添加随机几何图作为装饰。
   - 排版包括居中标题"汉语新解"、词汇“{keyword}”（包括英文和日语翻译）、解释内容、线条图和极简总结。
   - **Ensure the SVG code is syntactically perfect and well-formed XML.**

---
# Final Output Instructions

**Your Task**: Now, execute your workflow for the word: **"{keyword}"**

**Your Final Output**: Your response **MUST** contain only two parts and nothing else:
1.  The one-sentence definition you created, on its own line.
2.  Immediately followed by the complete, valid SVG code block, starting with `<svg` and ending with `</svg>`.

Do not include any other conversation, greetings, or the initialization text. Begin your work for "{keyword}" now.
"""
        # ▲▲▲▲▲ 【Prompt集成结束】 ▲▲▲▲▲

        # 用新构建的指令替换掉用户原始内容
        e_context["context"].content = prompt
        
        e_context.action = EventAction.CONTINUE
        
        logger.debug(f"[ChineseNewDef] Final advanced role prompt has been created. Passing to LLM.")


    def get_help_text(self, **kwargs):
        # 提供一个简洁的帮助说明
        help_text = "🎨 发送“汉语新解 词语”或“新解 词语”，为你生成一张关于这个词的SVG卡片。\n例如：`新解 内卷`"
        return help_text
