// 在文件顶部添加导入语句
import { getProducts, getProductsByCategory, submitOrder } from './api.js';

// 購物車資料
let cart = [];

// 當前選中的分類
let currentCategory = 'all';

// 產品資料 - 移除硬编码数据，改为从API获取
let products = [];

// DOM 元素
let productContainer;
let cartContainer;
let emptyCartMessage;
let cartSummary;
let totalAmountElement;
let toastElement;
let tabButtons;
let floatingCartCount;

// 頁面載入時執行
document.addEventListener('DOMContentLoaded', async function() {
    // 獲取DOM元素
    productContainer = document.getElementById('product-container');
    cartContainer = document.getElementById('cart-container');
    emptyCartMessage = document.getElementById('empty-cart-message');
    cartSummary = document.getElementById('cart-summary');
    totalAmountElement = document.getElementById('cart-total');
    toastElement = document.getElementById('toast');
    tabButtons = document.querySelectorAll('.tab-btn');
    floatingCartCount = document.getElementById('floating-cart-count');
    
    // 從本地存儲加載購物車
    loadCart();
    
    // 更新購物車顯示
    updateCartDisplay();
    
    // 顯示加載狀態
    productContainer.innerHTML = '<div class="loading">正在加載產品...</div>';
    
    try {
        // 從API獲取產品資料
        products = await getProducts();
        
        // 渲染產品
        renderProducts();
    } catch (error) {
        console.error('加載產品失敗:', error);
        productContainer.innerHTML = '<div class="error">加載產品失敗，請刷新頁面重試</div>';
        showToast('加載產品失敗，請檢查網絡連接');
    }
    
    // 添加清空購物車按鈕事件
    const clearCartBtn = document.getElementById('clear-cart-btn');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', clearCart);
    }
    
    // 添加分類標籤點擊事件
    tabButtons.forEach(button => {
        button.addEventListener('click', async function() {
            // 移除所有標籤的活動狀態
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // 設置當前標籤為活動狀態
            this.classList.add('active');
            
            // 獲取分類值
            currentCategory = this.getAttribute('data-category');
            
            try {
                // 使用API获取分类产品
                if (currentCategory === 'all') {
                    products = await getProducts();
                } else {
                    products = await getProductsByCategory(currentCategory);
                }
                
                // 渲染產品
                renderProducts();
            } catch (error) {
                console.error('获取分类产品失败:', error);
                // 显示错误提示
                showToast('获取产品数据失败，请稍后再试');
            }
        });
    });
});

// 渲染產品列表
function renderProducts() {
    productContainer.innerHTML = '';
    
    // 根據當前分類過濾產品
    const filteredProducts = currentCategory === 'all' 
        ? products 
        : products.filter(product => product.category === currentCategory);
    
    // 如果沒有產品
    if (filteredProducts.length === 0) {
        const noProducts = document.createElement('p');
        noProducts.className = 'info-message';
        noProducts.textContent = '此分類暫無商品';
        productContainer.appendChild(noProducts);
        return;
    }
    
    filteredProducts.forEach(function(product) {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        
        productCard.innerHTML = `
            <img src="${product.image}" alt="${product.name}" class="product-image" onload="this.style.opacity='1'" onerror="this.onerror=null; this.src='https://via.placeholder.com/300x150?text=圖片載入失敗'; this.style.opacity='1';">
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-description">${product.description}</p>
                <p class="product-price ${product.onSale ? 'sale' : ''}">NT$ ${product.price}</p>
                ${product.onSale ? `<p class="product-original-price">原價 NT$ ${product.originalPrice}</p>` : ''}
                ${product.onSale ? `<p class="product-sale-tag">特價</p>` : ''}
                <button class="add-to-cart-btn" data-id="${product.id}">加入購物車</button>
            </div>
        `;
        
        productContainer.appendChild(productCard);
    });
    
    // 添加加入購物車按鈕事件
    const addButtons = document.querySelectorAll('.add-to-cart-btn');
    addButtons.forEach(function(button) {
        button.addEventListener('click', addToCart);
    });
}

