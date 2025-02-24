import streamlit as st
from streamlit_card import card
import sqlite3
import os

# 設置頁面配置
st.set_page_config(page_title="購物車清單", layout="wide")

# 初始化數據庫
def init_db():
    # 確保數據目錄存在
    data_dir = os.path.join('app', 'data')
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'shopping_cart.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart
        (product_id INTEGER PRIMARY KEY,
         name TEXT,
         price REAL,
         quantity INTEGER)
    ''')
    conn.commit()
    conn.close()

# 添加商品到購物車
def add_to_cart(product):
    db_path = os.path.join('app', 'data', 'shopping_cart.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # 檢查商品是否已在購物車中
        c.execute('SELECT quantity FROM cart WHERE product_id = ?', (product['id'],))
        result = c.fetchone()
        
        if result:
            # 更新數量
            new_quantity = result[0] + 1
            c.execute('UPDATE cart SET quantity = ? WHERE product_id = ?', 
                     (new_quantity, product['id']))
        else:
            # 新增商品
            c.execute('''INSERT INTO cart 
                        (product_id, name, price, quantity) 
                        VALUES (?, ?, ?, 1)''',
                     (product['id'], product['name'], product['price']))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"數據庫錯誤: {e}")
        return False
    finally:
        conn.close()

# 從購物車中刪除商品
def remove_from_cart(product_id):
    db_path = os.path.join('app', 'data', 'shopping_cart.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM cart WHERE product_id = ?', (product_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"數據庫錯誤: {e}")
        return False
    finally:
        conn.close()

# 清空購物車
def clear_cart():
    db_path = os.path.join('app', 'data', 'shopping_cart.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM cart')
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"數據庫錯誤: {e}")
        return False
    finally:
        conn.close()

# 獲取購物車內容
def get_cart_items():
    db_path = os.path.join('app', 'data', 'shopping_cart.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('SELECT product_id, name, price, quantity FROM cart')
        items = c.fetchall()
        return items
    except sqlite3.Error as e:
        st.error(f"數據庫錯誤: {e}")
        return []
    finally:
        conn.close()

# 初始化數據庫
init_db()

# 商品資料
products = [
    {
        "id": 1,
        "name": "紐西蘭牛排",
        "price": 499,
        "image": "https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "紐西蘭頂級草飼牛排"
    },
    {
        "id": 2,
        "name": "松阪豬",
        "price": 359,
        "image": "https://images.unsplash.com/photo-1602470520998-f4a52199a3d6?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "日本進口松阪豬，油花均勻"
    },
    {
        "id": 3,
        "name": "去骨雞腿",
        "price": 189,
        "image": "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "新鮮去骨雞腿，真空包裝"
    },
    {
        "id": 4,
        "name": "急凍生蝦",
        "price": 399,
        "image": "https://images.unsplash.com/photo-1623855244183-52fd8d3ce2f7?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "嚴選深海大蝦，急速冷凍保鮮"
    },
    {
        "id": 5,
        "name": "鮭魚片",
        "price": 299,
        "image": "https://images.unsplash.com/photo-1485921325833-c519f76c4927?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "挪威進口鮭魚，真空包裝"
    },
    {
        "id": 6,
        "name": "花枝片",
        "price": 259,
        "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "新鮮花枝，切片即食"
    }
]

# 標題
st.title("🐟 魚老闆嚴選")

# 顯示商品卡片
# st.subheader("🐠商品列表")

# 添加自定義 CSS 來美化卡片
st.markdown("""
<style>
    .stColumn {
        padding: 0.2rem !important;
    }
    div[data-testid="stImage"] img {
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    .product-card {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        margin-bottom: 1rem;
        background-color: white;
    }
    .product-title {
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .product-description {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .product-price {
        color: #e63946;
        font-weight: bold;
        font-size: 1.1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# cols = st.columns(3,border=True)

for idx, product in enumerate(products):
    # with cols[idx % 3]:
    with st.container(border=True):
        # st.markdown('<div class="product-card">', unsafe_allow_html=True)
        
        # 顯示商品圖片
        st.image(product["image"], use_container_width=True)
        st.markdown(f"#### 📌{product['name']}")
        st.write(product["description"])
        st.write(f"NT$ {product['price']}")

        # 顯示商品信息

        # 添加按鈕
        if st.button("🉑加入購物車", key=f"add_{product['id']}",use_container_width=True):
            if add_to_cart(product):
                st.toast(f"已將 {product['name']} 加入購物車！", icon="✅")
        

# 顯示購物車內容
st.divider()
st.subheader("📇購物車內容")

cart_items = get_cart_items()
if not cart_items:
    st.info("購物車是空的，快去選購喜歡的商品吧！")
else:
    # 計算總金額
    total = sum(price * quantity for _, _, price, quantity in cart_items)
    
    # 顯示購物車內容
    for product_id, name, price, quantity in cart_items:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.write(f"{name} × {quantity} = NT$ {price * quantity}")
        with col2:
            if st.button("刪除", key=f"remove_{product_id}"):
                if remove_from_cart(product_id):
                    st.rerun()
    
    st.divider()
    st.markdown(f"### 總金額: NT$ {total}")
    
    # 清空購物車按鈕
    if st.button("清空購物車", type="primary"):
        if clear_cart():
            st.rerun()
