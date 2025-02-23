import streamlit as st
from streamlit_card import card
import pandas as pd
import json
from datetime import datetime

# 設置頁面配置
st.set_page_config(
    page_title="海鮮冷藏專賣店",
    page_icon="🐟",
    layout="wide"
)

# 商品數據
products = [
    {
        "類別": "鮮魚",
        "名稱": "挪威鮭魚切片",
        "規格": "300g/包",
        "價格": 299,
        "庫存": 50,
        "圖片": "https://images.unsplash.com/photo-1485921325833-c519f76c4927",
        "描述": "新鮮空運進口，油脂豐富"
    },
    {
        "類別": "鮮魚",
        "名稱": "黑鮪魚生魚片",
        "規格": "200g/盒",
        "價格": 599,
        "庫存": 25,
        "圖片": "https://images.unsplash.com/photo-1579712267685-42da80f60aa4",
        "描述": "頂級黑鮪魚，油脂豐富"
    },
    {
        "類別": "蝦類",
        "名稱": "活凍草蝦",
        "規格": "600g/盒",
        "價格": 399,
        "庫存": 40,
        "圖片": "https://images.unsplash.com/photo-1565680018434-b583b12be0d3",
        "描述": "現撈急凍，保持鮮甜"
    },
    {
        "類別": "蝦類",
        "名稱": "大明蝦",
        "規格": "400g/盒",
        "價格": 499,
        "庫存": 30,
        "圖片": "https://images.unsplash.com/photo-1565980928632-3db8f418e5e4",
        "描述": "肉質鮮美，口感彈牙"
    },
    {
        "類別": "螃蟹",
        "名稱": "活凍大沙母蟹",
        "規格": "600g±50g/隻",
        "價格": 899,
        "庫存": 20,
        "圖片": "https://images.unsplash.com/photo-1550747545-c896b5f89ff7",
        "描述": "肉質鮮美，膏黃豐富"
    },
    {
        "類別": "螃蟹",
        "名稱": "萬里蟹",
        "規格": "400g±50g/隻",
        "價格": 699,
        "庫存": 15,
        "圖片": "https://images.unsplash.com/photo-1550747528-cdb45925b3f7",
        "描述": "在地特產，新鮮直送"
    },
    {
        "類別": "貝類",
        "名稱": "生食級大干貝",
        "規格": "10顆/盒",
        "價格": 699,
        "庫存": 30,
        "圖片": "https://images.unsplash.com/photo-1565680018434-b583b12be0d3",
        "描述": "日本北海道進口，鮮甜可口"
    },
    {
        "類別": "貝類",
        "名稱": "活凍白蛤蜊",
        "規格": "500g/包",
        "價格": 199,
        "庫存": 45,
        "圖片": "https://images.unsplash.com/photo-1565980928-261fd63e46f4",
        "描述": "新鮮活凍，保持原味"
    }
]

# 初始化購物車
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# 讀取訂單數據
try:
    with open('data/orders.json', 'r', encoding='utf-8') as f:
        orders = json.load(f)
except:
    orders = []

# 生成訂單號
def generate_order_id():
    return datetime.now().strftime('ORD%Y%m%d%H%M%S')

