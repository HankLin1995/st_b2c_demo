# 将前端与FastAPI集成的步骤

## 已完成的工作

1. 创建了`api.js`文件，集中管理所有与FastAPI后端的通信
2. 修改了`index.html`和`checkout.html`中的script标签为模块类型
3. 在`checkout.js`中集成了API接口，实现了订单提交功能

## 需要完成的工作

### 1. 修改script.js中的产品加载逻辑

```javascript
// 在文件顶部添加导入语句
import { getProducts, getProductsByCategory, submitOrder } from './api.js';

// 加載產品
async function loadProducts() {
    try {
        // 使用API获取产品数据
        products = await getProducts();
        renderProducts(products);
    } catch (error) {
        console.error('加载产品失败:', error);
        // 如果API请求失败，使用本地数据作为备份
        products = productsData;
        renderProducts(products);
    }
}

// 根據分類過濾產品
async function filterProductsByCategory(category) {
    try {
        if (category === 'all') {
            // 如果是"全部"分类，获取所有产品
            products = await getProducts();
        } else {
            // 否则获取特定分类的产品
            products = await getProductsByCategory(category);
        }
        renderProducts(products);
    } catch (error) {
        console.error('过滤产品失败:', error);
        // 如果API请求失败，使用本地数据过滤
        if (category === 'all') {
            renderProducts(productsData);
        } else {
            const filteredProducts = productsData.filter(product => product.category === category);
            renderProducts(filteredProducts);
        }
    }
}
```

## FastAPI后端实现建议

### 1. 创建基本的FastAPI应用

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

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
    sale: Optional[bool] = False
    originalPrice: Optional[float] = None

# 订单项目模型
class OrderItem(BaseModel):
    productId: int
    name: str
    price: float
    quantity: int
    sale: Optional[bool] = False
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
        "name": "鮮嫩牛肉",
        "description": "頂級牛肉，鮮嫩多汁",
        "price": 320,
        "image": "https://images.unsplash.com/photo-1603048297172-c92544798d5e",
        "category": "meat",
        "sale": True,
        "originalPrice": 380
    },
    # ... 添加更多产品
]

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
    # 这里应该添加订单处理逻辑，如保存到数据库
    # 简化示例，只返回成功消息
    return {"message": "Order created successfully", "orderId": "ORD12345"}

# 启动服务器
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

### 2. 数据库集成

对于生产环境，建议使用数据库存储产品和订单信息。可以使用SQLAlchemy与FastAPI集成：

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./seafood_shop.db"
# 生产环境可以使用PostgreSQL或MySQL
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. 部署建议

1. **开发环境**：使用Uvicorn的内置服务器
   ```
   uvicorn main:app --reload
   ```

2. **生产环境**：使用Gunicorn作为WSGI服务器，Uvicorn作为worker
   ```
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

3. **容器化**：使用Docker部署
   ```dockerfile
   FROM python:3.9
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

4. **反向代理**：在生产环境中，建议使用Nginx作为反向代理

### 4. 安全性建议

1. 实现适当的身份验证和授权机制
2. 限制CORS来源为您的前端域名
3. 使用HTTPS加密通信
4. 实现速率限制以防止DDoS攻击
5. 验证和清理所有用户输入

## 测试API

使用Postman或FastAPI的自动生成的Swagger文档（访问 `/docs` 路径）来测试API端点。
