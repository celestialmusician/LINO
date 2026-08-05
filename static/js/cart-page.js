//==================================================
// LINO
// CART PAGE
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    const container =
        document.getElementById("cartContainer");

    const summary =
        document.getElementById("cartSummary");

    if (!container) return;

    //----------------------------------------
    // GET CART
    //----------------------------------------

    function getCart() {

        return JSON.parse(

            localStorage.getItem("cart")

        ) || [];

    }

    //----------------------------------------
    // SAVE CART
    //----------------------------------------

    function saveCart(cart) {

        localStorage.setItem(

            "cart",

            JSON.stringify(cart)

        );

    }

    //----------------------------------------
    // FORMAT PRICE
    //----------------------------------------

    function formatPrice(price) {

        return Number(

            String(price)

                .replace(/[₹,\s]/g, "")

        ).toLocaleString("en-IN");

    }

    //----------------------------------------
    // RENDER CART
    //----------------------------------------

    function renderCart() {

        const cart = getCart();

        if (cart.length === 0) {

            container.innerHTML = `

                <div class="cart-empty">

                    <h2>

                        Your Bag is Empty

                    </h2>

                    <p>

                        Discover our luxury fragrances.

                    </p>

                    <a
                        href="/collections/"
                        class="btn-luxury">

                        Explore Collection

                    </a>

                </div>

            `;

            if (summary) {

                summary.innerHTML = "";

            }

            return;

        }

        let html = "";

                cart.forEach((item, index) => {

            html += `

                <div class="cart-card">

                    <!-- IMAGE -->

                    <div class="cart-image">

                        <img
                            src="${item.image}"
                            alt="${item.name}">

                    </div>

                    <!-- CONTENT -->

                    <div class="cart-content">

                        <h2>

                            ${item.name}

                        </h2>

                        <div class="cart-price">

                            ₹ ${formatPrice(item.price)}

                        </div>

                        <!-- QUANTITY -->

                        <div class="cart-quantity">

                            <button
                                class="qty-btn qty-minus"
                                data-index="${index}"
                                aria-label="Decrease quantity">

                                &minus;

                            </button>

                            <span data-qty-value="${index}">

                                ${item.quantity}

                            </span>

                            <button
                                class="qty-btn qty-plus"
                                data-index="${index}"
                                aria-label="Increase quantity">

                                &plus;

                            </button>

                        </div>

                        <!-- ACTION BUTTONS -->

                        <div class="cart-buttons">

                            <a
                                href="/product/${item.slug}/"
                                class="btn-primary">

                                View Product

                            </a>

                            <button
                                class="btn-secondary remove-cart"
                                data-index="${index}">

                                Remove

                            </button>

                        </div>

                    </div>

                </div>

            `;

        });

        container.innerHTML = html;

        renderSummary();

        //----------------------------------------
        // RENDER SUMMARY
        //----------------------------------------

        function renderSummary() {

            if (!summary) return;

            const cart = getCart();

            if (cart.length === 0) {

                summary.innerHTML = "";

                return;

            }

            let subtotal = 0;

            cart.forEach(item => {

                const rawPrice = String(item.price).replace(/[^\d.]/g, "");

                const price = parseFloat(rawPrice) || 0;

                subtotal += price * (item.quantity || 1);

            });

            summary.innerHTML = `

                <div class="cart-summary">

                    <h2>Order Summary</h2>

                    <div class="summary-row">

                        <span>Subtotal (${cart.length} item${cart.length !== 1 ? "s" : ""})</span>

                        <strong>₹ ${subtotal.toLocaleString("en-IN")}</strong>

                    </div>

                    <div class="summary-row">

                        <span>Shipping</span>

                        <strong style="color: #137333;">FREE</strong>

                    </div>

                    <div class="summary-row total">

                        <span>Total</span>

                        <strong>₹ ${subtotal.toLocaleString("en-IN")}</strong>

                    </div>

                    <button
                        type="button"
                        id="proceedCheckoutBtn"
                        class="checkout-btn">

                        Proceed to Checkout

                    </button>

                    <a href="/collections/" class="continue-shopping">

                        Continue Shopping

                    </a>

                </div>

            `;

            const checkoutBtn = document.getElementById("proceedCheckoutBtn");

            if (checkoutBtn) {

                checkoutBtn.addEventListener("click", (e) => {

                    e.preventDefault();

                    if (!window.IS_USER_AUTHENTICATED) {

                        if (typeof window.openAuthModal === "function") {

                            window.openAuthModal("checkout", "/checkout/");

                        } else {

                            window.location.href = "/login/?next=/checkout/";

                        }

                    } else {

                        window.location.href = "/checkout/";

                    }

                });

            }

        }

    

        //----------------------------------------
        // REMOVE
        //----------------------------------------

        document.querySelectorAll(".remove-cart").forEach(btn => {

            btn.addEventListener("click", () => {

                const cart = getCart();

                cart.splice(

                    Number(btn.dataset.index),

                    1

                );

                saveCart(cart);

                renderCart();

                if (window.updateCartCount) {

                    window.updateCartCount();

                }

            });

        });

        //----------------------------------------
        // INCREASE QUANTITY
        //----------------------------------------

        document.querySelectorAll(".qty-plus").forEach(btn => {

            btn.addEventListener("click", () => {

                const cart = getCart();

                const index = Number(btn.dataset.index);

                if (!cart[index]) return;

                cart[index].quantity += 1;

                saveCart(cart);

                renderCart();

                if (window.updateCartCount) {

                    window.updateCartCount();

                }

            });

        });

        //----------------------------------------
        // DECREASE QUANTITY
        //----------------------------------------

        document.querySelectorAll(".qty-minus").forEach(btn => {

            btn.addEventListener("click", () => {

                const cart = getCart();

                const index = Number(btn.dataset.index);

                if (!cart[index]) return;

                if (cart[index].quantity > 1) {

                    cart[index].quantity -= 1;

                } else {

                    cart.splice(index, 1);

                }

                saveCart(cart);

                renderCart();

                if (window.updateCartCount) {

                    window.updateCartCount();

                }

            });

        });

    }

    renderCart();

});
