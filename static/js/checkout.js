//==================================================
// LINO - CHECKOUT
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    const container    = document.getElementById("checkoutItems");
    const subtotalEl   = document.getElementById("subtotal");
    const grandTotalEl = document.getElementById("grandTotal");
    const summaryCount = document.getElementById("summaryCount");
    const form         = document.getElementById("checkoutForm");
    const cartDataInput= document.getElementById("cartDataInput");

    const cart = JSON.parse(localStorage.getItem("cart")) || [];

    let total = 0;

    //--------------------------------------
    // EMPTY CART
    //--------------------------------------

    if (!container) return;

    if (cart.length === 0) {

        container.innerHTML = `

            <div class="empty-checkout">

                <h3>Your Bag is Empty</h3>

                <p>Add your favourite fragrance to continue.</p>

            </div>

        `;

        if (subtotalEl)   subtotalEl.textContent   = "₹0";
        if (grandTotalEl) grandTotalEl.textContent = "₹0";
        if (summaryCount) summaryCount.textContent = "0 Items";

    } else {

        //--------------------------------------
        // RENDER ITEMS
        //--------------------------------------

        if (summaryCount) {
            summaryCount.textContent =
                `${cart.length} Item${cart.length !== 1 ? "s" : ""}`;
        }

        cart.forEach(item => {

            const rawPrice = String(item.price).replace(/[^\d.]/g, "");
            const price    = parseFloat(rawPrice) || 0;
            const itemTotal = price * (item.quantity || 1);

            total += itemTotal;

            container.innerHTML += `

                <div class="checkout-item">

                    <img src="${item.image}"
                         alt="${item.name}">

                    <div class="checkout-info">

                        <h4>${item.name}</h4>

                        <p>Qty : ${item.quantity || 1}</p>

                    </div>

                    <strong>

                        ₹${itemTotal.toLocaleString("en-IN")}

                    </strong>

                </div>

            `;

        });

        if (subtotalEl) {
            subtotalEl.textContent =
                `₹${total.toLocaleString("en-IN")}`;
        }

        if (grandTotalEl) {
            grandTotalEl.textContent =
                `₹${total.toLocaleString("en-IN")}`;
        }

    }

    //--------------------------------------
    // FORM SUBMIT → inject cart JSON
    //--------------------------------------

    if (form) {

        form.addEventListener("submit", (e) => {

            if (cart.length === 0) {
                e.preventDefault();
                alert("Your cart is empty. Please add items before checking out.");
                return;
            }

            // Populate hidden field with cart JSON
            if (cartDataInput) {
                cartDataInput.value = JSON.stringify(cart);
            }

            // Clear cart from localStorage after successful form submit
            // (happens after redirect, so we store a flag)
            sessionStorage.setItem("clearCartOnLoad", "true");

        });

    }

});

//--------------------------------------
// CLEAR CART IF RETURNING FROM ORDER SUCCESS
//--------------------------------------

if (sessionStorage.getItem("clearCartOnLoad") === "true") {
    localStorage.removeItem("cart");
    sessionStorage.removeItem("clearCartOnLoad");
    if (typeof updateCartCount === "function") updateCartCount();
}