let cartItems = []; 
let total = 0; 
 
function addToCart(id, name, price) { 
    let existingItem = cartItems.find(item => item.id === id); 
    if (existingItem) { 
        existingItem.quantity++; 
    } else { 
        cartItems.push({ id, name, price, quantity: 1 }); 
    } 
    total += price; 
    updateCart(); 
} 
 
function updateCart() { 
    let cartItemsDiv = document.getElementById("cart-items"); 
    cartItemsDiv.innerHTML = ""; 
    for (let item of cartItems) { 
        let itemDiv = document.createElement("div"); 
        itemDiv.innerText = `${item.name} - $${item.price} x ${item.quantity}`; 
        cartItemsDiv.appendChild(itemDiv); 
    } 
    document.getElementById("total-price").innerText = "$" + total; 
} 
 
function showQR() { 
    document.getElementById("cart").style.display = "none"; 
    document.getElementById("qr").style.display = "block"; 
    document.getElementById("items").style.display = "none"; 
    setTimeout(() => { 
        document.getElementById("qr").style.display = "none"; 
        document.getElementById("thank-you").style.display = "block"; 
    }, 15000); // Hide QR code after 15 seconds 
} 