# 保存訂單
def save_order(order):
    orders.append(order)
    with open('data/orders.json', 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

# 更新商品庫存
def update_product_stock(product_name, quantity):
    for product in products:
        if product["名稱"] == product_name:
            product["庫存"] -= quantity
            break
    with open('data/products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

# 自定義CSS
st.markdown("""
    <style>
    .main {
        padding: 0 !important;
    }
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        height: 2.5em;
        background-color: #FF4B4B;
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        margin: 0.2rem 0;
    }
    .stButton > button:hover {
        background-color: #FF6B6B;
    }
    div[data-testid="column"] {
        padding: 0.5rem !important;
    }
    .element-container {
        margin: 0.5rem 0 !important;
    }
    hr {
        margin: 0.5rem 0 !important;
    }
    .stNumberInput {
        margin-bottom: 0.2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 標題
st.title("🐟 海鮮冷藏專賣店")
st.markdown("### 新鮮直送到府 | 冷藏配送 | 品質保證")

# 顯示購物車
with st.sidebar:
    st.header("🛒 購物車")
    if not st.session_state.cart:
        st.info("購物車是空的")
    else:
        total = 0
        order_items = []  # 用於記錄訂單項目
        
        for item, quantity in st.session_state.cart.items():
            product_info = next((p for p in products if p["名稱"] == item), None)
            
            if product_info:
                subtotal = product_info["價格"] * quantity
                total += subtotal
                order_items.append({
                    "商品名稱": item,
                    "單價": product_info["價格"],
                    "數量": quantity,
                    "小計": subtotal
                })
                
                st.markdown(f"""
                    **{item}** x {quantity}  
                    單價: NT$ {product_info["價格"]}  
                    小計: NT$ {subtotal}
                """)
                
                if st.button(f"❌ 移除 {item}", key=f"del_{item}"):
                    del st.session_state.cart[item]
                    st.rerun()
                st.markdown("---")
        
        st.markdown(f"### 商品總計: NT$ {total}")
        shipping_fee = 0 if total >= 3000 else 150
        st.markdown(f"### 運費: NT$ {shipping_fee}")
        final_total = total + shipping_fee
        st.markdown(f"### 應付金額: NT$ {final_total}")
        st.markdown("*滿3000元免運費*")
        
        # 結帳表單
        with st.form("checkout_form"):
            st.subheader("填寫訂購資料")
            customer_name = st.text_input("姓名")
            phone = st.text_input("電話")
            
            # 取貨方式選擇
            delivery_method = st.radio(
                "取貨方式",
                ["宅配到府", "市場取貨"],
                horizontal=True
            )
            
            if delivery_method == "宅配到府":
                address = st.text_input("配送地址")
                pickup_location = ""
            else:
                pickup_location = st.selectbox(
                    "選擇取貨地點",
                    [
                        "南門市場",
                        "東門市場",
                        "迪化街市場",
                        "建成市場",
                        "中山市場",
                        "松山市場",
                        "龍山寺",
                        "行天宮",
                        "保安宮",
                        "松山慈祐宮"
                    ]
                )
                address = ""
            
            if st.form_submit_button("💳 確認結帳"):
                if not (customer_name and phone and (address or pickup_location)):
                    st.error("請填寫完整的訂購資料")
                else:
                    # 創建訂單
                    order = {
                        "訂單號": generate_order_id(),
                        "日期": datetime.now().strftime("%Y-%m-%d"),
                        "客戶名稱": customer_name,
                        "電話": phone,
                        "地址": address,
                        "取貨地點": pickup_location,
                        "取貨方式": delivery_method,
                        "商品": order_items,
                        "運費": shipping_fee,
                        "總金額": final_total,
                        "狀態": "待處理"
                    }
                    
                    # 更新庫存
                    for item in order_items:
                        update_product_stock(item["商品名稱"], item["數量"])
                    
                    # 保存訂單
                    save_order(order)
                    
                    # 清空購物車
                    st.session_state.cart = {}
                    st.success("訂單已送出！我們會盡快為您出貨！")
                    st.rerun()

# 商品分類選擇
categories = ["全部"] + sorted(list(set(p["類別"] for p in products)))
selected_category = st.selectbox("選擇商品類別", categories, index=0)

# 商品展示
filtered_products = products if selected_category == "全部" else [p for p in products if p["類別"] == selected_category]

st.markdown('<div style="height: 0.5rem"></div>', unsafe_allow_html=True)

for i in range(0, len(filtered_products), 2):
    cols = st.columns([1, 1])
    for j in range(2):
        if i + j < len(filtered_products):
            product = filtered_products[i + j]
            with cols[j]:
                # 使用streamlit-card顯示商品
                has_clicked = card(
                    title=product["名稱"],
                    text=f"""
                    {product['描述']}
                    規格：{product['規格']}
                    庫存：{product['庫存']} 件
                    價格：NT$ {product['價格']}
                    """,
                    image=product["圖片"],
                    key=f"card_{product['名稱']}"
                )
                
                # 加入購物車區域
                col1, col2 = st.columns([1, 1])
                with col1:
                    quantity = st.number_input(
                        "購買數量",
                        min_value=1,
                        max_value=product["庫存"],
                        value=1,
                        key=f"qty_{product['名稱']}"
                    )
                with col2:
                    if st.button("🛒 加入購物車", key=f"add_{product['名稱']}"):
                        if product["名稱"] in st.session_state.cart:
                            st.session_state.cart[product["名稱"]] += quantity
                        else:
                            st.session_state.cart[product["名稱"]] = quantity
                        st.success("已加入購物車！")
                st.markdown("---")
