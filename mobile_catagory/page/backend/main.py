from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime

app = FastAPI(title="濠鮮嚴選API")

# 启用CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 产品模型
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image: str
    category: str
    onSale: Optional[bool] = False
    originalPrice: Optional[float] = None

# 订单项目模型
class OrderItem(BaseModel):
    productId: int
    name: str
    price: float
    quantity: int
    onSale: Optional[bool] = False
    originalPrice: Optional[float] = None

# 订单模型
class Order(BaseModel):
    items: List[OrderItem]
    total: float
    customerName: str
    phone: str
    email: str
    address: str
    paymentMethod: str
    notes: Optional[str] = None
    orderDate: str

# 示例产品数据
products = [
    {
        "id": 1,
        "name": "紐西蘭牛排",
        "price": 499,
        "originalPrice": 599,
        "onSale": True,
        "image": "https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "紐西蘭頂級草飼牛排",
        "category": "meat"
    },
    {
        "id": 2,
        "name": "松阪豬",
        "price": 359,
        "image": "https://images.unsplash.com/photo-1602470520998-f4a52199a3d6?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "日本進口松阪豬，油花均勻",
        "category": "meat"
    },
    {
        "id": 3,
        "name": "去骨雞腿",
        "price": 189,
        "image": "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "新鮮去骨雞腿，真空包裝",
        "category": "meat"
    },
    {
        "id": 4,
        "name": "急凍生蝦",
        "price": 399,
        "image": "https://images.unsplash.com/photo-1623855244183-52fd8d3ce2f7?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "嚴選深海大蝦，急速冷凍保鮮",
        "category": "shrimp"
    },
    {
        "id": 5,
        "name": "鮭魚片",
        "price": 299,
        "image": "https://images.unsplash.com/photo-1485921325833-c519f76c4927?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "挪威進口鮭魚，真空包裝",
        "category": "fish"
    },
    {
        "id": 6,
        "name": "花枝片",
        "price": 259,
        "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "新鮮花枝，切片即食",
        "category": "fish"
    },
    {
        "id": 7,
        "name": "鱈魚排",
        "price": 329,
        "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "深海鱈魚，肉質鮮嫩",
        "category": "fish"
    },
    {
        "id": 8,
        "name": "生蠔",
        "price": 499,
        "originalPrice": 599,
        "onSale": True,
        "image": "https://images.unsplash.com/photo-1498579687545-d5a4fffb0a9e?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "新鮮生蠔，海洋的滋味",
        "category": "shellfish"
    },
    {
        "id": 9,
        "name": "扇貝",
        "price": 459,
        "image": "https://images.unsplash.com/photo-1569494315581-13efc7e67d1e?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "北海道扇貝，肉質飽滿",
        "category": "shellfish"
    },
    {
        "id": 10,
        "name": "白蝦",
        "price": 359,
        "image": "https://images.unsplash.com/photo-1559737558-2f5a35f4523b?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "台灣白蝦，鮮甜可口",
        "category": "shrimp"
    },
    {
        "id": 11,
        "name": "龍蝦",
        "price": 1299,
        "originalPrice": 1499,
        "onSale": True,
        "image": "https://images.unsplash.com/photo-1550747545-c896b5f89ff7?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "波士頓龍蝦，肉質鮮美",
        "category": "shrimp"
    },
    {
        "id": 12,
        "name": "帝王蟹",
        "price": 1599,
        "image": "https://images.unsplash.com/photo-1559737706-1f3b1d657d3c?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "阿拉斯加帝王蟹，鮮甜多汁",
        "category": "shellfish"
    }
]

# 存储订单的字典
orders = {}

# 路由：获取所有产品
@app.get("/products", response_model=List[Product])
async def get_products():
    return products

# 路由：按类别获取产品
@app.get("/products/category/{category}", response_model=List[Product])
async def get_products_by_category(category: str):
    if category == "all":
        return products
    
    filtered_products = [p for p in products if p["category"] == category]
    return filtered_products

# 路由：获取单个产品
@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# 路由：提交订单
@app.post("/orders", response_model=dict)
async def create_order(order: Order):
    # 生成唯一订单ID
    order_id = str(uuid.uuid4())
    
    # 保存订单
    orders[order_id] = order.dict()
    
    # 添加订单ID和状态
    orders[order_id]["id"] = order_id
    orders[order_id]["status"] = "pending"
    orders[order_id]["createdAt"] = datetime.now().isoformat()
    
    return {
        "message": "Order created successfully", 
        "orderId": order_id,
        "status": "pending"
    }

# 路由：获取订单状态
@app.get("/orders/{order_id}", response_model=dict)
async def get_order(order_id: str):
    if order_id not in orders:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return orders[order_id]

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 启动时的消息
@app.on_event("startup")
async def startup_event():
    print("濠鮮嚴選API已启动")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
