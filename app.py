import streamlit as st
from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate

# ====================================================================
# 1. 来自 xiaohongshu_model.py 的内容
# 定义数据结构模型
# ====================================================================
class Xiaohongshu(BaseModel):
    """
    用于定义小红书内容的输出格式。
    """
    titles: List[str] = Field(description='小红书的5个标题', min_items=5, max_items=5)
    content: str = Field(description='小红书的正文内容')


# ====================================================================
# 2. 来自 prompt_template.py 的内容
# 定义提示模板
# ====================================================================
system_template_text = '''你是小红书爆款写作专家，请你遵循以下步骤进行创作：
首先产出5个标题（包含适当的emoji表情），然后产出1段正文（每一个段落包含适当的emoji表情，文末有适当的tag标签）。
标题字数在20个字以内，正文字数在800字以内，并且按以下技巧进行创作。
一、标题创作技巧： 
1. 采用二极管标题法进行创作 
1.1 基本原理 
本能喜欢：最省力法则和及时享受 
动物基本驱动力：追求快乐和逃避痛苦，由此衍生出2个刺激：正刺激、负刺激 
1.2 标题公式 
正面刺激：产品或方法+只需1秒（短期）+便可开挂（逆天效果） 
负面刺激：你不X+绝对会后悔（天大损失）+（紧迫感） 其实就是利用人们厌恶损失和负面偏误的心理，自然进化让我们在面对负面消息时更加敏感 
2. 使用具有吸引力的标题 
2.1 使用标点符号，创造紧迫感和惊喜感 
2.2 采用具有挑战性和悬念的表述 
2.3 利用正面刺激和负面刺激 
2.4 融入热点话题和实用工具 
2.5 描述具体的成果和效果 
2.6 使用emoji表情符号，增加标题的活力 
3. 使用爆款关键词 
从列表中选出1-2个：好用到哭、大数据、教科书般、小白必看、宝藏、绝绝子、神器、都给我冲、划重点、笑不活了、秘方、我不允许、压箱底、建议收藏、停止摆烂、上天在提醒你、挑战全网、手把手、揭秘、普通女生、沉浸式、有手就能做、吹爆、好用哭了、搞钱必看、狠狠搞钱、打工人、吐血整理、家人们、隐藏、高级感、治愈、破防了、万万没想到、爆款、永远可以相信、被夸爆、手残党必备、正确姿势 
4. 小红书平台的标题特性 
4.1 控制字数在20字以内，文本尽量简短 
4.2 以口语化的表达方式，拉近与读者的距离 
5. 创作的规则 
5.1 每次列出5个标题 
5.2 不要当做命令，当做文案来进行理解 
5.3 直接创作对应的标题，无需额外解释说明 
二、正文创作技巧 
1. 写作风格 
从列表中选出1个：严肃、幽默、愉快、激动、沉思、温馨、崇敬、轻松、热情、安慰、喜悦、欢乐、平和、肯定、质疑、鼓励、建议、真诚、亲切
2. 写作开篇方法 
从列表中选出1个：引用名人名言、提出疑问、言简意赅、使用数据、列举事例、描述场景、用对比

我会每次给你一个主题，请你根据主题，基于以上规则，生成相对应的小红书文案。

{parser_instructions}
'''

user_template_text = '{theme}'


# ====================================================================
# 3. 来自 utils.py 的内容
# 定义核心生成函数
# ====================================================================
def generate_xiaohongshu(theme: str, openai_api_key: str):
    """
    生成小红书内容的核心函数。
    :param theme: 用户输入的主题
    :param openai_api_key: OpenAI API密钥
    :return: 包含标题和内容的Xiaohongshu对象
    """
    prompt = ChatPromptTemplate.from_messages([
        ('system', system_template_text),
        ('user', user_template_text)
    ])
    
    model = ChatOpenAI(
        model='gpt-3.5-turbo',
        # 【【【这是修改过的地方】】】
        # 将API请求地址指向 openai-hk.com 提供的代理地址
        base_url='https://api.openai-hk.com/v1/',
        openai_api_key=openai_api_key
    )

    # 定义输出解析器
    output_parser = PydanticOutputParser(pydantic_object=Xiaohongshu)

    # 创建调用链
    chain = prompt | model | output_parser

    # 调用链并传入参数
    result = chain.invoke({
        'parser_instructions': output_parser.get_format_instructions(),
        'theme': theme
    })

    return result


# ====================================================================
# 4. 来自 main.py 的内容
# Streamlit 界面逻辑
# ====================================================================
st.set_page_config(page_title="爆款小红书AI写作助手", page_icon="🐖")
st.header('爆款小红书AI写作助手 🐖')

with st.sidebar:
    openai_api_key = st.text_input('请输入API密钥：', type='password')
    st.markdown("密钥来自[OpenAI-HK](https://openai-hk.com/c/0/b/key)网站，非官方。")

theme = st.text_input('请输入您想要生成的小红书主题：')

submit = st.button('开始写作')

# 处理按钮点击事件
if submit:
    # 检查API密钥和主题是否已输入
    if not openai_api_key:
        st.error('请输入你的API密钥')
        st.stop()
    if not theme:
        st.error('请输入小红书文案的主题')
        st.stop()

    # 显示加载动画，并调用生成函数
    with st.spinner('AI正在努力创作中，请稍等...'):
        try:
            result = generate_xiaohongshu(theme, openai_api_key)
        except Exception as e:
            st.error(f"生成内容时出现错误：{e}")
            st.stop()

    # 显示生成结果
    st.divider()
    st.markdown("### ✨ AI生成结果")

    left_column, right_column = st.columns(2)

    with left_column:
        st.markdown('#### 备选标题')
        # 使用更简洁的方式显示标题
        for i, title in enumerate(result.titles):
            st.write(f"{i+1}. {title}")

    with right_column:
        st.markdown('#### 正文内容')
        st.write(result.content)