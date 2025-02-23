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
    # 載入商品數據
    try:
        with open('data/products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
            st.session_state.products = products
            print(f"成功載入 {len(products)} 個商品")
    except Exception as e:
        print(f"載入商品數據時出錯: {str(e)}")
        st.session_state.products = []

    # 載入訂單數據
    try:
        with open('data/orders.json', 'r', encoding='utf-8') as f:
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

# # 重新載入數據按鈕
# if st.sidebar.button("重新載入數據"):
#     load_data()
#     st.sidebar.success("數據已重新載入")

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
        location_data = []  
        for order in st.session_state.orders:
            order_date = datetime.strptime(order['日期'], '%Y-%m-%d').date()
            for item in order['商品']:
                sales_data.append({
                    '日期': order_date,
                    '商品名稱': item['商品名稱'],
                    '銷量': item['數量'],
                    '銷售額': item['小計'],
                    '取貨地點': order['取貨地點']
                })
                # 收集取貨地點數據
                location_data.append({
                    '取貨地點': order['取貨地點'],
                    '商品名稱': item['商品名稱'],
                    '數量': item['數量']
                })

        sales_df = pd.DataFrame(sales_data)
        location_df = pd.DataFrame(location_data)
        
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
                <div class="metric-value">NT$ {sales_df['銷售額'].sum() / len(st.session_state.orders):,.0f}</div>
                <div class="metric-label">平均訂單金額</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{sales_df['銷量'].sum():,.0f}</div>
                <div class="metric-label">總銷售數量 (件)</div>
            </div>
            """, unsafe_allow_html=True)

        # 分析圖表
        tab1, tab2 = st.tabs(["📈 銷售趨勢", "📊 商品分析"])
        
        with tab1:
            # 銷售趨勢圖
            daily_sales = sales_df.groupby('日期')['銷售額'].sum().reset_index()
            daily_sales['日期'] = pd.to_datetime(daily_sales['日期'])
            daily_sales = daily_sales.sort_values('日期')
            
            fig = px.line(daily_sales, 
                         x='日期', 
                         y='銷售額',
                         title='每日銷售趨勢',
                         template='plotly_white')
            fig.update_traces(line_color='#1f77b4', line_width=2)
            fig.update_layout(
                plot_bgcolor='white',
                yaxis_title='銷售額 (NT$)',
                xaxis_title='日期',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True, key="daily_sales_trend")
            
            # 計算成長率
            if len(daily_sales) > 1:
                growth_rate = ((daily_sales['銷售額'].iloc[-1] - daily_sales['銷售額'].iloc[0]) / daily_sales['銷售額'].iloc[0]) * 100
                st.info(f"期間銷售成長率: {growth_rate:.1f}%")
        
        with tab2:
            # 熱門商品分析
            product_sales = sales_df.groupby('商品名稱').agg({
                '銷量': 'sum',
                '銷售額': 'sum'
            }).reset_index()
            
            # 熱門商品長條圖
            fig = px.bar(product_sales.sort_values('銷售額', ascending=True),
                       x='銷售額',
                       y='商品名稱',
                       title='商品銷售排行',
                       orientation='h',
                       template='plotly_white')
            fig.update_traces(marker_color='#2ecc71')
            fig.update_layout(
                plot_bgcolor='white',
                xaxis_title='銷售額 (NT$)',
                yaxis_title='商品名稱',
                height=600,
                showlegend=False,
                title_x=0.5,
                title_font_size=20
            )
            fig.update_traces(
                texttemplate='NT$ %{x:,.0f}',
                textposition='outside',
                textfont_size=12
            )
            st.plotly_chart(fig, use_container_width=True, key="product_sales_ranking")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 銷量分布圓餅圖
                fig = px.pie(product_sales,
                           values='銷量',
                           names='商品名稱',
                           title='商品銷量分布',
                           template='plotly_white')
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    textfont_size=12,
                    hole=0.4
                )
                fig.update_layout(
                    height=500,
                    title_x=0.5,
                    title_font_size=20,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True, key="product_sales_distribution")
            
            with col2:
                # 商品銷售明細表
                st.subheader("商品銷售明細")
                
                # 計算銷售占比
                total_sales = product_sales['銷售額'].sum()
                product_sales['銷售占比'] = product_sales['銷售額'] / total_sales * 100
                
                # 格式化數據
                product_sales_display = product_sales.copy()
                product_sales_display['銷售額'] = product_sales_display['銷售額'].apply(lambda x: f'NT$ {x:,.0f}')
                product_sales_display['銷售占比'] = product_sales_display['銷售占比'].apply(lambda x: f'{x:.1f}%')
                
                # 排序並顯示
                product_sales_display = product_sales_display.sort_values('銷量', ascending=False)
                st.dataframe(
                    product_sales_display,
                    column_config={
                        "商品名稱": st.column_config.TextColumn("商品名稱", width="medium"),
                        "銷量": st.column_config.NumberColumn("銷量", format="%d"),
                        "銷售額": st.column_config.TextColumn("銷售額", width="medium"),
                        "銷售占比": "銷售占比"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # 顯示一些重要統計
                st.markdown("---")
                st.markdown("### 商品分析摘要")
                st.markdown(f"- 最暢銷商品：**{product_sales.iloc[0]['商品名稱']}** ({int(product_sales.iloc[0]['銷量'])} 件)")
                st.markdown(f"- 銷售額最高：**{product_sales.sort_values('銷售額', ascending=False).iloc[0]['商品名稱']}** (NT$ {product_sales.sort_values('銷售額', ascending=False).iloc[0]['銷售額']:,.0f})")
                st.markdown(f"- 平均單品銷量：**{product_sales['銷量'].mean():.1f}** 件")
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
        df = pd.read_json('data/orders.json')
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
