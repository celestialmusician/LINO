//==================================================
// LINO - PRODUCT DETAIL PAGE
// Handles: Quantity selector, Add to Cart, Wishlist
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    //--------------------------------------
    // ELEMENTS
    //--------------------------------------

    const addToCartBtn    = document.getElementById("addToCartBtn");
    const wishlistBtn     = document.querySelector(".wishlist-detail-btn");

    //--------------------------------------
    // QUANTITY SELECTOR
    //--------------------------------------

    let quantity = 1;

    const qtyDisplay = document.querySelector(".qty-value");
    const qtyMinus   = document.querySelector(".qty-minus");
    const qtyPlus    = document.querySelector(".qty-plus");

    if (qtyMinus) {
        qtyMinus.addEventListener("click", () => {
            if (quantity > 1) {
                quantity--;
                if (qtyDisplay) qtyDisplay.textContent = quantity;
            }
        });
    }

    if (qtyPlus) {
        qtyPlus.addEventListener("click", () => {
            quantity++;
            if (qtyDisplay) qtyDisplay.textContent = quantity;
        });
    }

    //--------------------------------------
    // ADD TO CART
    //--------------------------------------

    if (addToCartBtn) {
        const slug = addToCartBtn.dataset.slug;

        // Check if item is already in cart on page load
        if (typeof getCart === "function") {
            const cart = getCart();
            if (cart.some(item => item.slug === slug)) {
                addToCartBtn.innerHTML = `<i class="fa-solid fa-bag-shopping"></i> View In Bag`;
                addToCartBtn.classList.add("btn--in-cart");
                addToCartBtn.dataset.inCart = "true";
            }
        }

        addToCartBtn.addEventListener("click", () => {
            if (addToCartBtn.dataset.inCart === "true") {
                // Second tap -> Navigate directly to shopping cart page
                window.location.href = "/cart/";
                return;
            }

            const product = {
                name    : addToCartBtn.dataset.name,
                price   : addToCartBtn.dataset.price,
                image   : addToCartBtn.dataset.image,
                slug    : addToCartBtn.dataset.slug,
                quantity: quantity,
            };

            if (typeof addToCart === "function") {
                addToCart(product);
            }

            // Visual feedback & state change to "View In Bag"
            addToCartBtn.innerHTML = `<i class="fa-solid fa-circle-check"></i> Added! View In Bag`;
            addToCartBtn.classList.add("btn--in-cart");
            addToCartBtn.dataset.inCart = "true";

            setTimeout(() => {
                addToCartBtn.innerHTML = `<i class="fa-solid fa-bag-shopping"></i> View In Bag`;
            }, 1200);
        });
    }

    //--------------------------------------
    // BUY NOW
    //--------------------------------------

    const buyNowDetailBtn = document.getElementById("buyNowDetailBtn");
    if (buyNowDetailBtn) {
        buyNowDetailBtn.addEventListener("click", () => {
            const product = {
                name    : buyNowDetailBtn.dataset.name,
                price   : buyNowDetailBtn.dataset.price,
                image   : buyNowDetailBtn.dataset.image,
                slug    : buyNowDetailBtn.dataset.slug,
                quantity: quantity,
            };

            if (typeof addToCart === "function") {
                addToCart(product);
            }

            if (!window.IS_USER_AUTHENTICATED) {
                if (typeof window.openAuthModal === "function") {
                    window.openAuthModal("buy_now", "/checkout/");
                } else {
                    window.location.href = "/login/?next=/checkout/";
                }
            } else {
                window.location.href = "/checkout/";
            }
        });
    }

    //--------------------------------------
    // WISHLIST TOGGLE
    //--------------------------------------

    if (wishlistBtn) {

        const slug = wishlistBtn.dataset.slug;

        // Set initial state
        let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];
        const alreadySaved = wishlist.some(item => item.slug === slug);

        if (alreadySaved) {
            wishlistBtn.innerHTML = `<i class="fa-solid fa-heart"></i> Wishlisted`;
        }

        wishlistBtn.addEventListener("click", () => {

            wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];

            const exists = wishlist.some(item => item.slug === slug);

            if (exists) {

                // Remove from wishlist
                const updated = wishlist.filter(item => item.slug !== slug);
                localStorage.setItem("wishlist", JSON.stringify(updated));
                wishlistBtn.innerHTML = `<i class="fa-regular fa-heart"></i> Wishlist`;

            } else {

                // Add to wishlist
                wishlist.push({
                    slug : wishlistBtn.dataset.slug,
                    name : wishlistBtn.dataset.name,
                    price: wishlistBtn.dataset.price,
                    image: wishlistBtn.dataset.image,
                });
                localStorage.setItem("wishlist", JSON.stringify(wishlist));
                wishlistBtn.innerHTML = `<i class="fa-solid fa-heart"></i> Wishlisted`;

            }

            // Update count badge
            const saved = JSON.parse(localStorage.getItem("wishlist")) || [];
            document.querySelectorAll(".wishlist-count").forEach(badge => {
                badge.textContent = saved.length;
            });

        });

    }

});
