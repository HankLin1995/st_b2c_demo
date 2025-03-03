# 濠鮮嚴選 API 後端

這是濠鮮嚴選電商平台的FastAPI後端服務。

## 功能

- 產品API：獲取所有產品、按類別獲取產品、獲取單個產品詳情
- 訂單API：提交訂單、查詢訂單狀態
- CORS支持：允許前端應用訪問API
- Docker支持：使用Docker容器化部署

## 技術棧

- FastAPI：高性能Python Web框架
- Pydantic：數據驗證和設置管理
- Uvicorn：ASGI服務器
- Docker：容器化部署

## 快速開始

### 使用Docker運行

1. 確保已安裝Docker和Docker Compose

2. 在backend目錄下運行：

```bash
docker-compose up -d
```

3. API將在 http://localhost:8000 上運行

4. 訪問API文檔：http://localhost:8000/docs

### 不使用Docker運行

1. 確保已安裝Python 3.9+

2. 安裝依賴：

```bash
pip install -r requirements.txt
```

3. 運行服務：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API端點

### 產品API

- `GET /products` - 獲取所有產品
- `GET /products/category/{category}` - 按類別獲取產品
- `GET /products/{product_id}` - 獲取單個產品詳情

### 訂單API

- `POST /orders` - 提交新訂單
- `GET /orders/{order_id}` - 獲取訂單狀態

### 其他端點

- `GET /health` - 健康檢查

## 開發

### 添加新端點

在`main.py`中添加新的路由函數：

```python
@app.get("/your-endpoint")
async def your_function():
    return {"message": "Your response"}
```

### 添加新模型

在`main.py`中使用Pydantic定義新的數據模型：

```python
class YourModel(BaseModel):
    field1: str
    field2: int
    optional_field: Optional[bool] = False
```
