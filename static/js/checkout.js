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
    // PREMIUM PAYMENT DROPDOWN CONTROLLER
    //--------------------------------------

    const dropdownWrapper = document.getElementById('paymentDropdownWrapper');
    const trigger         = document.getElementById('paymentDropdownTrigger');
    const menu            = document.getElementById('paymentDropdownMenu');
    const hiddenInput     = document.getElementById('paymentMethodInput');
    const errorMsg        = document.getElementById('paymentErrorMsg');

    const selectedIcon     = document.getElementById('selectedPaymentIcon');
    const selectedTitle    = document.getElementById('selectedPaymentTitle');
    const selectedSubtitle = document.getElementById('selectedPaymentSubtitle');

    if (dropdownWrapper && trigger && menu && hiddenInput) {
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = dropdownWrapper.classList.contains('open');
            dropdownWrapper.classList.toggle('open');
            trigger.setAttribute('aria-expanded', !isOpen);
        });

        const options = menu.querySelectorAll('.premium-option');
        options.forEach(opt => {
            opt.addEventListener('click', (e) => {
                e.stopPropagation();
                const val = opt.dataset.value;
                const title = opt.dataset.title;
                const subtitle = opt.dataset.subtitle;
                const iconClass = opt.dataset.icon;

                hiddenInput.value = val;

                if (selectedTitle) selectedTitle.textContent = title;
                if (selectedSubtitle) selectedSubtitle.textContent = subtitle;
                if (selectedIcon) selectedIcon.innerHTML = `<i class="${iconClass}"></i>`;

                // Remove placeholder styling
                trigger.classList.remove('is-placeholder');

                // Clear error status
                dropdownWrapper.classList.remove('has-error');
                if (errorMsg) errorMsg.style.display = 'none';

                options.forEach(o => o.classList.remove('item-selected'));
                opt.classList.add('item-selected');

                dropdownWrapper.classList.remove('open');
                trigger.setAttribute('aria-expanded', 'false');
            });
        });

        document.addEventListener('click', (e) => {
            if (!dropdownWrapper.contains(e.target)) {
                dropdownWrapper.classList.remove('open');
                trigger.setAttribute('aria-expanded', 'false');
            }
        });
    }

    //--------------------------------------
    // EMPTY CART CHECK
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
    // FORM SUBMIT → handle mandatory payment & payment options
    //--------------------------------------

    if (form) {

        form.addEventListener("submit", (e) => {

            if (!window.IS_USER_AUTHENTICATED) {
                e.preventDefault();
                if (typeof window.openAuthModal === "function") {
                    window.openAuthModal("checkout", "/checkout/");
                } else {
                    window.location.href = "/login/?next=/checkout/";
                }
                return;
            }

            if (cart.length === 0) {
                e.preventDefault();
                alert("Your cart is empty. Please add items before checking out.");
                return;
            }

            // MANDATORY PAYMENT SELECTION CHECK
            const paymentMethod = hiddenInput ? hiddenInput.value.trim() : "";
            if (!paymentMethod) {
                e.preventDefault();

                if (errorMsg) {
                    errorMsg.style.display = "flex";
                }

                if (dropdownWrapper) {
                    dropdownWrapper.classList.add("has-error");
                    dropdownWrapper.scrollIntoView({ behavior: "smooth", block: "center" });
                    dropdownWrapper.classList.add("open");
                    if (trigger) trigger.setAttribute("aria-expanded", "true");
                }
                return;
            }

            // Populate hidden field with cart JSON
            if (cartDataInput) {
                cartDataInput.value = JSON.stringify(cart);
            }

            if (paymentMethod === "upi" || paymentMethod === "card") {
                e.preventDefault();

                const submitBtn = document.getElementById("placeOrderBtn");
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = "Processing Payment...";
                }

                const formData = new FormData(form);
                formData.append("is_online_payment", "true");

                fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "RAZORPAY_INIT") {
                        openRazorpayModal(data, submitBtn);
                    } else if (data.status === "SUCCESS") {
                        localStorage.removeItem("cart");
                        window.location.href = data.redirect_url;
                    } else {
                        alert(data.message || "Error creating payment order.");
                        if (submitBtn) {
                            submitBtn.disabled = false;
                            submitBtn.textContent = "Place Order";
                        }
                    }
                })
                .catch(err => {
                    alert("Order processing error: " + err);
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = "Place Order";
                    }
                });
            } else {
                // COD Flow
                sessionStorage.setItem("clearCartOnLoad", "true");
            }

        });

    }

    function openRazorpayModal(rzpData, submitBtn) {
        const options = {
            "key": rzpData.razorpay_key_id,
            "amount": rzpData.amount,
            "currency": "INR",
            "name": "LINO Luxury Perfumes",
            "description": `Order #${rzpData.order_id}`,
            "image": "/static/images/logo/lino-logo-white.png",
            "order_id": rzpData.razorpay_order_id,
            "handler": function (response) {
                if (submitBtn) submitBtn.textContent = "Verifying Payment...";

                fetch("/razorpay-verify/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: new URLSearchParams({
                        "razorpay_order_id": response.razorpay_order_id || rzpData.razorpay_order_id,
                        "razorpay_payment_id": response.razorpay_payment_id || `pay_dummy_${rzpData.order_id}`,
                        "razorpay_signature": response.razorpay_signature || "dummy_signature_ok"
                    })
                })
                .then(res => res.json())
                .then(verRes => {
                    if (verRes.status === "SUCCESS") {
                        localStorage.removeItem("cart");
                        window.location.href = verRes.redirect_url;
                    } else {
                        alert("Payment verification failed: " + verRes.message);
                        if (submitBtn) {
                            submitBtn.disabled = false;
                            submitBtn.textContent = "Place Order";
                        }
                    }
                })
                .catch(err => {
                    alert("Verification error: " + err);
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = "Place Order";
                    }
                });
            },
            "prefill": {
                "name": rzpData.name,
                "email": rzpData.email,
                "contact": rzpData.phone
            },
            "theme": {
                "color": "#D4AF37"
            },
            "modal": {
                "ondismiss": function() {
                    alert("Payment modal closed. You can complete payment or switch to Cash on Delivery.");
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = "Place Order";
                    }
                }
            }
        };

        if (typeof Razorpay !== "undefined" && !rzpData.razorpay_key_id.startsWith("rzp_test_lino_dummy")) {
            const rzp = new Razorpay(options);
            rzp.open();
        } else {
            // Interactive Test / Dummy Mode Simulation Modal
            setTimeout(() => {
                if (confirm(`[LINO TEST MODE PAYMENT]\n\nSimulating Razorpay Payment Gateway Modal\n\nOrder ID: #${rzpData.order_id}\nTotal Amount: ₹${(rzpData.amount / 100).toLocaleString('en-IN')}\nPayment Method: Online (UPI / Cards)\n\nClick OK to simulate SUCCESSFUL PAYMENT.`)) {
                    options.handler({
                        razorpay_order_id: rzpData.razorpay_order_id,
                        razorpay_payment_id: `pay_simulated_${rzpData.order_id}`,
                        razorpay_signature: `sig_simulated_${rzpData.order_id}`
                    });
                } else {
                    options.modal.ondismiss();
                }
            }, 300);
        }
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