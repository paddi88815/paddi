import streamlit as st
import pandas as pd
import plotly.graph_objects as go  # 更灵活的绘图库

# -------------- 1. 读取数据 --------------
@st.cache_data(ttl=0)  # 禁用缓存，确保读取最新Excel
def load_data():
    return pd.read_excel("企业数字化转型指数结果.xlsx")
df = load_data()
df["股票代码"] = df["股票代码"].astype(str)
df = df.sort_values("年份")
all_years = sorted(df["年份"].unique())
all_stocks = df["股票代码"].unique()

# -------------- 2. 前端界面 --------------
st.set_page_config(page_title="数字化转型指数查询", layout="wide")
st.title("企业数字化转型指数查询系统")
st.subheader("📊 指数趋势（带年份箭头标注）", divider="blue")

# 左侧查询设置
with st.sidebar:
    st.header("🔍 查询设置")
    # 查询方式：股票代码/企业名称
    query_mode = st.radio("查询方式", ["股票代码", "企业名称"], index=0)
    # 输入框
    if query_mode == "股票代码":
        stock_code = st.text_input("股票代码", placeholder="例：000001")
        filter_col = "股票代码"
        filter_val = stock_code.strip()
    else:
        company_name = st.text_input("企业名称", placeholder="例：平安银行")
        filter_col = "企业名称"
        filter_val = company_name.strip()
    # 年份选择
    query_year = st.selectbox("查询年份", all_years, index=len(all_years)-1)
    # 按钮
    query_btn = st.button("执行查询", type="primary")
    reset_btn = st.button("重置")

# -------------- 3. 数据筛选与可视化（带箭头标注） --------------
if reset_btn:
    st.experimental_rerun()  # 重置页面

if query_btn:
    if not filter_val:
        st.warning("⚠️ 请输入查询内容！")
    else:
        # 筛选数据
        filter_df = df[df[filter_col] == filter_val]
        if len(filter_df) == 0:
            st.error("❌ 未找到匹配数据！")
        else:
            # 提取该企业的所有年份数据
            company_df = filter_df.sort_values("年份")
            # 提取指定年份的数据（用于箭头标注）
            target_year_data = company_df[company_df["年份"] == query_year].iloc[0]

            # -------------- 绘制带箭头的折线图 --------------
            fig = go.Figure()
            # 绘制折线
            fig.add_trace(go.Scatter(
                x=company_df["年份"],
                y=company_df["数字化转型指数"],
                mode="lines+markers",
                name=target_year_data["企业名称"],
                line=dict(width=3, color="#1f77b4"),
                marker=dict(size=8, color="#1f77b4")
            ))

            # 为每一年添加箭头标注
            for idx, row in company_df.iterrows():
                fig.add_annotation(
                    x=row["年份"],
                    y=row["数字化转型指数"],
                    text=f"{row['年份']}年",  # 标注内容：年份
                    showarrow=True,
                    arrowhead=2,  # 箭头样式
                    arrowcolor="#ff7f0e",  # 箭头颜色
                    ax=0,  # 箭头水平偏移
                    ay=-20,  # 箭头垂直偏移（向上）
                    font=dict(size=10, color="#333")
                )

            # 优化图表样式
            fig.update_layout(
                title=f"数字化转型指数趋势 (1999-2023) | {query_year}年",
                xaxis_title="年份",
                yaxis_title="数字化转型指数",
                height=500,
                showlegend=True,
                legend_title="企业名称"
            )
            st.plotly_chart(fig, use_container_width=True)

            # 展示详细数据
            st.subheader("📋 详细数据")
            show_df = company_df[["年份", "股票代码", "企业名称", "数字化转型指数"]]
            show_df["数字化转型指数"] = show_df["数字化转型指数"].round(2)
            st.dataframe(show_df, use_container_width=True, hide_index=True)

