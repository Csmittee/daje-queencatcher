#!/usr/bin/env python3
"""
Product Page Generator for Daje Games
Compact layout with close button - pages in root folder
"""

import csv
import json
import re
import shutil
from pathlib import Path

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def parse_csv_list(value):
    """Parse line-break or comma-separated values (AirTable format uses line breaks)"""
    if not value or value == '':
        return []
    # Line break split first (AirTable format)
    if '\n' in str(value):
        return [item.strip() for item in str(value).split('\n') if item.strip()]
    # Comma split (fallback)
    elif ',' in str(value):
        return [item.strip() for item in str(value).split(',') if item.strip()]
    # Single value
    else:
        return [str(value).strip()] if str(value).strip() else []

def parse_color_swatches(colors_str, hex_str):
    colors = parse_csv_list(colors_str)
    hexes = parse_csv_list(hex_str)
    
    if len(hexes) == len(colors) and hexes:
        return [{'name': colors[i], 'hex': hexes[i]} for i in range(len(colors))]
    else:
        default_colors = {
            'Pink': '#FFB6C1', 'Black': '#000000', 'White': '#FFFFFF',
            'Red': '#FF4444', 'Blue': '#4444FF', 'Purple': '#AA66FF',
            'Gold': '#D4AF37', 'Silver': '#C0C0C0'
        }
        return [{'name': c, 'hex': default_colors.get(c, '#CCCCCC')} for c in colors]

def generate_thumbnails(gallery_images, main_image):
    thumbs = []
    all_images = [main_image] + gallery_images if gallery_images else [main_image]
    seen = set()
    unique_images = []
    for img in all_images:
        if img and img not in seen:
            seen.add(img)
            unique_images.append(img)
    
    for img in unique_images:
        active_class = 'active' if img == main_image else ''
        thumbs.append(f'<img src="{img}" class="thumbnail {active_class}" onclick="changeImage(this.src)">')
    return '\n'.join(thumbs)

def generate_color_options(colors_data):
    if not colors_data or len(colors_data) == 0:
        return ''
    swatches = []
    for i, color in enumerate(colors_data):
        selected_class = 'selected' if i == 0 else ''
        swatches.append(f'<div class="color-swatch {selected_class}" style="background: {color["hex"]}" data-color="{color["name"]}" onclick="selectColor(this, \'{color["name"]}\')"></div>')
    return f'''
    <div class="color-options">
        <h3>Color Options</h3>
        <div class="color-swatches">
            {''.join(swatches)}
        </div>
    </div>
    '''

def generate_size_options(sizes):
    if not sizes or len(sizes) == 0:
        return ''
    buttons = []
    for i, size in enumerate(sizes):
        selected_class = 'selected' if i == 0 else ''
        buttons.append(f'<div class="size-btn {selected_class}" data-size="{size}" onclick="selectSize(this, \'{size}\')">{size}</div>')
    return f'''
    <div class="size-options">
        <h3>Available Options</h3>
        <div class="size-buttons">
            {''.join(buttons)}
        </div>
    </div>
    '''

