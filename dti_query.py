import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -------------- 1. 读取数据 --------------
@st.cache_data(ttl=0)
def load_data():
    return pd.read_excel("企业数字化转型指数结果.xlsx")
df = load_data()
df["股票代码"] = df["股票代码"].astype(str)
df = df.sort_values("年份")
all_years = sorted(df["年份"].unique())
all_stocks = df["股票代码"].unique()

# -------------- 2. 前端界面 --------------
st.set_page_config(page_title="数字化转型指数查询", layout="wide")
st.title("企业数字化转型指数趋势分析")
st.subheader("📊 多企业对比+指定年份标注", divider="blue")

# 左侧查询设置
with st.sidebar:
    st.header("🔍 查询条件")
    # 多股票代码输入（逗号分隔）
    stock_codes = st.text_input(
        "股票代码（多个用逗号分隔）",
        placeholder="例：000001,000002",
        value="000001"
    )
    # 选择需要标注的年份
    target_year = st.selectbox("选择标注年份", all_years, index=all_years.index(2004))
    # 按钮
    query_btn = st.button("生成趋势图", type="primary")
    reset_btn = st.button("重置")

    st.divider()
    st.info("### 📌 效果说明")
    st.write("1. 输入多个股票代码，展示多企业趋势对比")
    st.write("2. 选择年份后，在对应点添加箭头+年份+数值标注")

# -------------- 3. 重置功能 --------------
if reset_btn:
    st.experimental_rerun()

# -------------- 4. 可视化逻辑 --------------
if query_btn:
    if not stock_codes:
        st.warning("⚠️ 请输入至少一个股票代码！")
    else:
        # 处理多股票代码
        code_list = [code.strip() for code in stock_codes.split(",")]
        # 筛选数据（多股票+全年份）
        filter_df = df[df["股票代码"].isin(code_list)]
        
        if len(filter_df) == 0:
            st.error("❌ 未找到匹配数据！")
        else:
            # 提取指定年份的所有企业数据（用于标注）
            target_data = filter_df[filter_df["年份"] == target_year]

            # -------------- 绘制多企业趋势图 --------------
            fig = go.Figure()
            # 为每个企业绘制折线
            for stock in code_list:
                company_df = filter_df[filter_df["股票代码"] == stock]
                if len(company_df) == 0:
                    continue
                fig.add_trace(go.Scatter(
                    x=company_df["年份"],
                    y=company_df["数字化转型指数"],
                    mode="lines+markers",
                    name=f"{company_df.iloc[0]['企业名称']} ({stock})",
                    line=dict(width=2),
                    marker=dict(size=6)
                ))

            # -------------- 为指定年份添加箭头+数值标注 --------------
            for _, row in target_data.iterrows():
                fig.add_annotation(
                    x=row["年份"],
                    y=row["数字化转型指数"],
                    text=f"{row['年份']}年: {row['数字化转型指数']:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="#ff5722",
                    ax=0,
                    ay=20 if row["数字化转型指数"] < 0 else -20,  # 数值为负时箭头向下
                    font=dict(size=10, color="#333")
                )

            # 优化图表样式（与示例图一致）
            fig.update_layout(
                title=f"数字化转型指数趋势 (1999-2023) | {target_year}年",
                xaxis_title="年份",
                yaxis_title="数字化转型指数",
                height=500,
                showlegend=True,
                legend_title="企业信息",
                xaxis_tickmode="linear"  # 年份均匀分布
            )
            st.plotly_chart(fig, use_container_width=True)

            # 展示详细数据
            st.subheader("📋 详细数据")
            show_df = filter_df[["年份", "股票代码", "企业名称", "数字化转型指数"]].sort_values(["年份", "企业名称"])
            show_df["数字化转型指数"] = show_df["数字化转型指数"].round(2)
            st.dataframe(show_df, use_container_width=True, hide_index=True)
