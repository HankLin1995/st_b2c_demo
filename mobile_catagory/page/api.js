// api.js - 处理与FastAPI后端的所有通信

// API基础URL - 根据您的FastAPI部署情况修改
const API_BASE_URL = 'http://localhost:8000';

// 通用的fetch函数，处理错误和响应
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `API请求失败: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API请求错误:', error);
        showToast(error.message || '连接服务器失败，请稍后再试');
        throw error;
    }
}

// 获取所有产品
async function getProducts() {
    return await fetchAPI('/products');
}

// 获取特定类别的产品
async function getProductsByCategory(category) {
    return await fetchAPI(`/products/category/${category}`);
}

// 获取产品详情
async function getProductDetails(productId) {
    return await fetchAPI(`/products/${productId}`);
}

// 提交订单
async function submitOrder(orderData) {
    return await fetchAPI('/orders', {
        method: 'POST',
        body: JSON.stringify(orderData)
    });
}

// 获取订单状态
async function getOrderStatus(orderId) {
    return await fetchAPI(`/orders/${orderId}`);
}

// 用户登录
async function login(credentials) {
    return await fetchAPI('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials)
    });
}

// 用户注册
async function register(userData) {
    return await fetchAPI('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData)
    });
}

// 导出所有API函数
export {
    getProducts,
    getProductsByCategory,
    getProductDetails,
    submitOrder,
    getOrderStatus,
    login,
    register
};