def generate_product_page(product, all_products, lang='en'):
    """Generate compact product detail page with close button"""
    
    if lang == 'th':
        name = product.get('name_th', product['name'])
        description = product.get('full_description_th', product['full_description'])
        lang_prefix = '/th'
        stock_labels = {'In Stock': 'มีสินค้า', 'Low Stock': 'สินค้าใกล้หมด', 'Out of Stock': 'สินค้าหมด', 'Pre-order': 'สั่งจองล่วงหน้า'}
        stock_status_text = stock_labels.get(product['stock_status'], product['stock_status'])
        back_link = 'https://daje.janishammer.com/th/'
        # Use Thai feature details if available
        feature_details_raw = product.get('feature_details_th', product.get('feature_details', ''))
    else:
        name = product['name']
        description = product['full_description']
        lang_prefix = ''
        stock_status_text = product['stock_status']
        back_link = 'https://daje.janishammer.com/'
        feature_details_raw = product.get('feature_details', '')
    
    gallery_images = parse_csv_list(product.get('gallery_images', ''))
    colors_data = parse_color_swatches(product.get('colors', ''), product.get('color_hex', ''))
    sizes = parse_csv_list(product.get('options', ''))
    
    default_color = colors_data[0]['name'] if colors_data else 'Default'
    default_size = sizes[0] if sizes else 'Standard'
    
    stock_class = {'In Stock': 'in-stock', 'Low Stock': 'low-stock', 'Out of Stock': 'out-stock', 'Pre-order': 'pre-order'}.get(product['stock_status'], 'in-stock')
    stock_icon = 'check-circle' if product['stock_status'] == 'In Stock' else 'clock' if product['stock_status'] == 'Pre-order' else 'exclamation-circle'
    
    price_value = int(float(product['price'])) if product.get('price') else 0
    
    # Recommendations — passed in from main() to avoid re-reading CSV on every call
    product_id = product.get('id', '')
    recommendations = [p for p in all_products if p.get('id', '') != product_id][:4]
    
    rec_html = ''
    for rec in recommendations:
        rec_name = rec['name'] if lang == 'en' else rec.get('name_th', rec['name'])
        rec_slug = slugify(rec['name'])
        rec_price = int(float(rec['price'])) if rec.get('price') else 0
        rec_html += f'''
        <div class="recommend-card" onclick="location.href='{lang_prefix}/{rec_slug}.html'">
            <img src="{rec.get('main_image', '')}" class="recommend-card-image">
            <div class="recommend-card-info">
                <div class="recommend-card-name">{rec_name}</div>
                <div class="recommend-card-price">{rec_price:,}</div>
            </div>
        </div>'''
    
    # DAJE BRAND COLORS
    html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>{name} | Daje Games</title>
    <meta name="description" content="{description[:150]}">
    <meta property="og:title" content="{name}">
    <meta property="og:description" content="{description[:150]}">
    <meta property="og:image" content="{product['main_image']}">
    <meta property="og:url" content="https://daje.janishammer.com{lang_prefix}/{slugify(product['name'])}.html">
    <!-- Anti-flicker: hides page until injector builds correct navbar -->
    <style id="jh-anti-flicker">body {{ opacity: 0; }}</style>
    <!-- INJECTORS (config must load before core) -->
    <script src="https://assets.janishammer.com/js/injector-config.js"></script>
    <script src="https://assets.janishammer.com/js/injector-core.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Quicksand', sans-serif;
            background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
            min-height: 100vh;
            padding: 80px 1rem 2rem;
        }}
        .close-btn {{
            position: fixed; top: 20px; right: 20px;
            width: 44px; height: 44px; border-radius: 50%;
            background: #FFB6C1; color: #333;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; z-index: 1001; font-size: 1.5rem;
            text-decoration: none; transition: all 0.3s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .close-btn:hover {{ transform: scale(1.1); background: #D4AF37; color: white; }}
        .cart-floating {{
            position: fixed; bottom: 2rem; right: 2rem;
            background: linear-gradient(135deg, #FFB6C1, #FF99AA);
            width: 50px; height: 50px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .cart-floating:hover {{ transform: scale(1.1); }}
        .cart-floating i {{ font-size: 1.2rem; color: #333; }}
        .cart-count {{
            position: absolute; top: -5px; right: -5px;
            background: #D4AF37; color: #333; border-radius: 50%;
            width: 20px; height: 20px; display: flex;
            align-items: center; justify-content: center;
            font-size: 0.65rem; font-weight: bold;
        }}
        .product-container {{ max-width: 960px; margin: 0 auto; background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 8px 30px rgba(0,0,0,0.08); }}
        .product-detail {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; padding: 1.5rem; }}
        .main-image-container {{ position: relative; cursor: pointer; overflow: hidden; border-radius: 16px; background: #fafafa; aspect-ratio: 1/1; display: flex; align-items: center; justify-content: center; }}
        .main-image {{ width: 100%; height: 100%; object-fit: contain; transition: transform 0.3s; }}
        .zoom-icon {{ position: absolute; bottom: 0.75rem; right: 0.75rem; background: rgba(0,0,0,0.6); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }}
        .thumbnail-gallery {{ display: flex; gap: 0.5rem; margin-top: 0.75rem; overflow-x: auto; }}
        .thumbnail {{ width: 60px; height: 60px; border-radius: 12px; cursor: pointer; border: 2px solid transparent; object-fit: cover; flex-shrink: 0; }}
        .thumbnail.active {{ border-color: #FFB6C1; }}
        .product-info {{ display: flex; flex-direction: column; gap: 0.75rem; }}
        .product-category {{ display: inline-block; background: rgba(255,182,193,0.2); color: #FFB6C1; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; width: fit-content; }}
        .product-name {{ font-size: 1.5rem; font-weight: 700; color: #333; line-height: 1.3; }}
        .product-brand {{ font-size: 0.8rem; color: #888; display: flex; align-items: center; gap: 0.5rem; }}
        .product-price {{ font-size: 1.6rem; font-weight: 700; color: #D4AF37; margin: 0.25rem 0; }}
        .product-price::before {{ content: "฿"; font-size: 1.2rem; }}
        .stock-status {{ display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.3rem 0.8rem; border-radius: 40px; font-weight: 600; font-size: 0.7rem; width: fit-content; }}
        .stock-status.in-stock {{ background: rgba(212,175,55,0.1); color: #D4AF37; }}
        .stock-status.low-stock {{ background: rgba(255,152,0,0.1); color: #FF9800; }}
        .features-section h3 {{ font-size: 0.9rem; color: #333; margin-bottom: 0.5rem; }}
        .features-list {{ white-space: pre-line; line-height: 1.5; color: #666; font-size: 0.8rem; }}
        .color-options, .size-options {{ margin: 0.25rem 0; }}
        .color-options h3, .size-options h3 {{ font-size: 0.8rem; margin-bottom: 0.4rem; }}
        .color-swatches {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
        .color-swatch {{ width: 32px; height: 32px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; transition: all 0.2s; }}
        .color-swatch.selected {{ border-color: #FFB6C1; transform: scale(1.05); }}
        .size-buttons {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
        .size-btn {{ background: #f0f0f0; border: 1px solid #e0e0e0; padding: 0.3rem 0.8rem; border-radius: 40px; cursor: pointer; font-size: 0.75rem; transition: all 0.2s; }}
        .size-btn.selected {{ background: #FFB6C1; border-color: #FFB6C1; color: #333; }}
        .quantity-selector {{ margin: 0.25rem 0; }}
        .quantity-selector h3 {{ font-size: 0.8rem; margin-bottom: 0.4rem; }}
        .quantity-control {{ display: flex; align-items: center; gap: 0.5rem; }}
        .qty-btn {{ width: 30px; height: 30px; border-radius: 8px; background: #f0f0f0; border: 1px solid #e0e0e0; cursor: pointer; font-size: 1rem; }}
        .quantity-input {{ width: 50px; height: 30px; text-align: center; border: 1px solid #e0e0e0; border-radius: 8px; }}
        .action-buttons {{ display: flex; gap: 0.75rem; margin-top: 0.5rem; }}
        .btn-add-to-cart {{ flex: 2; background: linear-gradient(135deg, #FFB6C1, #FF99AA); color: #333; border: none; padding: 0.7rem; border-radius: 40px; font-weight: 600; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }}
        .btn-wishlist {{ background: #f0f0f0; border: 1px solid #e0e0e0; padding: 0.7rem; border-radius: 40px; cursor: pointer; aspect-ratio: 1; }}
        .you-may-like {{ background: #fafafa; padding: 1.5rem; border-top: 1px solid #eee; }}
        .you-may-like h2 {{ font-size: 1.1rem; margin-bottom: 1rem; }}
        .slider-track {{ display: flex; gap: 1rem; overflow-x: auto; scroll-behavior: smooth; }}
        .recommend-card {{ flex: 0 0 calc(25% - 0.75rem); min-width: 140px; background: white; border-radius: 12px; overflow: hidden; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.2s; }}
        .recommend-card:hover {{ transform: translateY(-4px); }}
        .recommend-card-image {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; }}
        .recommend-card-info {{ padding: 0.5rem; }}
        .recommend-card-name {{ font-size: 0.75rem; font-weight: 600; margin-bottom: 0.25rem; }}
        .recommend-card-price {{ font-size: 0.8rem; font-weight: 700; color: #D4AF37; }}
        .slider-nav {{ display: flex; justify-content: center; gap: 0.5rem; margin-top: 0.75rem; }}
        .nav-btn {{ width: 30px; height: 30px; border-radius: 50%; background: white; border: 1px solid #e0e0e0; cursor: pointer; }}
        .cart-modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2000; justify-content: center; align-items: center; }}
        .cart-modal.active {{ display: flex; }}
        .cart-content {{ max-width: 500px; width: 90%; max-height: 70vh; background: white; border-radius: 20px; overflow: hidden; display: flex; flex-direction: column; }}
        .cart-header {{ padding: 1rem; background: linear-gradient(135deg, #FFB6C1, #FF99AA); display: flex; justify-content: space-between; align-items: center; }}
        .cart-header h2 {{ font-size: 1.1rem; color: #333; }}
        .cart-close {{ font-size: 1.2rem; cursor: pointer; color: #333; }}
        .cart-items {{ flex: 1; overflow-y: auto; padding: 0.75rem; }}
        .cart-item {{ display: flex; gap: 0.75rem; padding: 0.75rem; border-bottom: 1px solid #eee; }}
        .cart-item-image {{ width: 50px; height: 50px; object-fit: cover; border-radius: 8px; }}
        .cart-item-name {{ font-weight: 600; font-size: 0.85rem; }}
        .cart-item-price {{ color: #D4AF37; font-weight: 600; font-size: 0.8rem; }}
        .cart-summary {{ padding: 1rem; background: #fafafa; border-top: 1px solid #eee; }}
        .cart-total {{ display: flex; justify-content: space-between; font-size: 1rem; font-weight: 700; margin-bottom: 0.75rem; }}
        .btn-quotation {{ width: 100%; background: linear-gradient(135deg, #FFB6C1, #FF99AA); color: #333; border: none; padding: 0.7rem; border-radius: 40px; font-weight: 600; cursor: pointer; }}
        .toast {{ position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%) translateY(100px); background: #D4AF37; color: #333; padding: 0.6rem 1.2rem; border-radius: 40px; font-size: 0.8rem; z-index: 2001; transition: transform 0.3s; }}
        .toast.show {{ transform: translateX(-50%) translateY(0); }}
        .lightbox {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 3000; justify-content: center; align-items: center; }}
        .lightbox.active {{ display: flex; }}
        .lightbox-img {{ max-width: 90%; max-height: 90%; object-fit: contain; }}
        .lightbox-close {{ position: absolute; top: 20px; right: 30px; color: white; font-size: 2rem; cursor: pointer; }}
        @media (max-width: 768px) {{
            body {{ padding: 70px 0.5rem 1rem; }}
            .product-detail {{ grid-template-columns: 1fr; gap: 1rem; padding: 1rem; }}
            .product-name {{ font-size: 1.2rem; }}
            .recommend-card {{ flex: 0 0 calc(50% - 0.5rem); }}
            .close-btn {{ top: 10px; right: 10px; width: 36px; height: 36px; font-size: 1.2rem; }}
        }}
    </style>
</head>
<body>
    <a href="{back_link}" class="close-btn">&times;</a>
    <div class="cart-floating" id="cartFloating"><i class="fas fa-shopping-bag"></i><span class="cart-count" id="cartCount">0</span></div>
    
    <div class="product-container">
        <div class="product-detail">
            <div class="product-gallery">
                <div class="main-image-container" id="mainImageContainer">
                    <img src="{product['main_image']}" alt="{name}" class="main-image" id="mainImage">
                    <div class="zoom-icon" id="zoomIcon"><i class="fas fa-expand"></i></div>
                </div>
                <div class="thumbnail-gallery" id="thumbnailGallery">
                    {generate_thumbnails(gallery_images, product['main_image'])}
                </div>
            </div>
            <div class="product-info">
                <span class="product-category">{product['category']}</span>
                <h1 class="product-name">{name}</h1>
                <div class="product-brand"><i class="fas fa-tag"></i><span>{product.get('brand', 'Daje Games')} · {product.get('collection', 'Premium')}</span></div>
                <div class="product-price">{price_value:,}</div>
                <div class="stock-status {stock_class}"><i class="fas fa-{stock_icon}"></i><span>{stock_status_text}</span></div>
                <div class="features-section"><h3>Specifications</h3><div class="features-list">{feature_details_raw}</div></div>
                {generate_color_options(colors_data)}
                {generate_size_options(sizes)}
                <div class="quantity-selector"><h3>Quantity</h3><div class="quantity-control"><button class="qty-btn" onclick="updateQuantity(-1)">-</button><input type="number" id="quantity" class="quantity-input" value="1" min="1" max="99" readonly><button class="qty-btn" onclick="updateQuantity(1)">+</button></div></div>
                <div class="action-buttons"><button class="btn-add-to-cart" onclick="addToCart()"><i class="fas fa-shopping-cart"></i> Add to Cart</button><button class="btn-wishlist" onclick="toggleWishlist(this)"><i class="far fa-heart"></i></button></div>
            </div>
        </div>
        <div class="you-may-like"><h2>✨ You May Also Like</h2><div class="slider-track" id="sliderTrack">{rec_html}</div><div class="slider-nav"><button class="nav-btn" onclick="scrollSlider(-1)"><i class="fas fa-chevron-left"></i></button><button class="nav-btn" onclick="scrollSlider(1)"><i class="fas fa-chevron-right"></i></button></div></div>
    </div>
    
    <div id="cartModal" class="cart-modal"><div class="cart-content"><div class="cart-header"><h2><i class="fas fa-shopping-bag"></i> Your Cart</h2><span class="cart-close" onclick="closeCart()">&times;</span></div><div class="cart-items" id="cartItems"><div style="text-align:center;padding:1rem;">Your cart is empty</div></div><div class="cart-summary"><div class="cart-total"><span>Total</span><span id="cartTotal">฿0</span></div><button class="btn-quotation" onclick="requestQuotation()"><i class="fas fa-file-invoice"></i> Get Quotation</button></div></div></div>
    <div id="quotationModal" class="cart-modal"><div class="cart-content" style="max-width:400px;text-align:center;"><div class="cart-header"><h2><i class="fas fa-check-circle"></i> Thank You!</h2><span class="cart-close" onclick="closeQuotationModal()">&times;</span></div><div style="padding:1.5rem;"><i class="fas fa-envelope" style="font-size:2rem;color:#D4AF37;margin-bottom:0.5rem;"></i><p>We've received your quotation request.</p><p style="font-size:0.8rem;color:#888;">Our team will contact you within 24 hours.</p><button class="btn-quotation" style="margin-top:1rem;" onclick="closeQuotationModal()">Continue</button></div></div></div>
    <div id="lightbox" class="lightbox" onclick="closeLightbox()"><span class="lightbox-close">&times;</span><img class="lightbox-img" id="lightboxImg"></div>
    <div id="toast" class="toast"></div>
    
    <script>
        let cart = JSON.parse(localStorage.getItem('dajeCart')) || [];
        let currentColor = "{default_color}";
        let currentSize = "{default_size}";
        let currentQuantity = 1;
        const currentProduct = {{ id: '{product.get('id', '')}', name: "{name}", price: {price_value}, image: "{product['main_image']}", colors: {json.dumps([c['name'] for c in colors_data])}, sizes: {json.dumps(sizes)} }};
        
        function updateCartUI() {{ const count = cart.reduce((s,i)=>s+i.quantity,0); document.getElementById('cartCount').innerText=count; localStorage.setItem('dajeCart',JSON.stringify(cart)); renderCartItems(); }}
        function renderCartItems() {{ const container=document.getElementById('cartItems'),totalSpan=document.getElementById('cartTotal'); if(!container) return; if(cart.length===0){{ container.innerHTML='<div style="text-align:center;padding:1rem;">Your cart is empty</div>'; if(totalSpan) totalSpan.innerText='฿0'; return; }} let total=0; container.innerHTML=cart.map((item,idx)=>{{ const itemTotal=item.price*item.quantity; total+=itemTotal; return `<div class="cart-item"><img src="${{item.image}}" class="cart-item-image"><div class="cart-item-details"><div class="cart-item-name">${{item.name}}</div><div class="cart-item-price">฿${{item.price.toLocaleString()}}</div></div><div class="cart-item-actions"><button class="cart-qty-btn" onclick="updateCartItem(${{idx}},-1)">-</button><span>${{item.quantity}}</span><button class="cart-qty-btn" onclick="updateCartItem(${{idx}},1)">+</button><i class="fas fa-trash-alt" onclick="removeCartItem(${{idx}})" style="color:#F44336;cursor:pointer;"></i></div></div>`; }}).join(''); if(totalSpan) totalSpan.innerText=`฿${{total.toLocaleString()}}`; }}
        function updateCartItem(idx,ch) {{ const n=cart[idx].quantity+ch; if(n<=0) cart.splice(idx,1); else cart[idx].quantity=n; updateCartUI(); }}
        function removeCartItem(idx) {{ cart.splice(idx,1); updateCartUI(); }}
        function addToCart() {{ const existing=cart.find(i=>i.id===currentProduct.id&&i.color===currentColor&&i.size===currentSize); if(existing) existing.quantity+=currentQuantity; else cart.push({{id:currentProduct.id,name:currentProduct.name,price:currentProduct.price,image:currentProduct.image,color:currentColor,size:currentSize,quantity:currentQuantity}}); updateCartUI(); showToast(`Added ${{currentQuantity}} x ${{currentProduct.name}}`); }}
        function requestQuotation() {{ if(cart.length===0){{ showToast('Add items first'); return; }} let items=cart.map(i=>`${{i.name}} (${{i.color}}, ${{i.size}}) x ${{i.quantity}} = ฿${{(i.price*i.quantity).toLocaleString()}}`).join('\\n'); let total=cart.reduce((s,i)=>s+i.price*i.quantity,0); window.location.href=`mailto:info@daje.janishammer.com?subject=Quotation Request&body=Hello,%0A%0AI would like a quotation for:%0A%0A${{encodeURIComponent(items)}}%0A%0ATotal: ฿${{total.toLocaleString()}}%0A%0APlease contact me.%0A%0ABest regards`; showToast('Opening email...'); }}
        function updateQuantity(ch) {{ let n=currentQuantity+ch; if(n>=1&&n<=99){{ currentQuantity=n; document.getElementById('quantity').value=currentQuantity; }} }}
        function selectColor(el,c) {{ document.querySelectorAll('.color-swatch').forEach(s=>s.classList.remove('selected')); el.classList.add('selected'); currentColor=c; }}
        function selectSize(el,s) {{ document.querySelectorAll('.size-btn').forEach(b=>b.classList.remove('selected')); el.classList.add('selected'); currentSize=s; }}
        function toggleWishlist(btn) {{ const i=btn.querySelector('i'); i.classList.toggle('far'); i.classList.toggle('fas'); showToast(i.classList.contains('fas')?'Added to wishlist':'Removed'); }}
        function changeImage(src) {{ document.getElementById('mainImage').src=src; document.querySelectorAll('.thumbnail').forEach(t=>t.classList.remove('active')); if(event.target&&event.target.classList) event.target.classList.add('active'); }}
        function openLightbox() {{ const lb=document.getElementById('lightbox'); document.getElementById('lightboxImg').src=document.getElementById('mainImage').src; lb.classList.add('active'); }}
        function closeLightbox() {{ document.getElementById('lightbox').classList.remove('active'); }}
        function openCart() {{ document.getElementById('cartModal').classList.add('active'); renderCartItems(); }}
        function closeCart() {{ document.getElementById('cartModal').classList.remove('active'); }}
        function closeQuotationModal() {{ document.getElementById('quotationModal').classList.remove('active'); }}
        function showToast(msg) {{ const t=document.getElementById('toast'); t.textContent=msg; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),2000); }}
        function scrollSlider(dir) {{ const track=document.getElementById('sliderTrack'); track.scrollBy({{left:dir*track.clientWidth*0.8,behavior:'smooth'}}); }}
        document.getElementById('cartFloating').addEventListener('click',openCart);
        document.getElementById('mainImageContainer').addEventListener('click',openLightbox);
        document.getElementById('zoomIcon').addEventListener('click',(e)=>{{ e.stopPropagation(); openLightbox(); }});
        updateCartUI();
    </script>
</body>
</html>'''
    
    return html

def generate_products_json(products):
    json_data = []
    for p in products:
        # Get Thai description short version
        thai_desc = p.get('full_description_th', p.get('full_description', ''))
        thai_desc_short = thai_desc[:120] + '...' if len(thai_desc) > 120 else thai_desc
        
        json_data.append({
            'id': p['id'],
            'name': p['name'],
            'name_th': p.get('name_th', p['name']),
            'brand': p.get('brand', 'Daje Games'),
            'category': p['category'],
            'price': int(float(p['price'])) if p.get('price') else 0,
            'main_image': p['main_image'],
            'description': p['full_description'][:120] + '...' if len(p['full_description']) > 120 else p['full_description'],
            'description_th': thai_desc_short,
            'stock_status': p['stock_status']
        })
    with open(Path(__file__).parent.parent / 'products.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated products.json ({len(json_data)} products)")

def main():
    csv_path = Path(__file__).parent.parent / 'products.csv'
    
    if not csv_path.exists():
        print(f"❌ Error: {csv_path} not found!")
        return
    
    # ===== CLEAN OLD FILES =====
    product_dir = Path(__file__).parent.parent
    th_dir = product_dir / 'th'
    
    # Delete existing product HTML files in root
    for file in product_dir.glob('*.html'):
        # Don't delete index.html
        if file.name != 'index.html':
            file.unlink()
            print(f"🗑️  Deleted: {file}")
    
    # Delete existing Thai product files
    if th_dir.exists():
        for file in th_dir.glob('*.html'):
            file.unlink()
            print(f"🗑️  Deleted: {file}")
    
    print(f"📁 Cleaned old product files")
    # ===== END CLEAN =====
    
    products = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('id'):
                products.append(row)
    
    print(f"📦 Loaded {len(products)} products from CSV")
    generate_products_json(products)
    
    # Generate individual product pages
    for product in products:
        try:
            # English page
            en_html = generate_product_page(product, products, lang='en')
            en_path = product_dir / f"{slugify(product['name'])}.html"
            with open(en_path, 'w', encoding='utf-8') as f:
                f.write(en_html)
            print(f"✅ Generated: {en_path}")
            
            # Thai page (if Thai content exists)
            if product.get('name_th') and product.get('full_description_th'):
                th_dir.mkdir(exist_ok=True)
                th_html = generate_product_page(product, products, lang='th')
                th_path = th_dir / f"{slugify(product['name'])}.html"
                with open(th_path, 'w', encoding='utf-8') as f:
                    f.write(th_html)
                print(f"✅ Generated: {th_path}")
        except Exception as e:
            print(f"❌ Error generating {product.get('name', 'unknown')}: {e}")
    
    print("\n🎉 All product pages generated successfully!")

if __name__ == '__main__':
    main()
