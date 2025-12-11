import streamlit as st
import pandas as pd
import plotly.express as px

# -------------- 1. 读取并预处理数据 --------------
df = pd.read_excel("企业数字化转型指数结果.xlsx")
df["股票代码"] = df["股票代码"].astype(str)  # 统一字符串格式
df = df.sort_values("年份")  # 按年份排序
all_years = sorted(df["年份"].unique())  # 提取所有年份（用于下拉框）
all_stocks = df["股票代码"].unique()  # 提取所有股票代码

# -------------- 2. 前端界面布局 --------------
st.set_page_config(page_title="数字化转型指数查询", layout="wide")  # 宽屏布局
st.title("企业数字化转型指数查询系统")
st.subheader("📊 指数查询与趋势可视化", divider="blue")

# 分栏布局：左侧筛选条件，右侧结果展示
col1, col2 = st.columns([1, 3])

with col1:
    st.sidebar.header("🔍 查询条件")
    # 股票代码输入（支持多个）
    stock_codes = st.sidebar.text_input(
        "股票代码（多个用逗号分隔）",
        placeholder="例：600000 或 600000,600016",
        help="可输入多个代码，用英文逗号分隔"
    )
    
    # 年份筛选：单选/多选/全部
    query_type = st.sidebar.radio("查询类型", ["单年份查询", "多年份趋势查询"])
    if query_type == "单年份查询":
        selected_year = st.sidebar.selectbox("选择年份", all_years, index=len(all_years)-1)
        year_filter = [selected_year]  # 单年份
    else:
        selected_years = st.sidebar.multiselect(
            "选择年份（默认全部）",
            all_years,
            default=all_years,
            help="可勾选多个年份，展示趋势"
        )
        year_filter = selected_years  # 多年份

    # 查询按钮
    query_btn = st.sidebar.button("执行查询", type="primary")

# -------------- 3. 数据筛选与可视化 --------------
with col2:
    if query_btn:
        # 校验输入
        if not stock_codes:
            st.warning("⚠️ 请输入至少一个股票代码！")
        elif not year_filter:
            st.warning("⚠️ 请选择至少一个年份！")
        else:
            # 处理股票代码
            code_list = [code.strip() for code in stock_codes.split(",")]
            # 筛选数据（股票代码+年份）
            filter_df = df[
                (df["股票代码"].isin(code_list)) & 
                (df["年份"].isin(year_filter))
            ]

            if len(filter_df) == 0:
                st.error("❌ 未找到匹配的股票代码/年份数据！")
            else:
                # 展示查询结果概览
                st.success(f"✅ 查询结果：{len(code_list)} 家企业 · {len(year_filter)} 个年份")
                
                # 1. 绘制折线图（适配单/多年份）
                st.subheader("📈 数字化转型指数趋势")
                fig = px.line(
                    filter_df,
                    x="年份",
                    y="数字化转型指数",
                    color="企业名称",
                    symbol="股票代码",
                    title=f"{'单年份' if len(year_filter)==1 else '多年份'}指数对比",
                    labels={"数字化转型指数": "转型指数", "年份": "统计年份"},
                    hover_data={"股票代码": True, "企业名称": True, "数字化转型指数": ":.2f"},
                    markers=True  # 单年份时显示圆点，多年份时显示折线+圆点
                )
                fig.update_layout(height=500, xaxis_tickmode="linear")  # 优化样式
                st.plotly_chart(fig, use_container_width=True)

                # 2. 展示详细数据表格
                st.subheader("📋 详细数据")
                # 按年份+企业名称排序
                show_df = filter_df[["年份", "股票代码", "企业名称", "数字化转型指数"]].sort_values(["年份", "企业名称"])
                # 格式化指数为2位小数
                show_df["数字化转型指数"] = show_df["数字化转型指数"].round(2)
                st.dataframe(show_df, use_container_width=True, hide_index=True)

# -------------- 4. 侧边栏辅助信息 --------------
with st.sidebar:
    st.divider()
    st.info("### 📌 数据说明")
    st.write(f"📅 数据年份范围：{min(all_years)} - {max(all_years)}")
    st.write(f"🏢 覆盖企业数：{len(all_stocks)} 家")
    st.write("💡 单年份查询仅展示该年份数据，多年份可查看趋势变化")

