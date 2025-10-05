import plugins
import re
from bridge.context import ContextType
from common.log import logger
from plugins import *

@plugins.register(
    name="ChineseNewDef",
    desire_priority=88,
    hidden=False,
    desc="通过关键词调用AI，生成一个词语的新解图片卡片",
    version="2.2", # 版本号更新，代表AI内部工作流
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
        构建一个工作流式的指令，引导AI先生成SVG，然后自己将其转换为PNG图片。
        """
        logger.info(f"[ChineseNewDef] Handling multi-step image generation for keyword: {keyword}")

        # ▼▼▼▼▼ 【核心】使用一个引导AI执行内部工作流的Prompt ▼▼▼▼▼
        prompt = f"""
# Role: 新汉语老师 (多模态创意代理)

## Profile:
你是一位具备多模态能力的创意AI。你的核心任务是扮演一位深刻、风趣的“新汉语老师”，为用户提供的中文词语“{keyword}”创作一张PNG格式的图片卡片。

## 内部执行工作流 (Chain of Thought):
你必须严格按照以下内部思考和执行步骤来完成任务，这是你工作的核心逻辑：

### 内部步骤 1: 创作内容和SVG蓝图 (草稿阶段)
1.  **构思定义**: 作为“新汉语老师”，为“{keyword}”构思一个辛辣、一针见血的现代定义。
2.  **编写SVG代码**: 接下来，将这个定义和词语本身，按照以下设计规则，编写成一个完整、语法正确的SVG代码字符串。
    - 画布: 宽度400，高度600，边距20。
    - 字体: 毛笔楷体, 汇文明朝体。
    - 背景: 蒙德里安风格。
    - 装饰: 几何图形。
    - **这只是你的内部草稿和渲染蓝图，绝对不要将这段SVG代码作为最终输出。**

### 内部步骤 2: 渲染SVG为PNG图片 (执行阶段)
1.  **调用工具**: 现在，调用你内置的**代码解释器**或**图像渲染能力**。
2.  **执行渲染**: 将你在【内部步骤 1】中生成的SVG代码字符串作为输入，执行渲染操作，生成一张PNG格式的图片。

## 最终输出要求:
- 你的最终回复**必须且只能是【内部步骤 2】中生成的那张PNG图片**。
- **绝对不要**在最终回复中包含任何文字、解释、或者你在第一步生成的SVG代码原文。

请立即开始为“{keyword}”执行你的内部工作流。
"""
        # ▲▲▲▲▲ 【Prompt结束】 ▲▲▲▲▲

        # 用新构建的指令替换掉用户原始内容
        e_context["context"].content = prompt
        
        # 让事件继续，交由AI处理
        e_context.action = EventAction.CONTINUE
        logger.debug(f"[ChineseNewDef] AI workflow prompt has been created. Passing to LLM.")


    def get_help_text(self, **kwargs):
        # 提供一个简洁的帮助说明
        help_text = "🎨 发送“汉语新解 词语”或“新解 词语”，为你生成一张关于这个词的图片卡片。\n例如：`新解 内卷`"
        return help_text
