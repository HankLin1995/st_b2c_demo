import json
import random
from datetime import datetime, timedelta
import os

# 確保數據目錄存在
if not os.path.exists('data'):
    os.makedirs('data')

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

# 客戶名稱列表
customer_names = [
    "王大明", "李小華", "張美玲", "陳志偉", "林雅婷",
    "吳建志", "黃淑芬", "劉俊傑", "周雅琪", "蔡文心"
]

# 地址列表
addresses = [
    "台北市中山區中山北路123號",
    "台北市大安區忠孝東路456號",
    "新北市板橋區縣民大道789號",
    "新北市中和區中和路234號",
    "桃園市中壢區中央西路567號",
    "台中市西屯區台灣大道890號",
    "台中市北屯區崇德路321號",
    "高雄市前鎮區中山路654號",
    "高雄市鳳山區光復路987號",
    "台南市東區長榮路432號"
]

# 生成訂單
orders = []
for i in range(20):
    # 隨機選擇取貨方式
    delivery_method = random.choice(["宅配到府", "市場取貨"])
    
    # 根據取貨方式設置地址或取貨地點
    if delivery_method == "宅配到府":
        address = f"台北市{random.choice(['大安區', '中正區', '信義區'])}{''.join(random.choices('一二三四五六七八九十', k=1))}街{random.randint(1, 100)}號"
        pickup_location = ""
    else:
        address = ""
        pickup_location = random.choice([
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
        ])

    # 隨機選擇1-4個商品
    order_items = []
    total = 0
    selected_products = random.sample(products, random.randint(1, 4))
    
    for product in selected_products:
        quantity = random.randint(1, 3)
        subtotal = product["價格"] * quantity
        total += subtotal
        
        order_items.append({
            "商品名稱": product["名稱"],
            "單價": product["價格"],
            "數量": quantity,
            "小計": subtotal
        })
    
    # 計算運費
    shipping_fee = 0 if total >= 3000 else 150
    
    # 創建訂單
    order = {
        "訂單號": f"ORD{(i+1):04d}",
        "日期": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
        "客戶名稱": f"{random.choice(['王', '李', '張', '劉', '陳'])}{random.choice(['小明', '大華', '志明', '俊傑', '淑芬', '美玲'])}",
        "電話": f"09{random.randint(10000000, 99999999)}",
        "地址": address,
        "取貨地點": pickup_location,
        "取貨方式": delivery_method,
        "商品": order_items,
        "運費": shipping_fee,
        "總金額": total + shipping_fee,
        "狀態": random.choice(["待處理", "處理中", "已出貨", "已完成"])
    }
    
    orders.append(order)

# 保存商品數據
with open('data/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

# 保存訂單數據
with open('data/orders.json', 'w', encoding='utf-8') as f:
    json.dump(orders, f, ensure_ascii=False, indent=2)

print(f"已生成 {len(products)} 個商品和 {len(orders)} 個訂單的模擬數據")
