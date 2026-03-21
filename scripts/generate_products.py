#!/usr/bin/env python3
import csv
import json
import os

# Paths
PRODUCTS_DIR = "."
CSV_FILE = "products.csv"
JSON_FILE = "products.json"

# ===== PRODUCT PAGE TEMPLATE =====
PRODUCT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>{name} | Daje Games</title>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts - Quicksand for Daje -->
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- INJECTORS -->
    <script src="https://assets.janishammer.com/js/injector-core.js"></script>
    <script src="https://assets.janishammer.com/js/injector-config.js"></script>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Quicksand', sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            min-height: 100vh;
            padding: 1rem;
        }}
        
        /* Floating Cart Button */
        .cart-floating {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: linear-gradient(135deg, #FFB6C1, #FF99AA);
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            z-index: 1000;
            border: 2px solid rgba(255,255,255,0.3);
        }}
        
        .cart-floating:hover {{
            transform: scale(1.1);
            box-shadow: 0 12px 30px rgba(0,0,0,0.3);
        }}
        
        .cart-floating i {{
            font-size: 1.5rem;
            color: #000;
        }}
        
        .cart-count {{
            position: absolute;
            top: -5px;
            right: -5px;
            background: #D4AF37;
            color: #000;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: bold;
        }}
        
        .product-container {{
            max-width: 1280px;
            margin: 0 auto;
            background: rgba(255,255,255,0.98);
            border-radius: 32px;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
        }}
        
        .product-detail {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            padding: 2rem;
            background: white;
        }}
        
        .product-gallery {{
            position: relative;
        }}
        
        .main-image-container {{
            position: relative;
            cursor: pointer;
            overflow: hidden;
            border-radius: 24px;
            background: #f8f9fa;
            aspect-ratio: 1 / 1;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .main-image {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: transform 0.4s ease;
        }}
        
        .main-image-container:hover .main-image {{
            transform: scale(1.05);
        }}
        
        .zoom-icon {{
            position: absolute;
            bottom: 1rem;
            right: 1rem;
            background: rgba(0,0,0,0.7);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }}
        
        .zoom-icon:hover {{
            background: #D4AF37;
            color: #000;
            transform: scale(1.1);
        }}
        
        .thumbnail-gallery {{
            display: flex;
            gap: 0.75rem;
            margin-top: 1rem;
            overflow-x: auto;
            padding-bottom: 0.5rem;
        }}
        
        .thumbnail {{
            width: 70px;
            height: 70px;
            border-radius: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 3px solid transparent;
            object-fit: cover;
            flex-shrink: 0;
        }}
        
        .thumbnail:hover {{
            transform: translateY(-4px);
            border-color: #D4AF37;
        }}
        
        .thumbnail.active {{
            border-color: #D4AF37;
            box-shadow: 0 4px 12px rgba(212,175,55,0.3);
        }}
        
        .product-info {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .product-category {{
            display: inline-block;
            background: rgba(255,182,193,0.2);
            color: #FFB6C1;
            padding: 0.4rem 1rem;
            border-radius: 40px;
            font-size: 0.85rem;
            font-weight: 600;
            width: fit-content;
        }}
        
        .product-name {{
            font-size: 2rem;
            font-weight: 800;
            color: #000;
            line-height: 1.2;
        }}
        
        .product-brand {{
            font-size: 0.9rem;
            color: #666;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .product-brand i {{
            color: #FFB6C1;
        }}
        
        .product-price {{
            font-size: 2.2rem;
            font-weight: 800;
            color: #D4AF37;
            margin: 0.25rem 0;
        }}
        
        .product-price::before {{
            content: "฿";
            font-size: 1.6rem;
        }}
        
        .stock-status {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 40px;
            font-weight: 600;
            font-size: 0.85rem;
            width: fit-content;
        }}
        
        .stock-status.in-stock {{
            background: rgba(212,175,55,0.1);
            color: #D4AF37;
            border: 1px solid rgba(212,175,55,0.3);
        }}
        
        .stock-status.pre-order {{
            background: rgba(255,152,0,0.1);
            color: #FF9800;
            border: 1px solid rgba(255,152,0,0.3);
        }}
        
        .stock-status.out-stock {{
            background: rgba(244,67,54,0.1);
            color: #F44336;
            border: 1px solid rgba(244,67,54,0.3);
        }}
        
        .features-section h3 {{
            font-size: 1rem;
            color: #000;
            margin-bottom: 0.75rem;
            font-weight: 700;
        }}
        
        .features-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .features-list li {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: #555;
            font-size: 0.85rem;
        }}
        
        .features-list li i {{
            color: #D4AF37;
            font-size: 0.9rem;
            width: 20px;
        }}
        
        .color-options {{
            margin: 0.5rem 0;
        }}
        
        .color-options h3 {{
            font-size: 0.9rem;
            color: #000;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        .color-swatches {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .color-swatch {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 3px solid transparent;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .color-swatch:hover {{
            transform: scale(1.1);
        }}
        
        .color-swatch.selected {{
            border-color: #D4AF37;
            transform: scale(1.1);
            box-shadow: 0 0 0 2px white, 0 0 0 4px #D4AF37;
        }}
        
        .quantity-selector {{
            margin: 0.5rem 0;
        }}
        
        .quantity-selector h3 {{
            font-size: 0.9rem;
            color: #000;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        .quantity-control {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .qty-btn {{
            width: 36px;
            height: 36px;
            border-radius: 12px;
            background: #f0f0f0;
            border: 1px solid #e0e0e0;
            cursor: pointer;
            font-size: 1.2rem;
            font-weight: bold;
            transition: all 0.2s;
        }}
        
        .qty-btn:hover {{
            background: #D4AF37;
            border-color: #D4AF37;
        }}
        
        .quantity-input {{
            width: 60px;
            height: 36px;
            text-align: center;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 0.75rem;
            margin-top: 0.5rem;
        }}
        
        .btn-add-to-cart {{
            flex: 2;
            background: linear-gradient(135deg, #FFB6C1, #FF99AA);
            color: #000;
            border: none;
            padding: 0.8rem;
            border-radius: 60px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}
        
        .btn-add-to-cart:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255,182,193,0.3);
        }}
        
        .btn-wishlist {{
            background: rgba(0,0,0,0.05);
            border: 2px solid #e0e0e0;
            padding: 0.8rem;
            border-radius: 60px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #666;
            aspect-ratio: 1;
        }}
        
        .btn-wishlist:hover {{
            background: rgba(255,182,193,0.1);
            border-color: #FFB6C1;
            color: #FFB6C1;
        }}
        
        .you-may-like {{
            background: #f8f9fa;
            padding: 2rem;
            border-top: 1px solid #e0e0e0;
        }}
        
        .you-may-like h2 {{
            font-size: 1.5rem;
            color: #000;
            margin-bottom: 1.5rem;
            font-weight: 700;
        }}
        
        .slider-track {{
            display: flex;
            gap: 1rem;
            overflow-x: auto;
            scroll-behavior: smooth;
            padding-bottom: 1rem;
        }}
        
        .slider-track::-webkit-scrollbar {{
            height: 6px;
        }}
        
        .slider-track::-webkit-scrollbar-track {{
            background: #e0e0e0;
            border-radius: 10px;
        }}
        
        .slider-track::-webkit-scrollbar-thumb {{
            background: #D4AF37;
            border-radius: 10px;
        }}
        
        .recommend-card {{
            flex: 0 0 calc(25% - 0.75rem);
            min-width: 200px;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            transition: all 0.4s ease;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        
        .recommend-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }}
        
        .recommend-card-image {{
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
        }}
        
        .recommend-card-info {{
            padding: 0.75rem;
        }}
        
        .recommend-card-name {{
            font-size: 0.9rem;
            font-weight: 700;
            color: #000;
            margin-bottom: 0.25rem;
        }}
        
        .recommend-card-price {{
            font-size: 1rem;
            font-weight: 800;
            color: #D4AF37;
        }}
        
        .recommend-card-price::before {{
            content: "฿";
            font-size: 0.8rem;
        }}
        
        .slider-nav {{
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .nav-btn {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: white;
            border: 1px solid #e0e0e0;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .nav-btn:hover {{
            background: #D4AF37;
            border-color: #D4AF37;
        }}
        
        .cart-modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 10001;
            justify-content: center;
            align-items: center;
        }}
        
        .cart-modal.active {{
            display: flex;
        }}
        
        .cart-content {{
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            background: white;
            border-radius: 32px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .cart-header {{
            padding: 1.5rem;
            background: linear-gradient(135deg, #FFB6C1, #FF99AA);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .cart-header h2 {{
            color: #000;
            font-size: 1.3rem;
        }}
        
        .cart-close {{
            font-size: 1.5rem;
            cursor: pointer;
            color: #000;
        }}
        
        .cart-items {{
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
        }}
        
        .cart-item {{
            display: flex;
            gap: 1rem;
            padding: 1rem;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .cart-item-image {{
            width: 70px;
            height: 70px;
            object-fit: cover;
            border-radius: 12px;
        }}
        
        .cart-item-details {{
            flex: 1;
        }}
        
        .cart-item-name {{
            font-weight: 700;
            color: #000;
            margin-bottom: 0.25rem;
        }}
        
        .cart-item-variant {{
            font-size: 0.75rem;
            color: #888;
        }}
        
        .cart-item-price {{
            color: #D4AF37;
            font-weight: 700;
        }}
        
        .cart-item-actions {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .cart-qty-btn {{
            width: 28px;
            height: 28px;
            border-radius: 8px;
            background: #f0f0f0;
            border: none;
            cursor: pointer;
        }}
        
        .cart-item-qty {{
            width: 40px;
            text-align: center;
        }}
        
        .cart-item-remove {{
            color: #F44336;
            cursor: pointer;
            font-size: 1.2rem;
        }}
        
        .cart-summary {{
            padding: 1.5rem;
            background: #f8f9fa;
            border-top: 2px solid #e0e0e0;
        }}
        
        .cart-total {{
            display: flex;
            justify-content: space-between;
            font-size: 1.2rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }}
        
        .btn-quotation {{
            width: 100%;
            background: linear-gradient(135deg, #FFB6C1, #FF99AA);
            color: #000;
            border: none;
            padding: 1rem;
            border-radius: 60px;
            font-weight: 800;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .btn-quotation:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255,182,193,0.3);
        }}
        
        .toast {{
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: #D4AF37;
            color: #000;
            padding: 0.8rem 1.5rem;
            border-radius: 60px;
            font-weight: 600;
            z-index: 10002;
            transition: transform 0.3s;
            white-space: nowrap;
        }}
        
        .toast.show {{
            transform: translateX(-50%) translateY(0);
        }}
        
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            z-index: 10000;
            justify-content: center;
            align-items: center;
        }}
        
        .lightbox.active {{
            display: flex;
        }}
        
        .lightbox-img {{
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
        }}
        
        .lightbox-close {{
            position: absolute;
            top: 20px;
            right: 30px;
            color: white;
            font-size: 40px;
            cursor: pointer;
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 0.5rem; }}
            .product-detail {{ grid-template-columns: 1fr; gap: 1rem; padding: 1rem; }}
            .product-name {{ font-size: 1.5rem; }}
            .product-price {{ font-size: 1.8rem; }}
            .you-may-like {{ padding: 1rem; }}
            .recommend-card {{ flex: 0 0 calc(50% - 0.5rem); }}
            .action-buttons {{ flex-direction: column; }}
            .btn-wishlist {{ aspect-ratio: auto; padding: 0.8rem; }}
            .cart-floating {{ bottom: 1rem; right: 1rem; width: 50px; height: 50px; }}
        }}
        
        @media (max-width: 480px) {{
            .recommend-card {{ flex: 0 0 100%; }}
        }}
    </style>
</head>
<body>
    <div class="cart-floating" id="cartFloating">
        <i class="fas fa-shopping-bag"></i>
        <span class="cart-count" id="cartCount">0</span>
    </div>
    
    <div class="product-container">
        <div class="product-detail">
            <div class="product-gallery">
                <div class="main-image-container" id="mainImageContainer">
                    <img src="{main_image}" alt="{name}" class="main-image" id="mainImage">
                    <div class="zoom-icon" id="zoomIcon">
                        <i class="fas fa-expand"></i>
                    </div>
                </div>
                <div class="thumbnail-gallery" id="thumbnailGallery">
                    {thumbnails}
                </div>
            </div>
            
            <div class="product-info">
                <div>
                    <span class="product-category">Claw Machine</span>
                </div>
                <h1 class="product-name">{name}</h1>
                <div class="product-brand">
                    <i class="fas fa-tag"></i>
                    <span>Daje Games · Premium Edition</span>
                </div>
                <div class="product-price">{price:,}</div>
                <div class="stock-status {stock}" id="stockStatus">
                    <i class="fas fa-check-circle"></i>
                    <span>{stock_text}</span>
                </div>
                
                <div class="features-section">
                    <h3>Key Features</h3>
                    <ul class="features-list">
                        {features_html}
                    </ul>
                </div>
                
                <div class="color-options">
                    <h3>Color Options</h3>
                    <div class="color-swatches">
                        {color_swatches}
                    </div>
                </div>
                
                <div class="quantity-selector">
                    <h3>Quantity</h3>
                    <div class="quantity-control">
                        <button class="qty-btn" onclick="updateQuantity(-1)">-</button>
                        <input type="number" id="quantity" class="quantity-input" value="1" min="1" max="99" readonly>
                        <button class="qty-btn" onclick="updateQuantity(1)">+</button>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn-add-to-cart" onclick="addToCart()">
                        <i class="fas fa-shopping-cart"></i>
                        Add to Cart
                    </button>
                    <button class="btn-wishlist" onclick="toggleWishlist(this)">
                        <i class="far fa-heart"></i>
                    </button>
                </div>
            </div>
        </div>
        
        <div class="you-may-like">
            <h2>✨ You May Also Like</h2>
            <div class="slider-track" id="sliderTrack">
                {recommendations}
            </div>
            <div class="slider-nav">
                <button class="nav-btn" onclick="scrollSlider(-1)"><i class="fas fa-chevron-left"></i></button>
                <button class="nav-btn" onclick="scrollSlider(1)"><i class="fas fa-chevron-right"></i></button>
            </div>
        </div>
    </div>
    
    <!-- CART MODAL -->
    <div id="cartModal" class="cart-modal">
        <div class="cart-content">
            <div class="cart-header">
                <h2><i class="fas fa-shopping-bag"></i> Your Cart</h2>
                <span class="cart-close" onclick="closeCart()">&times;</span>
            </div>
            <div class="cart-items" id="cartItems">
                <div style="text-align: center; padding: 2rem; color: #888;">Your cart is empty</div>
            </div>
            <div class="cart-summary">
                <div class="cart-total">
                    <span>Total</span>
                    <span id="cartTotal">฿0</span>
                </div>
                <button class="btn-quotation" onclick="requestQuotation()">
                    <i class="fas fa-file-invoice"></i> Get Your Quotation
                </button>
            </div>
        </div>
    </div>
    
    <!-- QUOTATION MODAL -->
    <div id="quotationModal" class="cart-modal">
        <div class="cart-content" style="max-width: 500px;">
            <div class="cart-header">
                <h2><i class="fas fa-check-circle"></i> Quotation Request</h2>
                <span class="cart-close" onclick="closeQuotationModal()">&times;</span>
            </div>
            <div style="padding: 2rem; text-align: center;">
                <i class="fas fa-envelope" style="font-size: 3rem; color: #D4AF37; margin-bottom: 1rem;"></i>
                <h3 style="color: #000; margin-bottom: 0.5rem;">Thank You!</h3>
                <p style="color: #666; margin-bottom: 1rem;">We've received your quotation request.</p>
                <p style="color: #888; font-size: 0.9rem;">Our team will contact you within 24 hours with your quotation details.</p>
                <button class="btn-quotation" style="margin-top: 1.5rem;" onclick="closeQuotationModal()">
                    Continue Shopping
                </button>
            </div>
        </div>
    </div>
    
    <!-- LIGHTBOX -->
    <div id="lightbox" class="lightbox" onclick="closeLightbox()">
        <span class="lightbox-close">&times;</span>
        <img class="lightbox-img" id="lightboxImg">
    </div>
    
    <div id="toast" class="toast"></div>
    
    <script>
        let cart = JSON.parse(localStorage.getItem('dajeCart')) || [];
        let currentColor = '{default_color}';
        let currentQuantity = 1;
        
        const currentProduct = {{
            id: '{slug}',
            name: "{name}",
            price: {price},
            image: "{main_image}"
        }};
        
        const recommendations = {recommendations_json};
        
        function updateCartUI() {{
            const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cartCount').innerText = cartCount;
            localStorage.setItem('dajeCart', JSON.stringify(cart));
            renderCartItems();
        }}
        
        function addToCart() {{
            const existingItem = cart.find(item => 
                item.id === currentProduct.id && 
                item.color === currentColor
            );
            
            if (existingItem) {{
                existingItem.quantity += currentQuantity;
            }} else {{
                cart.push({{
                    id: currentProduct.id,
                    name: currentProduct.name,
                    price: currentProduct.price,
                    image: currentProduct.image,
                    color: currentColor,
                    quantity: currentQuantity
                }});
            }}
            
            updateCartUI();
            showToast(`Added ${{currentQuantity}} x ${{currentProduct.name}} to cart`);
        }}
        
        function renderCartItems() {{
            const container = document.getElementById('cartItems');
            const cartTotal = document.getElementById('cartTotal');
            
            if (cart.length === 0) {{
                container.innerHTML = '<div style="text-align: center; padding: 2rem; color: #888;">Your cart is empty</div>';
                if (cartTotal) cartTotal.innerText = '฿0';
                return;
            }}
            
            let total = 0;
            container.innerHTML = cart.map((item, index) => {{
                const itemTotal = item.price * item.quantity;
                total += itemTotal;
                return `
                    <div class="cart-item">
                        <img src="${{item.image}}" class="cart-item-image">
                        <div class="cart-item-details">
                            <div class="cart-item-name">${{item.name}}</div>
                            <div class="cart-item-variant">${{item.color}}</div>
                            <div class="cart-item-price">฿${{item.price.toLocaleString()}}</div>
                        </div>
                        <div class="cart-item-actions">
                            <button class="cart-qty-btn" onclick="updateCartItem(${{index}}, -1)">-</button>
                            <span class="cart-item-qty">${{item.quantity}}</span>
                            <button class="cart-qty-btn" onclick="updateCartItem(${{index}}, 1)">+</button>
                            <i class="fas fa-trash-alt cart-item-remove" onclick="removeCartItem(${{index}})"></i>
                        </div>
                    </div>
                `;
            }}).join('');
            
            if (cartTotal) cartTotal.innerText = `฿${{total.toLocaleString()}}`;
        }}
        
        function updateCartItem(index, change) {{
            const newQty = cart[index].quantity + change;
            if (newQty <= 0) {{
                cart.splice(index, 1);
            }} else {{
                cart[index].quantity = newQty;
            }}
            updateCartUI();
        }}
        
        function removeCartItem(index) {{
            cart.splice(index, 1);
            updateCartUI();
        }}
        
        function requestQuotation() {{
            if (cart.length === 0) {{
                showToast('Please add items to your cart first');
                return;
            }}
            
            let itemsList = cart.map(item => 
                `${{item.name}} (${{item.color}}) x ${{item.quantity}} = ฿${{(item.price * item.quantity).toLocaleString()}}`
            ).join('\\n');
            
            const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            const subject = encodeURIComponent(`Quotation Request - Daje Games`);
            const body = encodeURIComponent(
                `Hello Daje Games Team,\\n\\n` +
                `I would like to request a quotation for the following items:\\n\\n` +
                `${{itemsList}}\\n\\n` +
                `Total: ฿${{total.toLocaleString()}}\\n\\n` +
                `Please contact me with the quotation details.\\n\\n` +
                `Best regards,\\n[Your Name]\\n[Your Email]\\n[Your Phone]`
            );
            
            closeCart();
            window.location.href = `mailto:info@daje.janishammer.com?subject=${{subject}}&body=${{body}}`;
            showToast('Opening email client...');
        }}
        
        function showToast(message) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => {{
                toast.classList.remove('show');
            }}, 2000);
        }}
        
        function openCart() {{
            document.getElementById('cartModal').classList.add('active');
            renderCartItems();
        }}
        
        function closeCart() {{
            document.getElementById('cartModal').classList.remove('active');
        }}
        
        function closeQuotationModal() {{
            document.getElementById('quotationModal').classList.remove('active');
        }}
        
        function updateQuantity(change) {{
            const input = document.getElementById('quantity');
            let newVal = currentQuantity + change;
            if (newVal >= 1 && newVal <= 99) {{
                currentQuantity = newVal;
                input.value = currentQuantity;
            }}
        }}
        
        function selectColor(element, color) {{
            document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
            element.classList.add('selected');
            currentColor = color;
        }}
        
        function toggleWishlist(btn) {{
            const icon = btn.querySelector('i');
            if (icon.classList.contains('far')) {{
                icon.classList.remove('far');
                icon.classList.add('fas');
                showToast('Added to wishlist');
            }} else {{
                icon.classList.remove('fas');
                icon.classList.add('far');
                showToast('Removed from wishlist');
            }}
        }}
        
        function changeImage(src) {{
            document.getElementById('mainImage').src = src;
            document.querySelectorAll('.thumbnail').forEach(thumb => {{
                thumb.classList.remove('active');
                if (thumb.src === src) thumb.classList.add('active');
            }});
        }}
        
        function openLightbox() {{
            const lightbox = document.getElementById('lightbox');
            const lightboxImg = document.getElementById('lightboxImg');
            lightboxImg.src = document.getElementById('mainImage').src;
            lightbox.classList.add('active');
        }}
        
        function closeLightbox() {{
            document.getElementById('lightbox').classList.remove('active');
        }}
        
        function scrollSlider(direction) {{
            const track = document.getElementById('sliderTrack');
            const scrollAmount = track.clientWidth * 0.8;
            track.scrollBy({{ left: direction * scrollAmount, behavior: 'smooth' }});
        }}
        
        document.getElementById('cartFloating').addEventListener('click', openCart);
        document.getElementById('mainImageContainer').addEventListener('click', openLightbox);
        document.getElementById('zoomIcon').addEventListener('click', (e) => {{
            e.stopPropagation();
            openLightbox();
        }});
        
        // Initialize recommendations
        const track = document.getElementById('sliderTrack');
        if (track && recommendations.length) {{
            track.innerHTML = recommendations.map(rec => `
                <div class="recommend-card" onclick="location.href='/product/${{rec.slug}}.html'">
                    <img src="${{rec.image}}" class="recommend-card-image">
                    <div class="recommend-card-info">
                        <div class="recommend-card-name">${{rec.name}}</div>
                        <div class="recommend-card-price">฿${{rec.price.toLocaleString()}}</div>
                    </div>
                </div>
            `).join('');
        }}
        
        updateCartUI();
        
        window.changeImage = changeImage;
        window.selectColor = selectColor;
        window.updateQuantity = updateQuantity;
        window.addToCart = addToCart;
        window.toggleWishlist = toggleWishlist;
        window.openLightbox = openLightbox;
        window.closeLightbox = closeLightbox;
        window.openCart = openCart;
        window.closeCart = closeCart;
        window.closeQuotationModal = closeQuotationModal;
        window.updateCartItem = updateCartItem;
        window.removeCartItem = removeCartItem;
        window.requestQuotation = requestQuotation;
        window.scrollSlider = scrollSlider;
    </script>
