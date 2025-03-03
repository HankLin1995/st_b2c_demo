// 產品資料
const products = [
    {
        "id": 1,
        "name": "紐西蘭牛排",
        "price": 499,
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
        "image": "https://images.unsplash.com/photo-1614377284368-a6d4f911edc7?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "新鮮生蠔，海洋的滋味",
        "category": "shellfish"
    },
    {
        "id": 9,
        "name": "扇貝",
        "price": 459,
        "image": "https://images.unsplash.com/photo-1565280654386-36c3c0e9a7ee?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "北海道扇貝，肉質飽滿",
        "category": "shellfish"
    },
    {
        "id": 10,
        "name": "白蝦",
        "price": 359,
        "image": "https://images.unsplash.com/photo-1565280654386-36c3c0e9a7ee?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
        "description": "台灣白蝦，鮮甜可口",
        "category": "shrimp"
    }
];

// 購物車資料
let cart = [];

// 當前選中的分類
let currentCategory = 'all';

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
document.addEventListener('DOMContentLoaded', function() {
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
    
    // 初始化頁面
    renderProducts();
    updateCartDisplay();
    
    // 添加清空購物車按鈕事件
    const clearCartBtn = document.getElementById('clear-cart-btn');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', clearCart);
    }
    
    // 添加分類標籤事件
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            filterProductsByCategory(category);
            
            // 更新活動標籤
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

// 初始化分類標籤
function initTabs() {
    tabButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // 移除所有標籤的active類
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // 添加當前標籤的active類
            this.classList.add('active');
            
            // 更新當前分類
            currentCategory = this.getAttribute('data-category');
            
            // 重新渲染產品列表
            renderProducts();
        });
    });
}

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
            <img src="${product.image}" alt="${product.name}" class="product-image" onload="this.style.opacity='1'" onerror="this.src='https://via.placeholder.com/300x150?text=圖片載入失敗'; this.style.opacity='1';">
            <div class="product-info">
                <h3 class="product-name">📌${product.name}</h3>
                <p class="product-description">${product.description}</p>
                <p class="product-price">NT$ ${product.price}</p>
                <button class="add-to-cart-btn" data-id="${product.id}">🉑加入購物車</button>
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
                <img src="${item.image}" alt="${item.name}" onerror="this.src='https://via.placeholder.com/50x50'">
                <div class="cart-item-details">
                    <h3>${item.name}</h3>
                    <p>價格: $${item.price}</p>
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