// 添加商品到購物車
function addToCart(event) {
    const productId = parseInt(event.target.getAttribute('data-id'));
    const product = products.find(p => p.id === productId);
    
    if (!product) {
        showToast('商品不存在');
        return;
    }
    
    // 檢查購物車中是否已有該商品
    const existingItemIndex = cart.findIndex(item => item.id === productId);
    
    if (existingItemIndex !== -1) {
        // 如果已存在，增加數量
        cart[existingItemIndex].quantity += 1;
        showToast(`已增加 ${product.name} 的數量`);
    } else {
        // 如果不存在，添加新項目
        cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            image: product.image,
            onSale: product.onSale || false,
            originalPrice: product.originalPrice,
            quantity: 1
        });
        showToast(`已添加 ${product.name} 到購物車`);
    }
    
    // 保存購物車到本地存儲
    saveCart();
    
    // 更新購物車顯示
    updateCartDisplay();
    
    // 添加按鈕動畫效果
    const button = event.target;
    button.classList.add('added');
    setTimeout(() => {
        button.classList.remove('added');
    }, 500);
}

// 從購物車中移除商品
function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartDisplay();
}

// 清空購物車
function clearCart() {
    cart = [];
    saveCart();
    updateCartDisplay();
}

// 更新購物車顯示
function updateCartDisplay() {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');
    const floatingCartCount = document.getElementById('floating-cart-count');
    
    // 清空購物車項目容器
    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = '';
    }
    
    // 獲取購物車數據
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    
    // 更新懸浮購物車計數
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    if (floatingCartCount) {
        floatingCartCount.textContent = totalItems;
        
        // 如果購物車為空，隱藏計數器
        if (totalItems === 0) {
            floatingCartCount.style.display = 'none';
        } else {
            floatingCartCount.style.display = 'flex';
        }
    }
    
    // 如果購物車為空，顯示空購物車消息
    if (cart.length === 0) {
        if (emptyCartMessage) {
            emptyCartMessage.style.display = 'block';
        }
        if (cartTotalElement) {
            cartTotalElement.textContent = '0';
        }
        return;
    }
    
    // 隱藏空購物車消息
    if (emptyCartMessage) {
        emptyCartMessage.style.display = 'none';
    }
    
    // 計算總價
    let total = 0;
    
    // 為每個購物車項目創建HTML
    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        if (cartItemsContainer) {
            const cartItemElement = document.createElement('div');
            cartItemElement.className = 'cart-item';
            
            cartItemElement.innerHTML = `
                <img src="${item.image}" alt="${item.name}" onerror="this.onerror=null; this.src='https://via.placeholder.com/50x50?text=無圖片'">
                <div class="cart-item-details">
                    <h3>${item.name}</h3>
                    <p class="cart-item-price ${item.onSale ? 'sale' : ''}">價格: $${item.price}</p>
                    ${item.onSale ? `<p class="cart-item-original-price">原價: $${item.originalPrice}</p>` : ''}
                    <div class="quantity-controls">
                        <button class="quantity-btn minus-btn" data-index="${index}">-</button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="quantity-btn plus-btn" data-index="${index}">+</button>
                    </div>
                </div>
                <p class="item-total">$${itemTotal}</p>
                <button class="remove-btn" data-index="${index}">×</button>
            `;
            
            cartItemsContainer.appendChild(cartItemElement);
        }
    });
    
    // 更新總價顯示
    if (cartTotalElement) {
        cartTotalElement.textContent = total;
    }
    
    // 為數量按鈕添加事件監聽器
    if (cartItemsContainer) {
        document.querySelectorAll('.minus-btn').forEach(button => {
            button.addEventListener('click', decreaseQuantity);
        });
        
        document.querySelectorAll('.plus-btn').forEach(button => {
            button.addEventListener('click', increaseQuantity);
        });
        
        // 為移除按鈕添加事件監聽器
        document.querySelectorAll('.remove-btn').forEach(button => {
            button.addEventListener('click', removeFromCart);
        });
    }
}

// 保存購物車到本地存儲
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

// 從本地存儲加載購物車
function loadCart() {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
        try {
            cart = JSON.parse(savedCart);
        } catch (e) {
            cart = [];
        }
    }
}

// 顯示通知
function showToast(message) {
    toastElement.textContent = message;
    toastElement.className = 'toast show';
    
    // 3秒後隱藏通知
    setTimeout(function() {
        toastElement.className = toastElement.className.replace('show', '');
    }, 3000);
}

// 減少購物車商品數量
function decreaseQuantity(event) {
    const index = parseInt(event.target.getAttribute('data-index'));
    cart[index].quantity -= 1;
    if (cart[index].quantity <= 0) {
        cart.splice(index, 1);
    }
    saveCart();
    updateCartDisplay();
}

// 增加購物車商品數量
function increaseQuantity(event) {
    const index = parseInt(event.target.getAttribute('data-index'));
    cart[index].quantity += 1;
    saveCart();
    updateCartDisplay();
}

// 分類產品
function filterProductsByCategory(category) {
    currentCategory = category;
    renderProducts();
}