</body>
</html>"""

def main():
    print("🚀 Generating Daje product pages from CSV...")
    
    # Read products from CSV
    products = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)
    
    # Generate each product page and build JSON data
    products_json = []
    
    for product in products:
        slug = product['slug']
        name = product['name']
        price = int(product['price'])
        description = product['description']
        main_image = product['image_url']
        stock = product['stock']
        
        # Stock text mapping
        stock_map = {
            'in-stock': 'In Stock · Ready to Ship',
            'pre-order': 'Pre-Order · Reserve Now',
            'out-stock': 'Out of Stock · Contact Us'
        }
        stock_text = stock_map.get(stock, 'In Stock')
        
        # Split gallery images
        gallery_list = [img.strip() for img in product['gallery'].split(',') if img.strip()]
        thumbnails = '\n'.join([
            f'<img src="{img}" class="thumbnail {"active" if i == 0 else ""}" onclick="changeImage(this.src)">'
            for i, img in enumerate(gallery_list)
        ])
        
        # Split features
        features_list = [f.strip() for f in product['features'].split(',') if f.strip()]
        features_html = '\n'.join([
            f'<li><i class="fas fa-check-circle"></i> {f}</li>'
            for f in features_list
        ])
        
        # Color options
        colors = [c.strip() for c in product['color_options'].split(',') if c.strip()]
        default_color = colors[0] if colors else "Black"
        color_swatches = '\n'.join([
            f'<div class="color-swatch {"selected" if i == 0 else ""}" style="background: {c}" data-color="{c}" onclick="selectColor(this, \'{c}\')"></div>'
            for i, c in enumerate(colors)
        ])
        
        # Generate recommendations (all other products)
        recommendations = []
        for other in products:
            if other['slug'] != slug:
                recommendations.append({
                    'slug': other['slug'],
                    'name': other['name'],
                    'price': int(other['price']),
                    'image': other['image_url']
                })
        
        recommendations_html = '\n'.join([
            f'<div class="recommend-card" onclick="location.href=\'/{rec["slug"]}.html\'">'
            f'<img src="{rec["image"]}" class="recommend-card-image">'
            f'<div class="recommend-card-info">'
            f'<div class="recommend-card-name">{rec["name"]}</div>'
            f'<div class="recommend-card-price">฿{rec["price"]:,}</div>'
            f'</div></div>'
            for rec in recommendations
        ])
        
        # Generate the page
        page_html = PRODUCT_TEMPLATE.format(
            slug=slug,
            name=name,
            price=price,
            description=description,
            main_image=main_image,
            thumbnails=thumbnails,
            features_html=features_html,
            color_swatches=color_swatches,
            default_color=default_color,
            stock=stock,
            stock_text=stock_text,
            recommendations=recommendations_html,
            recommendations_json=json.dumps(recommendations)
        )
        
        # Write the file
        output_file = f"{slug}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(page_html)
        print(f"✅ Generated {output_file}")
        
        # Add to JSON data for main page
        products_json.append({
            'id': slug,
            'name': name,
            'brand': 'Daje Games',
            'category': 'Claw Machine',
            'price': price,
            'description': description,
            'main_image': main_image,
            'gallery_images': gallery_list,
            'colors': colors,
            'stock_status': stock_text,
            'stock_code': stock
        })
    
    # Write products.json for main page
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(products_json, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {JSON_FILE}")
    
    print("🎉 Daje product generation complete!")

if __name__ == "__main__":
    main()
