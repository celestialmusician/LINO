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

        addToCartBtn.addEventListener("click", () => {

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

            // Visual feedback
            addToCartBtn.innerHTML = `<i class="fa-solid fa-circle-check"></i> Added To Bag`;
            addToCartBtn.classList.add("btn--success");

            setTimeout(() => {
                addToCartBtn.innerHTML = `<i class="fa-solid fa-bag-shopping"></i> Add To Bag`;
                addToCartBtn.classList.remove("btn--success");
            }, 1800);

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
