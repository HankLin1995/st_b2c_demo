// 全局變量
let cart = [];
let checkoutItemsContainer;
let checkoutTotalElement;
let toastElement;
let checkoutForm;

// 导入API函数
import { submitOrder } from './api.js';

// 頁面載入時執行
document.addEventListener('DOMContentLoaded', function() {
    // 獲取DOM元素
    checkoutItemsContainer = document.getElementById('checkout-items');
    checkoutTotalElement = document.getElementById('checkout-total');
    toastElement = document.getElementById('toast');
    checkoutForm = document.getElementById('checkout-form');
    
    // 從本地存儲加載購物車
    loadCart();
    
    // 顯示結帳項目
    displayCheckoutItems();
    
    // 添加表單提交事件監聽器
    checkoutForm.addEventListener('submit', handleCheckout);
});

// 從本地存儲加載購物車
function loadCart() {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
        try {
            cart = JSON.parse(savedCart);
        } catch (e) {
            cart = [];
            console.error('購物車數據解析錯誤', e);
        }
    }
}

// 顯示結帳項目
function displayCheckoutItems() {
    // 清空結帳項目容器
    checkoutItemsContainer.innerHTML = '';
    
    // 如果購物車為空，重定向回首頁
    if (cart.length === 0) {
        showToast('購物車是空的，請先選購商品');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
        return;
    }
    
    // 計算總價
    let total = 0;
    
    // 為每個結帳項目創建HTML
    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        
        const checkoutItemElement = document.createElement('div');
        checkoutItemElement.className = 'checkout-item';
        
        checkoutItemElement.innerHTML = `
            <div class="checkout-item-details">
                <div class="checkout-item-name">${item.name}</div>
                <div class="checkout-item-price">單價: ${item.price} 元</div>
                <div class="checkout-quantity-controls">
                    <button class="quantity-btn minus-btn" data-index="${index}">-</button>
                    <span class="quantity">${item.quantity}</span>
                    <button class="quantity-btn plus-btn" data-index="${index}">+</button>
                </div>
            </div>
            <div class="checkout-item-total">${itemTotal} 元</div>
            <button class="remove-item-btn" data-index="${index}">×</button>
        `;
        
        checkoutItemsContainer.appendChild(checkoutItemElement);
    });
    
    // 更新總價顯示
    checkoutTotalElement.textContent = total;
    
    // 添加數量控制按鈕事件
    document.querySelectorAll('.minus-btn').forEach(button => {
        button.addEventListener('click', decreaseQuantity);
    });
    
    document.querySelectorAll('.plus-btn').forEach(button => {
        button.addEventListener('click', increaseQuantity);
    });
    
    // 添加移除按鈕事件
    document.querySelectorAll('.remove-item-btn').forEach(button => {
        button.addEventListener('click', removeItem);
    });
}

// 減少數量
function decreaseQuantity(event) {
    const index = parseInt(event.target.getAttribute('data-index'));
    if (cart[index].quantity > 1) {
        cart[index].quantity -= 1;
        saveCart();
        displayCheckoutItems();
    } else {
        removeItem(event);
    }
}

// 增加數量
function increaseQuantity(event) {
    const index = parseInt(event.target.getAttribute('data-index'));
    cart[index].quantity += 1;
    saveCart();
    displayCheckoutItems();
}

// 移除項目
function removeItem(event) {
    const index = parseInt(event.target.getAttribute('data-index'));
    cart.splice(index, 1);
    saveCart();
    
    if (cart.length === 0) {
        showToast('購物車已清空，返回首頁');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
    } else {
        displayCheckoutItems();
    }
}

// 保存購物車
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

// 處理結帳提交
function handleCheckout(event) {
    event.preventDefault();
    
    // 獲取表單數據
    const formData = new FormData(checkoutForm);
    const orderData = {
        customer: {
            name: formData.get('name'),
            phone: formData.get('phone'),
            email: formData.get('email'),
            address: formData.get('address')
        },
        payment: formData.get('payment'),
        notes: formData.get('notes'),
        items: cart,
        total: cart.reduce((total, item) => total + (item.price * item.quantity), 0),
        orderDate: new Date().toISOString()
    };
    
    // 使用新的API接口提交訂單
    submitOrder(orderData).then(() => {
        console.log('訂單提交成功');
        
        // 清空購物車
        localStorage.removeItem('cart');
        
        // 顯示成功消息
        showToast('訂單已成功提交！我們將盡快處理您的訂單');
        
        // 延遲後重定向到首頁
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 3000);
    }).catch((error) => {
        console.error('訂單提交失敗', error);
    });
}

// 顯示提示消息
function showToast(message) {
    toastElement.textContent = message;
    toastElement.className = 'toast show';
    setTimeout(function() {
        toastElement.className = toastElement.className.replace('show', '');
    }, 3000);
}
