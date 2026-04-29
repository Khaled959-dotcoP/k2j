<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>K2J ARMORY - AK-47</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:#fff;font-family:'Courier New';color:#000;padding:20px;}
        .container{max-width:1200px;margin:0 auto;}
        .header{display:flex;justify-content:space-between;border-bottom:2px solid #000;padding-bottom:15px;margin-bottom:25px;}
        .logo{font-size:28px;font-weight:bold;}
        .cart-icon{border:2px solid #000;padding:8px 20px;cursor:pointer;}
        .products-grid{display:grid;grid-template-columns:1fr;gap:25px;max-width:600px;margin:0 auto;}
        .product-card{background:#f5f5f5;border:2px solid #000;border-radius:10px;padding:25px;}
        .product-img{width:100%;height:250px;object-fit:cover;border-radius:8px;margin-bottom:15px;}
        .product-title{font-size:22px;font-weight:bold;}
        .product-price{font-size:26px;margin:10px 0;font-weight:bold;}
        .add-to-cart{background:#fff;border:2px solid #000;padding:10px;cursor:pointer;width:100%;text-align:center;margin-top:15px;}
        .add-to-cart:hover{background:#000;color:#fff;}
        button{background:#fff;border:2px solid #000;padding:8px 15px;cursor:pointer;}
        button:hover{background:#000;color:#fff;}
        .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:1000;justify-content:center;align-items:center;}
        .modal-content{background:#fff;border:3px solid #000;border-radius:10px;padding:30px;max-width:500px;width:90%;}
        .cart-item{border-bottom:1px solid #ccc;padding:10px 0;display:flex;justify-content:space-between;}
        .total{font-size:20px;margin:15px 0;padding-top:10px;border-top:2px solid #000;font-weight:bold;}
        .checkout-btn{width:100%;padding:12px;background:#000;color:#fff;font-weight:bold;border:none;}
        .telegram-btn{background:#0088cc;color:white;border:none;}
        .auth-container{max-width:400px;margin:50px auto;background:#f5f5f5;border:2px solid #000;border-radius:10px;padding:30px;text-align:center;}
        .auth-container input{width:100%;padding:10px;margin:10px 0;border:1px solid #000;font-family:'Courier New';}
        .error{color:red;}
        .success{color:green;}
    </style>
</head>
<body>
<div class="container" id="app"></div>
<script>
    let currentUser = null;
    let cart = JSON.parse(localStorage.getItem("cart") || "[]");
    const API_URL = "http://localhost:5000/api";
    
    function saveCart(){ localStorage.setItem("cart", JSON.stringify(cart)); }
    function addToCart(p){ let e=cart.find(i=>i.id===p.id); if(e) e.quantity++; else cart.push({...p,quantity:1}); saveCart(); showNotification("Added: "+p.name); }
    function removeFromCart(id){ cart=cart.filter(i=>i.id!==id); saveCart(); renderCartModal(); }
    function updateQuantity(id,delta){ let i=cart.find(i=>i.id===id); if(i){ i.quantity+=delta; if(i.quantity<=0) cart=cart.filter(x=>x.id!==id); saveCart(); renderCartModal(); } }
    function getTotal(){ return cart.reduce((s,i)=>s+(i.price*i.quantity),0); }
    function showNotification(msg){ let n=document.createElement('div'); n.style.cssText='position:fixed;bottom:20px;right:20px;background:#000;color:#fff;padding:8px16px;z-index:2000;'; n.innerText=msg; document.body.appendChild(n); setTimeout(()=>n.remove(),2000); }
    
    async function apiCall(endpoint, data){
        let res = await fetch(API_URL+endpoint, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
        return res.json();
    }
    
    async function register(username, password){
        if(username.length<3) return {success:false, error:"Username min 3"};
        if(password.length<4) return {success:false, error:"Password min 4"};
        return await apiCall("/auth/register", {username, password});
    }
    
    async function login(username, password){
        let res = await apiCall("/auth/login", {username, password});
        if(res.success){
            currentUser = res.user;
            sessionStorage.setItem("user", JSON.stringify(currentUser));
        }
        return res;
    }
    
    function logout(){ currentUser=null; sessionStorage.removeItem("user"); render(); }
    function getCurrentUser(){ if(currentUser) return currentUser; let u=sessionStorage.getItem("user"); if(u){ currentUser=JSON.parse(u); return currentUser; } return null; }
    
    function sendTelegramOrder(items, total){
        let msg = "[NEW ORDER]\nITEMS: "+items+"\nTOTAL: $"+total+"\nPAYMENT: BITCOIN";
        window.open("https://t.me/+905367089683?text="+encodeURIComponent(msg), '_blank');
    }
    
    function render(){
        let user = getCurrentUser();
        if(!user){ renderAuth(); return; }
        renderStore();
    }
    
    function renderAuth(){
        let html = `<div class="auth-container"><h2>K2J ARMORY</h2><div id="authMsg"></div>
            <h3>REGISTER</h3><input type="text" id="regUser" placeholder="username (min 3)"><input type="password" id="regPass" placeholder="password (min 4)">
            <button onclick="doRegister()">[ REGISTER ]</button>
            <h3 style="margin-top:20px;">LOGIN</h3><input type="text" id="loginUser" placeholder="username"><input type="password" id="loginPass" placeholder="password">
            <button onclick="doLogin()">[ LOGIN ]</button>
            <p style="margin-top:15px;font-size:10px;">Admin: admin / admin123</p></div>`;
        document.getElementById("app").innerHTML = html;
    }
    
    function renderStore(){
        let cartCount = cart.reduce((s,i)=>s+i.quantity,0);
        let html = `<div class="header"><div class="logo">[ K2J ARMORY ]</div><div><span>USER: ${currentUser.username}</span><button onclick="logout()" style="margin-left:10px;">[ LOGOUT ]</button><div class="cart-icon" onclick="showCart()" style="display:inline-block;margin-left:10px;">[ CART ] (${cartCount})</div></div></div>
            <div class="products-grid"><div class="product-card"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/AK-47_assault_rifle.jpg/800px-AK-47_assault_rifle.jpg" class="product-img" onerror="this.src='https://placehold.co/600x400/333/fff?text=AK-47'">
            <div class="product-title">AK-47</div><div class="product-price">$ 400 USD</div>
            <div class="product-specs">Caliber: 7.62x39mm | Range: 350m | 2 x FULL 30-ROUND MAGAZINES INCLUDED</div>
            <div class="add-to-cart" onclick="addToCartFromUI()">[ ADD TO CART ]</div></div></div>`;
        document.getElementById("app").innerHTML = html;
    }
    
    function renderCartModal(){
        let modal = document.getElementById("cartModal");
        if(!modal){ let m=document.createElement('div'); m.id="cartModal"; m.className="modal"; document.body.appendChild(m); modal=m; }
        if(cart.length===0){ modal.innerHTML=`<div class="modal-content"><h2>CART</h2><p>Empty</p><button onclick="closeCartModal()">[ CLOSE ]</button></div>`; modal.style.display="flex"; return; }
        let itemsHtml = cart.map(i=>`<div class="cart-item"><div><strong>${i.name}</strong><br>$${i.price} x ${i.quantity}</div><div><button onclick="updateQuantity(${i.id},-1)">-</button><span>${i.quantity}</span><button onclick="updateQuantity(${i.id},1)">+</button><button onclick="removeFromCart(${i.id})">[X]</button></div></div>`).join('');
        let total=getTotal();
        modal.innerHTML=`<div class="modal-content"><h2>CART</h2>${itemsHtml}<div class="total">TOTAL: $${total}</div><button class="checkout-btn" onclick="checkout()">[ CHECKOUT - BITCOIN ]</button><button onclick="closeCartModal()">[ CLOSE ]</button></div>`;
        modal.style.display="flex";
    }
    
    function checkout(){
        closeCartModal();
        let total=getTotal();
        let items=cart.map(i=>i.name+" x"+i.quantity).join(", ");
        let html=`<div class="header"><div class="logo">K2J ARMORY</div><div><button onclick="renderStore()"><-- BACK</button></div></div>
            <div style="max-width:500px;margin:20px auto;background:#f5f5f5;border:2px solid #000;padding:20px;"><h2>BITCOIN CHECKOUT</h2>
            ${cart.map(i=>`<p>${i.name} x${i.quantity} = $${i.price*i.quantity}</p>`).join('')}<h3>TOTAL: $${total}</h3>
            <p>Send BTC to: <strong>bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh</strong></p>
            <button class="telegram-btn" onclick="confirmOrder()" style="margin-top:15px;">[ CONFIRM VIA TELEGRAM ]</button></div>`;
        document.getElementById("app").innerHTML = html;
    }
    
    function confirmOrder(){
        let total=getTotal();
        let items=cart.map(i=>i.name+" x"+i.quantity).join(", ");
        sendTelegramOrder(items,total);
        cart=[]; saveCart();
        showNotification("Order sent to Telegram!");
        setTimeout(()=>renderStore(),1500);
    }
    
    window.doRegister=async function(){ let u=document.getElementById("regUser").value; let p=document.getElementById("regPass").value; let res=await register(u,p); let m=document.getElementById("authMsg"); if(res.success) m.innerHTML='<div class="success">Registered! Please login.</div>'; else m.innerHTML='<div class="error">'+res.error+'</div>'; };
    window.doLogin=async function(){ let u=document.getElementById("loginUser").value; let p=document.getElementById("loginPass").value; let res=await login(u,p); let m=document.getElementById("authMsg"); if(res.success) render(); else m.innerHTML='<div class="error">Invalid credentials</div>'; };
    window.addToCartFromUI=function(){ let p={id:1,name:"AK-47",price:400,image:"ak47.jpg"}; addToCart(p); };
    window.showCart=renderCartModal; window.closeCartModal=function(){ let m=document.getElementById("cartModal"); if(m) m.style.display="none"; };
    window.updateQuantity=updateQuantity; window.removeFromCart=removeFromCart; window.checkout=checkout; window.confirmOrder=confirmOrder;
    
    render();
</script>
</body>
</html>
