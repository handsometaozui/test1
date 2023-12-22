import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import pandas as pd
import plotly.express as px
import re
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 在左侧的列中添加一个文本框，用于输入目标网址
url = st.sidebar.text_input('输入网址')

# 异常处理：检查URL的有效性
if not url.startswith('http://') and not url.startswith('https://'):
    st.sidebar.warning("请输入有效的URL")
else:
    try:
        # 使用爬虫获取输入网址的内容
        response = requests.get(url)
        # 根据文本的内容来推测它的编码方式，防止中文乱码输出。
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取纯文本内容
        text_content = soup.get_text()

        # 去除文本中的标点符号和空白字符
        text_content = re.sub(r'[^\w\s]', '', text_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()

        # 对文本分词，并统计词频，过滤单词长度为1的词
        words = [word for word in jieba.cut(text_content) if word.strip() and len(word) > 1]
        word_counts = Counter(words)

        # 创建数据集
        data = {'词语': list(word_counts.keys()), '频次': list(word_counts.values())}
        df = pd.DataFrame(data)

        # 对数据框按频次降序排序
        df = df.sort_values(by='频次', ascending=False)

        # 截取前二十行数据
        df_top20 = df.head(20)

        # 添加名次列
        df_top20['名次'] = df_top20.reset_index().index + 1

        # 计算纵坐标的间隔值
        y_tick_interval = max(1, max(df_top20['频次']) // 10)

        # 在右侧的列中添加单选框，用于选择图表类型
        chart_type = st.sidebar.radio('选择你想展示的图表', ['数状图', '折线图', '饼状图', '散点图', '面积图', '圆环图', '雷达图'])

        if chart_type == '数状图':
            fig = px.bar(df_top20, x='词语', y='频次', title='单词-频次 - 数状图')
        elif chart_type == '折线图':
            fig = px.line(df_top20, x='词语', y='频次', title='单词-频次 - 折线图')
        elif chart_type == '饼状图':
            fig = px.pie(df_top20, names='词语', values='频次', title='单词-频次 - 饼状图')
        elif chart_type == '散点图':
            fig = px.scatter(df_top20, x='词语', y='频次', title='单词-频次 - 散点图')
        elif chart_type == '面积图':
            fig = px.area(df_top20, x='词语', y='频次', title='单词-频次 - 面积图')

        elif chart_type == '圆环图':
            fig = px.pie(df_top20, names='词语', values='频次', title='单词-频次 - 圆环图', hole=0.3)
        elif chart_type == '雷达图':
            fig = px.line_polar(df_top20, r='频次', theta='词语', line_close=True, title='单词-频次 - 雷达图')

        # 设置图表字体为中文支持的字体
        if chart_type not in ['雷达图']:
            fig.update_layout(font=dict(family="SimHei", size=12))

        # 将 y 轴的坐标轴间隔设置为计算得到的间隔值
        if chart_type not in ['雷达图']:
            fig.update_yaxes(tickvals=list(range(0, max(df_top20['频次']) + 1, y_tick_interval)))

        # 旋转 x 轴标签
        if chart_type not in ['雷达图']:
            fig.update_xaxes(tickangle=45)

        # 将 Plotly 图表嵌入 Streamlit 应用
        if chart_type not in ['雷达图']:
            st.plotly_chart(fig)
        else:
            st.plotly_chart(fig, use_container_width=True)

        # 显示排名前二十的词汇
        st.subheader("排名前二十的词汇:")
        st.table(df_top20.set_index('名次'))  # 将 '名次' 列设置为索引

        #生成词云，使用前二十的词频数据
        wordcloud = WordCloud(
            width=800,
            height=400,
            font_path='文泉驿正黑.ttc',  # 替换为中文字体路径
            background_color='white'
        ).generate_from_frequencies(df_top20.set_index('词语')['频次'].to_dict())

        st.subheader("词云图:")
        st.image(wordcloud.to_array(), caption="词云图", use_column_width=True)
        # text_data = df_top20.set_index('词语')['频次'].to_dict()

        # # 创建词云对象
        # wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(text_data)

        # # 使用 matplotlib 显示词云图
        # plt.figure(figsize=(10, 5))
        # plt.imshow(wordcloud, interpolation='bilinear')
        # plt.axis('off')
        # plt.show()

    except requests.exceptions.MissingSchema:
        st.sidebar.warning("请输入有效的URL")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"发生错误: {e}")
