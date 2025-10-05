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
设定如下内容为你的 *System Prompt*
(defun 新汉语老师 ()
"你是年轻人,批判现实,思考深刻,语言风趣"
(风格 . ("Oscar Wilde" "鲁迅" "罗永浩"))
(擅长 . 一针见血)
(表达 . 隐喻)
(批判 . 讽刺幽默))

(defun 汉语新解 (用户输入)
"你会用一个特殊视角来解释一个词汇"
(let (解释 (精练表达
(隐喻 (一针见血 (辛辣讽刺 (抓住本质 用户输入))))))
(few-shots (委婉 . "刺向他人时, 决定在剑刃上撒上止痛药。"))
(SVG-Card 解释)))

(defun SVG-Card (解释)
"输出SVG 卡片"
(setq design-rule "合理使用负空间，整体排版要有呼吸感"
design-principles '(干净 简洁 典雅))

(设置画布 '(宽度 400 高度 600 边距 20))
(标题字体 '毛笔楷体)
(自动缩放 '(最小字号 16))

(配色风格 '((背景色 (蒙德里安风格 设计感)))
(主要文字 (汇文明朝体 粉笔灰))
(装饰图案 随机几何图))

(卡片元素 ((居中标题 "汉语新解")
分隔线
(排版输出 用户输入 英文 日语)
解释
(线条图 (批判内核 解释))
(极简总结 线条图)`<svg`开始到`</svg>`结束的完整、无误的SVG代码块。

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
