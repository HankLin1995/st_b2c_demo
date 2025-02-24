import streamlit as st
import json
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import os
from io import BytesIO

# 設置頁面配置
st.set_page_config(
    page_title="海鮮購物網後台管理系統",
    page_icon="🐟",
    layout="wide"
)

# 確保數據目錄存在
os.makedirs('data', exist_ok=True)

# 載入數據函數
def load_data():
    # 獲取當前文件的目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')

    # 載入商品數據
    try:
        with open(os.path.join(data_dir, 'products.json'), 'r', encoding='utf-8') as f:
            products = json.load(f)
            st.session_state.products = products
            print(f"成功載入 {len(products)} 個商品")
    except Exception as e:
        print(f"載入商品數據時出錯: {str(e)}")
        st.session_state.products = []

    # 載入訂單數據
    try:
        with open(os.path.join(data_dir, 'orders.json'), 'r', encoding='utf-8') as f:
            orders = json.load(f)
            st.session_state.orders = orders
            print(f"成功載入 {len(orders)} 個訂單")
    except Exception as e:
        print(f"載入訂單數據時出錯: {str(e)}")
        st.session_state.orders = []

# 初始化 session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    load_data()

# 保存商品數據
def save_products():
    with open('data/products.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.products, f, ensure_ascii=False, indent=2)

# 保存訂單數據
def save_orders():
    with open('data/orders.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.orders, f, ensure_ascii=False, indent=2)

# 側邊欄
st.sidebar.title("功能選單")
page = st.sidebar.radio("選擇功能", ["商品管理", "訂單管理", "銷售分析", "備貨清單"])
st.sidebar.markdown("---")

# 主要內容
if page == "商品管理":
    st.title("商品管理")
    
    # 新增商品表單
    with st.expander("新增商品", expanded=False):
        with st.form("add_product"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("商品名稱")
                category = st.selectbox(
                    "商品類別",
                    ["鮮魚", "蝦類", "螃蟹", "貝類"]
                )
                price = st.number_input("價格", min_value=0, value=100)
                stock = st.number_input("庫存", min_value=0, value=10)
            with col2:
                spec = st.text_input("規格")
                image_url = st.text_input("圖片URL")
                description = st.text_area("商品描述")
            
            if st.form_submit_button("新增"):
                if name and category and price and spec:
                    new_product = {
                        "名稱": name,
                        "類別": category,
                        "價格": price,
                        "庫存": stock,
                        "規格": spec,
                        "圖片": image_url,
                        "描述": description
                    }
                    st.session_state.products.append(new_product)
                    save_products()
                    st.success("商品新增成功！")
    
    # 商品列表
    if st.session_state.products:
        st.subheader("商品列表")
        df = pd.DataFrame(st.session_state.products)
        
        # 添加操作列
        df["操作"] = False
        
        # 使用 data editor
        edited_df = st.data_editor(
            df,
            hide_index=True,
            use_container_width=True
        )
        
        # 刪除選中的商品
        if st.button("刪除選中商品"):
            to_delete = edited_df[edited_df["操作"]].index.tolist()
            for idx in sorted(to_delete, reverse=True):
                del st.session_state.products[idx]
            save_products()
            st.success("已刪除選中商品")
            st.rerun()
        
        # 保存編輯的更改
        if not edited_df.equals(df):
            for i, row in edited_df.iterrows():
                if i < len(st.session_state.products):
                    st.session_state.products[i].update(row.to_dict())
            save_products()
            st.success("更改已保存！")

elif page == "訂單管理":
    st.title("訂單管理")
    
    # 搜索和篩選
    search_col1, search_col2, search_col3= st.columns([2,2,2])
    with search_col1:
        search_term = st.text_input("搜尋訂單", key="order_search")
    with search_col2:
        status_filter = st.multiselect(
            "訂單狀態",
            ["待處理", "處理中", "已完成", "已取消"],
            default=[],
            key="status_filter"
        )
    with search_col3:
        pickup_locations = list(set(order['取貨地點'] for order in st.session_state.orders))
        location_filter = st.multiselect(
            "取貨地點",
            pickup_locations,
            default=[],
            key="location_filter"
        )
    
    # 過濾訂單
    filtered_orders = []
    for order in st.session_state.orders:
        if status_filter and order['狀態'] not in status_filter:
            continue
        if location_filter and order['取貨地點'] not in location_filter:
            continue
        if not search_term or search_term.lower() in order['訂單號'].lower() or search_term.lower() in order['客戶名稱'].lower():
            filtered_orders.append(order)
    
    if filtered_orders:
        # 分頁設置
        items_per_page = 25
        total_orders = len(filtered_orders)
        total_pages = (total_orders + items_per_page - 1) // items_per_page
        
        # 分頁選擇器（暫存頁碼）
        if 'page_number' not in st.session_state:
            st.session_state.page_number = 1
        
        # 計算當前頁的訂單範圍
        start_idx = (st.session_state.page_number - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_orders)
        current_page_orders = filtered_orders[start_idx:end_idx]
        
        # 準備導出數據
        export_data = []
        for order in filtered_orders:
            for item in order['商品']:
                export_data.append({
                    '訂單編號': order['訂單號'],
                    '日期': order['日期'],
                    '客戶名稱': order['客戶名稱'],
                    '電話': order['電話'],
                    '取貨地點': order['取貨地點'],
                    '商品名稱': item['商品名稱'],
                    '數量': item['數量'],
                    '單價': item['單價'],
                    '小計': item['小計'],
                    '狀態': order['狀態']
                })
        
        # 創建DataFrame並轉換為Excel格式的bytes
        df = pd.DataFrame(export_data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_data = output.getvalue()
        
        # 導出按鈕（放在側邊欄）
        st.sidebar.download_button(
            label="📥 導出訂單",
            data=excel_data,
            file_name=f'訂單報表_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # 顯示當前頁的訂單
        for order in current_page_orders:
            # 根據狀態設置顏色
            status_colors = {
                "待處理": "🔴",
                "處理中": "🟡",
                "已出貨": "🟢",
                "已完成": "🟢"
            }
            status_emoji = status_colors.get(order['狀態'], "⚪")
            with st.expander(f"{status_emoji} 訂單號：{order['訂單號']} - {order['日期']} - {order['客戶名稱']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("📦 訂單資訊")
                    st.write(f"狀態：{status_emoji} {order['狀態']}")
                    st.write(f"訂購時間：{order['日期']}")
                    st.write("---")
                    st.write(f"運費：NT$ {order['運費']}")
                    st.write(f"總金額：NT$ {order['總金額']}")
                
                with col2:
                    st.write("👤 客戶與配送資訊")
                    st.write(f"姓名：{order['客戶名稱']}")
                    st.write(f"電話：{order['電話']}")
                    st.write("---")
                    
                    if order['取貨方式'] == "宅配到府":
                        st.write("🚚 宅配到府")
                        st.write(f"配送地址：{order['地址']}")
                    else:
                        st.write("🏪 市場取貨")
                        st.write(f"取貨地點：{order['取貨地點']}")
                
                st.write("🛒 商品明細")
                items_df = pd.DataFrame(order['商品'])
                st.dataframe(items_df, hide_index=True)
                
                # 訂單狀態更新
                new_status = st.selectbox(
                    "更新訂單狀態",
                    ["待處理", "處理中", "已出貨", "已完成", "已取消"],
                    index=["待處理", "處理中", "已出貨", "已完成", "已取消"].index(order['狀態']),
                    key=f"status_{order['訂單號']}"
                )
                
                if new_status != order['狀態']:
                    order['狀態'] = new_status
                    save_orders()
                    st.success("訂單狀態已更新！")
        
        # 分頁控制（在所有訂單顯示完後）
        st.markdown("---")

        # 更新頁碼
        new_page = st.sidebar.selectbox(
            "選擇頁數",
            options=range(1, total_pages + 1),
            index=st.session_state.page_number - 1,
            key="page_select"
        )
        if new_page != st.session_state.page_number:
            st.session_state.page_number = new_page
            st.rerun()

        st.markdown(f"**第 {st.session_state.page_number} 頁，共 {total_pages} 頁**")

    else:
        st.info("沒有找到符合條件的訂單")

elif page == "銷售分析":
    st.title("銷售分析")
    
    if st.session_state.orders:
        # 準備數據
        sales_data = []
        customer_data = []
        for order in st.session_state.orders:
            order_date = datetime.strptime(order['日期'], '%Y-%m-%d').date()
            order_total = sum(item['小計'] for item in order['商品'])
            
            # 收集銷售數據
            for item in order['商品']:
                sales_data.append({
                    '日期': order_date,
                    '商品名稱': item['商品名稱'],
                    '銷量': item['數量'],
                    '銷售額': item['小計'],
                    '取貨地點': order['取貨地點']
                })
            
            # 收集客戶數據
            customer_data.append({
                '客戶名稱': order['客戶名稱'],
                '電話': order['電話'],
                '訂單日期': order_date,
                '訂單金額': order_total,
                '取貨方式': order['取貨方式'],
                '取貨地點': order.get('取貨地點', ''),
                '商品數量': len(order['商品'])
            })

        sales_df = pd.DataFrame(sales_data)
        customer_df = pd.DataFrame(customer_data)
        
        # 銷售統計卡片
        st.markdown("""
        <style>
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #1f77b4;
        }
        .metric-label {
            font-size: 16px;
            color: #666;
            margin-top: 5px;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state.orders)}</div>
                <div class="metric-label">總訂單數</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">NT$ {sales_df['銷售額'].sum():,.0f}</div>
                <div class="metric-label">總銷售額</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(customer_df['客戶名稱'].unique())}</div>
                <div class="metric-label">不重複客戶數</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">NT$ {customer_df['訂單金額'].mean():,.0f}</div>
                <div class="metric-label">平均客單價</div>
            </div>
            """, unsafe_allow_html=True)

        # 銷售趨勢分析
        tab1, tab2, tab3 = st.tabs(["📈 銷售趨勢", "📊 商品分析", "👥 客戶分析"])
        
        with tab1:
            # 時間範圍選擇
            date_range = st.selectbox(
                "選擇時間範圍",
                ["過去7天", "過去30天", "全部時間"],
                key="sales_date_range"
            )
            
            # 處理日期範圍
            today = datetime.now().date()
            if date_range == "過去7天":
                start_date = today - timedelta(days=7)
            elif date_range == "過去30天":
                start_date = today - timedelta(days=30)
            else:
                start_date = None
            
            # 過濾數據
            filtered_sales = sales_df.copy()
            filtered_sales['日期'] = pd.to_datetime(filtered_sales['日期'])
            if start_date:
                filtered_sales = filtered_sales[filtered_sales['日期'].dt.date >= start_date]
            
            # 計算每日銷售數據
            daily_sales = filtered_sales.groupby('日期').agg({
                '銷售額': 'sum',
                '銷量': 'sum'
            }).reset_index()
            
            # 銷售趨勢圖
            fig = px.line(daily_sales, 
                         x='日期', 
                         y='銷售額',
                         title=f'銷售趨勢 ({date_range})',
                         template='plotly_white')
            
            fig.update_layout(
                plot_bgcolor='white',
                yaxis_title='銷售額 (NT$)',
                xaxis_title='日期',
                height=400
            )
            
            fig.update_traces(
                line_color='#1f77b4',
                line_width=2,
                name='銷售額'
            )
            
            st.plotly_chart(fig, use_container_width=True, key="sales_trend")
            
            # 銷售統計摘要
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_sales = daily_sales['銷售額'].sum()
                avg_daily_sales = daily_sales['銷售額'].mean()
                st.metric(
                    "總銷售額",
                    f"NT$ {total_sales:,.0f}",
                    f"日均 NT$ {avg_daily_sales:,.0f}"
                )
            
            with col2:
                if len(daily_sales) > 1:
                    growth_rate = ((daily_sales['銷售額'].iloc[-1] - daily_sales['銷售額'].iloc[0]) 
                                 / daily_sales['銷售額'].iloc[0] * 100)
                    st.metric(
                        "銷售成長率",
                        f"{growth_rate:+.1f}%",
                        "相比期初"
                    )
            
            with col3:
                peak_date = daily_sales.loc[daily_sales['銷售額'].idxmax()]
                st.metric(
                    "最高單日銷售",
                    f"NT$ {peak_date['銷售額']:,.0f}",
                    f"{peak_date['日期'].strftime('%Y-%m-%d')}"
                )
        
        with tab2:
            st.subheader("商品分析摘要")
            
            # 商品銷售分析
            product_sales = sales_df.groupby('商品名稱').agg({
                '銷量': 'sum',
                '銷售額': 'sum'
            }).reset_index()
            
            # 計算商品分析摘要指標
            total_products = len(product_sales)
            total_quantity = product_sales['銷量'].sum()
            avg_price_per_unit = (product_sales['銷售額'].sum() / product_sales['銷量'].sum())
            
            # 顯示商品分析摘要指標
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("商品總數", f"{total_products:,d}")
            with col2:
                st.metric("總銷售數量", f"{total_quantity:,d}")
            with col3:
                st.metric("平均單價", f"NT$ {avg_price_per_unit:,.0f}")
            
            st.markdown("---")
            
            # 商品銷售明細和銷量分布
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("商品銷售明細")
                # 顯示銷售明細表格
                product_sales_formatted = product_sales.copy()
                # 計算平均單價
                product_sales_formatted['平均單價'] = product_sales_formatted['銷售額'] / product_sales_formatted['銷量']
                # 格式化金額顯示
                product_sales_formatted['平均單價'] = product_sales_formatted['平均單價'].apply(lambda x: f"NT$ {x:,.0f}")
                product_sales_formatted['銷售額'] = product_sales_formatted['銷售額'].apply(lambda x: f"NT$ {x:,.0f}")
                product_sales_formatted = product_sales_formatted.rename(columns={
                    '商品名稱': '商品名稱',
                    '銷量': '銷售數量',
                    '銷售額': '銷售金額',
                    '平均單價': '平均單價'
                })
                st.dataframe(
                    product_sales_formatted,
                    column_config={
                        "商品名稱": st.column_config.TextColumn("商品名稱", width="medium"),
                        "銷售數量": st.column_config.NumberColumn("銷售數量", format="%d"),
                        "銷售金額": st.column_config.TextColumn("銷售金額", width="medium"),
                        "平均單價": st.column_config.TextColumn("平均單價", width="medium")
                    },
                    hide_index=True
                )
            
            with col2:
                st.subheader("商品銷量分布")
                # 商品銷量分布甜甜圈圖
                fig = px.pie(product_sales,
                           values='銷量',
                           names='商品名稱',
                           title='',
                           template='plotly_white',
                           hole=0.6)  # 設置甜甜圈圖的中心孔洞大小
                
                fig.update_traces(
                    textposition='outside',
                    textinfo='percent+label',
                    pull=0.01  # 輕微分離每個區塊
                )
                fig.update_layout(
                    showlegend=False,  # 隱藏圖例
                    height=400,
                    margin=dict(t=0, b=0)  # 移除上下邊距
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            st.subheader("熱銷商品分析")
            
            # 商品銷售排行
            fig = px.bar(product_sales.sort_values('銷售額', ascending=True).tail(10),
                       x='銷售額',
                       y='商品名稱',
                       title='熱銷商品 TOP 10',
                       orientation='h',
                       template='plotly_white')
            fig.update_traces(marker_color='#2ecc71')
            fig.update_layout(
                plot_bgcolor='white',
                xaxis_title='銷售額 (NT$)',
                yaxis_title='商品名稱',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True, key="product_ranking")

        with tab3:
            # 客戶分析
            st.subheader("客戶消費分析")
            
            # 計算每個客戶的總消費金額和訂單次數
            customer_summary = customer_df.groupby('客戶名稱').agg({
                '訂單金額': ['sum', 'mean', 'count'],
                '商品數量': 'sum'
            }).reset_index()
            customer_summary.columns = ['客戶名稱', '總消費金額', '平均訂單金額', '訂單次數', '購買商品總數']
            
            # 客戶消費金額分布
            fig = px.histogram(customer_summary,
                             x='總消費金額',
                             nbins=20,
                             title='客戶消費金額分布',
                             template='plotly_white')
            fig.update_layout(
                plot_bgcolor='white',
                xaxis_title='消費金額 (NT$)',
                yaxis_title='客戶數量'
            )
            st.plotly_chart(fig, use_container_width=True, key="customer_spending_dist")
            
            # 客戶訂單頻率分析
            col1, col2 = st.columns(2)
            
            with col1:
                # 重複購買率
                total_customers = len(customer_summary)
                repeat_customers = len(customer_summary[customer_summary['訂單次數'] > 1])
                repeat_rate = (repeat_customers / total_customers) * 100
                
                st.metric(
                    "重複購買率",
                    f"{repeat_rate:.1f}%",
                    f"{repeat_customers} 位回購客戶"
                )
                
                # 訂單次數分布
                order_freq = customer_summary['訂單次數'].value_counts().reset_index()
                order_freq.columns = ['訂購次數', '客戶數量']
                fig = px.bar(
                    order_freq,
                    x='訂購次數',
                    y='客戶數量',
                    title='客戶訂購次數分布'
                )
                st.plotly_chart(fig, use_container_width=True, key="order_frequency_dist")
            
            with col2:
                # 取貨方式分析
                delivery_stats = customer_df['取貨方式'].value_counts()
                fig = px.pie(
                    values=delivery_stats.values,
                    names=delivery_stats.index,
                    title='取貨方式分布'
                )
                st.plotly_chart(fig, use_container_width=True, key="delivery_method_dist")
            
            # 客戶排行榜
            st.subheader("高價值客戶 TOP 10")
            top_customers = customer_summary.nlargest(10, '總消費金額')
            st.dataframe(
                top_customers,
                column_config={
                    "客戶名稱": "客戶名稱",
                    "總消費金額": st.column_config.NumberColumn(
                        "總消費金額",
                        format="NT$ %d"
                    ),
                    "平均訂單金額": st.column_config.NumberColumn(
                        "平均訂單金額",
                        format="NT$ %d"
                    ),
                    "訂單次數": "訂單次數",
                    "購買商品總數": "購買商品總數"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # 客戶行為摘要
            st.markdown("### 客戶行為摘要")
            st.markdown(f"""
            - 平均客單價：**NT$ {customer_df['訂單金額'].mean():,.0f}**
            - 客戶平均訂購次數：**{customer_summary['訂單次數'].mean():.1f}** 次
            - 最高客戶消費金額：**NT$ {customer_summary['總消費金額'].max():,.0f}**
            - 最常購買客戶：**{customer_summary.loc[customer_summary['訂單次數'].idxmax(), '客戶名稱']}** ({customer_summary['訂單次數'].max()} 次)
            """)
    else:
        st.info("目前還沒有任何訂單數據")

elif page == "備貨清單":
    if 'orders' in st.session_state and len(st.session_state.orders) > 0:
        df = pd.DataFrame(st.session_state.orders)
        
        # 將空的取貨地點改為"宅配到府"
        df['取貨地點'] = df['取貨地點'].replace('', '宅配到府')
        
        # 轉換日期列為datetime類型
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 讀取訂單資料
        df = pd.DataFrame(st.session_state.orders)
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 獲取所有有訂單的日期並格式化為字串
        available_dates = df['日期'].dt.date.unique()
        available_dates = sorted(available_dates, reverse=True)  # 降序排列，最新的日期在最前面
        date_options = [date.strftime('%Y-%m-%d') for date in available_dates]
        
        # 讓使用者從下拉選單選擇日期
        selected_date_str = st.sidebar.selectbox(
            "選擇日期",
            options=date_options,
            index=0
        )
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        
        # 篩選選定日期的訂單
        daily_orders = df[df['日期'].dt.date == selected_date]
        
        if len(daily_orders) > 0:
            # st.subheader(f"📅 {selected_date} 備貨清單")
            
            # 篩選非宅配到府的訂單
            pickup_orders = daily_orders[daily_orders['取貨方式'] == '市場取貨']
            
            if len(pickup_orders) > 0:
                # 計算當日總備貨需求
                total_products_demand = {}
                for _, order in pickup_orders.iterrows():
                    for item in order['商品']:
                        product_name = item['商品名稱']
                        quantity = item['數量']
                        if product_name not in total_products_demand:
                            total_products_demand[product_name] = 0
                        total_products_demand[product_name] += quantity
                
                # 轉換成DataFrame格式
                total_demand_df = pd.DataFrame([
                    {'商品名稱': product, '總數量': quantity}
                    for product, quantity in total_products_demand.items()
                ])
                total_demand_df = total_demand_df.sort_values('總數量', ascending=False)
                
                # 在側邊欄顯示當日總備貨需求
                st.sidebar.markdown("### 📦 總備貨需求")
                st.sidebar.dataframe(
                    total_demand_df,
                    hide_index=True,
                    use_container_width=True
                )
                
                st.sidebar.markdown("---")
                
                # 按取貨地點分組顯示
                for location in pickup_orders['取貨地點'].unique():
                    location_orders = pickup_orders[pickup_orders['取貨地點'] == location]
                    
                    # 顯示取貨地點標題
                    st.markdown(f"## 📍 {location}")
                    
                    # 使用列來排列客戶訂單卡片
                    st.markdown("""
                    <style>
                    .customer-card {
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        background-color: #f8f9fa;
                    }
                    .customer-info {
                        margin-bottom: 10px;
                    }
                    .customer-info h4 {
                        margin: 0;
                        color: #1f77b4;
                    }
                    .customer-info p {
                        margin: 5px 0;
                        color: #666;
                    }
                    .order-items {
                        margin-top: 10px;
                        padding-top: 10px;
                        border-top: 1px solid #eee;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # 使用 columns 布局
                    col1, col2, col3 = st.columns(3)
                    for idx, (_, order) in enumerate(location_orders.iterrows()):
                        # 根據索引決定顯示在哪一欄
                        with (col1 if idx % 3 == 0 else col2 if idx % 3 == 1 else col3):
                            st.markdown(f"""
                            <div class="customer-card">
                                <div class="customer-info">
                                    <h4>🧑‍💼 {order['客戶名稱']}</h4>
                                    <p>📝 訂單號：{order['訂單號']}</p>
                                    <p>📞 電話：{order['電話']}</p>
                                </div>
                                <div class="order-items">
                                    <p><strong>訂購商品：</strong></p>
                                    <ul style="list-style-type: none; padding-left: 0; margin: 5px 0;">
                                        {"".join(f'<li>• {item["商品名稱"]} × <strong>{item["數量"]}</strong></li>' for item in order['商品'])}
                                    </ul>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                
                # 匯出功能
                st.markdown("### 📤 匯出備貨單")
                
                if st.button("下載備貨單"):
                    # 創建一個 Excel 寫入器
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # 首先寫入總備貨需求
                        total_demand_df.to_excel(writer, sheet_name='總備貨需求', index=False)
                        
                        # 為每個取貨地點創建工作表
                        for location in pickup_orders['取貨地點'].unique():
                            location_orders = pickup_orders[pickup_orders['取貨地點'] == location]
                            
                            # 計算該地點的商品總量
                            location_products = {}
                            for _, order in location_orders.iterrows():
                                for item in order['商品']:
                                    product_name = item['商品名稱']
                                    quantity = item['數量']
                                    if product_name not in location_products:
                                        location_products[product_name] = 0
                                    location_products[product_name] += quantity
                            
                            # 創建商品總量DataFrame
                            products_df = pd.DataFrame([
                                {'商品名稱': product, '總數量': quantity}
                                for product, quantity in location_products.items()
                            ])
                            products_df = products_df.sort_values('總數量', ascending=False)
                            
                            # 創建訂單明細DataFrame
                            orders_data = []
                            for _, order in location_orders.iterrows():
                                for item in order['商品']:
                                    orders_data.append({
                                        '客戶名稱': order['客戶名稱'],
                                        '訂單號': order['訂單號'],
                                        '電話': order['電話'],
                                        '商品名稱': item['商品名稱'],
                                        '數量': item['數量']
                                    })
                            orders_df = pd.DataFrame(orders_data)
                            
                            # 寫入Excel
                            products_df.to_excel(writer, 
                                              sheet_name=f'{location}-商品總量',
                                              index=False)
                            orders_df.to_excel(writer,
                                            sheet_name=f'{location}-訂單明細',
                                            index=False)
                    
                    # 設定下載按鈕
                    output.seek(0)
                    st.download_button(
                        label="📥 下載 Excel 檔案",
                        data=output,
                        file_name=f'備貨單_{selected_date}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
            else:
                st.info(f"{selected_date} 沒有市場取貨的訂單")
        else:
            st.info("目前還沒有任何訂單數據")
    else:
        st.info("目前還沒有任何訂單數據")
