from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta

# 初始化 Dash 应用
app = Dash(__name__)

# 读取 Excel 文件
file_path = "/Users/siyuanxu/Desktop/Desktop - Sierra’s MacBook Air/ZQ/s/数据可视化/GLDI底稿0304(3).xlsx"   # 替换为你的 Excel 文件路径
df_price = pd.read_excel(file_path, sheet_name="行业-价", index_col=0)
df_price_volume = pd.read_excel(file_path, sheet_name="行业-价-量-分位数", index_col=0)
df_close_price = pd.read_excel(file_path, sheet_name="收盘价", index_col=0)

# 确保时间索引是 datetime 类型
df_price.index = pd.to_datetime(df_price.index)
df_price_volume.index = pd.to_datetime(df_price_volume.index)
df_close_price.index = pd.to_datetime(df_close_price.index)

# 获取所有行业名称
industries = df_price.columns.tolist()

# 定义网页布局
app.layout = html.Div([
    dcc.Tabs(id="industry-tabs", value="行业指数", children=[
        dcc.Tab(label="行业指数", value="行业指数"),  # 行业指数 Tab
        *[dcc.Tab(label=industry, value=industry) for industry in industries]
    ]),
    html.Div(id="industry-content")  # 动态加载内容
])

# 定义回调函数
@app.callback(
    Output("industry-content", "children"),
    Input("industry-tabs", "value")
)
def update_content(selected_tab):
    # 如果选择的是行业指数 Tab
    if selected_tab == "行业指数":
        # 直接嵌入行业-价-图的截图
        return html.Img(
            src="assets/1.png",  # 确保路径正确
            style={"width": "100%", "height": "auto"}  # 图片自适应宽度
        )

    # 如果选择的是其他行业 Tab
    else:
        selected_industry = selected_tab

        # 检查 selected_industry 是否在 df_close_price 的列名中
        if selected_industry not in df_close_price.columns:
            return dcc.Graph(figure=go.Figure())  # 返回一个空的图表

        # 创建子图
        fig = go.Figure()

        # 添加第一条线（行业-价）
        fig.add_trace(
            go.Scatter(
                x=df_price.index,
                y=df_price[selected_industry],
                name=f"{selected_industry}(Price)",
                line=dict(color="#CFBD9B", width=2.25),
            )
        )

        # 添加第二条线（行业-价-量-分位数）
        fig.add_trace(
            go.Scatter(
                x=df_price_volume.index,
                y=df_price_volume[selected_industry],
                name=f"{selected_industry}(Price-Volume)分位数",
                line=dict(color="#C8C8C8", width=1),
            )
        )

        # 添加第三条线（行业收盘价）
        fig.add_trace(
            go.Scatter(
                x=df_close_price.index,
                y=df_close_price[selected_industry],
                name=f"{selected_industry}收盘价(右轴)",
                line=dict(color="#C0504D", width=3),
                yaxis="y2",  # 使用第二个 Y 轴
            )
        )

        # 动态获取最新时间作为 end_date
        end_date = df_price.index[0]  # Excel 文件中最新时间（第一行）
        start_date = end_date - timedelta(days=365)  # 过去一年的起始时间

        # 计算右轴的范围（选取范围内的 min-100 到 max+100）
        selected_close_price = df_close_price.loc[start_date:end_date, selected_industry]
        y2_min = selected_close_price.min() - 100
        y2_max = selected_close_price.max() + 100

        # 设置布局
        fig.update_layout(
            title=f"{selected_industry} 数据趋势",
            xaxis=dict(
                title="时间",
                rangeslider=dict(visible=True),  # 显示范围滑块
                range=[start_date, end_date],    # 设置默认显示范围（从最新时间往前推一年）
                autorange=False,                 # 禁用自动调整范围
            ),
            yaxis=dict(
                title="分位数",  # 左轴标题
                tickformat=".0%",  # 将左轴显示为百分比
                range=[0, 1],      # 设置左轴范围为 0 到 1
                fixedrange=False,  # 允许 Y 轴缩放
                showline=True,     # 显示左侧边框
                linewidth=1,       # 设置左侧边框宽度
            ),
            yaxis2=dict(
                title="收盘价",  # 右轴标题
                overlaying="y",
                side="right",
                range=[y2_min, y2_max],  # 动态设置右轴范围
                showline=True,     # 显示右侧边框
                linewidth=1,       # 设置右侧边框宽度
            ),
            hovermode="x unified",
            legend=dict(
                orientation="h",  # 图例水平排列
                yanchor="bottom", # 图例位于底部
                y=1.02,           # 图例位于图表上方
                xanchor="center", # 图例水平居中
                x=0.5,            # 图例水平居中
                font=dict(weight="bold"),  # 图例字体加粗
            ),
            template="plotly_white",
        )

        # 添加水平虚线
        latest_price_value = df_price[selected_industry].iloc[1]  # 最新时间的数据（第二行）
        latest_price_volume_value = df_price_volume[selected_industry].iloc[1]  # 最新时间的数据（第二行）
        latest_close_price_value = df_close_price[selected_industry].iloc[1]  # 最新时间的数据（第二行）

        fig.add_shape(
            type="line",
            x0=df_price.index.min(), y0=latest_price_value,
            x1=df_price.index.max(), y1=latest_price_value,
            line=dict(color="black", width=2.25, dash="dash"),  # 调整颜色和宽度
        )
        fig.add_shape(
            type="line",
            x0=df_price.index.min(), y0=latest_price_volume_value,
            x1=df_price.index.max(), y1=latest_price_volume_value,
            line=dict(color="black", width=2.25, dash="dash"),  # 调整颜色和宽度
        )
        fig.add_shape(
            type="line",
            x0=df_price.index.min(), y0=latest_close_price_value,
            x1=df_price.index.max(), y1=latest_close_price_value,
            line=dict(color="black", width=2.25, dash="dash"),  # 调整颜色和宽度
        )

        return dcc.Graph(figure=fig)

# 运行应用
if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8050)