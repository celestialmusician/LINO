//==================================================
// LINO - QUICK VIEW
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("quickView");

    if (!modal) return;

    const closeBtn = document.getElementById("quickClose");

    const quickImage = document.getElementById("quickImage");
    const quickTitle = document.getElementById("quickTitle");
    const quickSubtitle = document.getElementById("quickSubtitle");
    const quickPrice = document.getElementById("quickPrice");

    const cartBtn = document.getElementById("quickCartBtn");
    const buyNowBtn = document.getElementById("quickBuyNowBtn");
    const wishlistBtn = document.getElementById("quickWishlistBtn");

    const qtyMinus = document.getElementById("quickQtyMinus");
    const qtyPlus = document.getElementById("quickQtyPlus");
    const qtyValue = document.getElementById("quickQty");

    let quantity = 1;

    const buttons = document.querySelectorAll(".quick-view-btn");

    //--------------------------------------
    // OPEN QUICK VIEW
    //--------------------------------------

    buttons.forEach((button) => {

        button.addEventListener("click", (e) => {

            // Explore button normal navigation
            if (e.target.closest(".btn-luxury")) {
                return;
            }

            e.preventDefault();

            quickImage.src = button.dataset.image;
            quickTitle.textContent = button.dataset.name;
            quickSubtitle.textContent = button.dataset.subtitle;
            quickPrice.textContent = button.dataset.price;

            // Handle multi-image gallery thumbnails in Quick View modal
            const quickThumbsList = document.getElementById("quickThumbsList");
            if (quickThumbsList) {
                quickThumbsList.innerHTML = "";
                const rawImages = button.dataset.images || button.dataset.image;
                const imgArray = rawImages ? rawImages.split("|").filter(Boolean) : [button.dataset.image];

                if (imgArray.length > 1) {
                    imgArray.forEach((imgUrl, idx) => {
                        const thumbBtn = document.createElement("button");
                        thumbBtn.type = "button";
                        thumbBtn.className = `quick-thumb-item ${idx === 0 ? "active" : ""}`;
                        thumbBtn.innerHTML = `<img src="${imgUrl}" alt="Thumbnail ${idx + 1}">`;
                        thumbBtn.addEventListener("click", () => {
                            quickImage.style.opacity = "0.4";
                            setTimeout(() => {
                                quickImage.src = imgUrl;
                                quickImage.style.opacity = "1";
                            }, 120);
                            document.querySelectorAll(".quick-thumb-item").forEach(b => b.classList.remove("active"));
                            thumbBtn.classList.add("active");
                        });
                        quickThumbsList.appendChild(thumbBtn);
                    });
                }
            }

            if (cartBtn) {

                cartBtn.dataset.slug = button.dataset.slug;
                cartBtn.dataset.name = button.dataset.name;
                cartBtn.dataset.price = button.dataset.price;
                cartBtn.dataset.image = button.dataset.image;

                // Check if already in cart
                const cartItems = (typeof getCart === "function") ? getCart() : (JSON.parse(localStorage.getItem("cart")) || []);
                const isInCart = cartItems.some(item => item.slug === button.dataset.slug);
                if (isInCart) {
                    cartBtn.innerHTML = `<i class="fa-solid fa-bag-shopping"></i> View In Bag`;
                    cartBtn.classList.add("btn--in-cart");
                    cartBtn.dataset.inCart = "true";
                } else {
                    cartBtn.innerHTML = `<i class="fa-solid fa-bag-shopping"></i> Add To Bag`;
                    cartBtn.classList.remove("btn--in-cart");
                    cartBtn.dataset.inCart = "false";
                }

            }

            if (buyNowBtn) {

                buyNowBtn.dataset.slug = button.dataset.slug;
                buyNowBtn.dataset.name = button.dataset.name;
                buyNowBtn.dataset.price = button.dataset.price;
                buyNowBtn.dataset.image = button.dataset.image;

            }

            if (wishlistBtn) {

                wishlistBtn.dataset.slug = button.dataset.slug;
                wishlistBtn.dataset.name = button.dataset.name;
                wishlistBtn.dataset.price = button.dataset.price;
                wishlistBtn.dataset.image = button.dataset.image;

            }

            quantity = 1;
            qtyValue.textContent = quantity;

            //----------------------------------
            // Wishlist State
            //----------------------------------

            if (wishlistBtn) {

                let wishlist =
                    JSON.parse(localStorage.getItem("wishlist")) || [];

                const exists =
                    wishlist.find(item => item.slug === button.dataset.slug);

                if (exists) {

                    wishlistBtn.innerHTML =
                        `<i class="fa-solid fa-heart"></i>`;

                } else {

                    wishlistBtn.innerHTML =
                        `<i class="fa-regular fa-heart"></i>`;

                }

            }

            modal.classList.add("active");

            const whatsapp =
                document.getElementById("whatsappWidget");

            if (whatsapp) {

                whatsapp.classList.add("whatsapp-hidden");

            }

            if (window.lenis) {

                window.lenis.stop();

            }

            document.documentElement.classList.add("lenis-stopped");
            document.body.style.overflow = "hidden";

        });

    });

    //--------------------------------------
    // QUANTITY PLUS
    //--------------------------------------

    if (qtyPlus) {

        qtyPlus.addEventListener("click", () => {

            quantity++;
            qtyValue.textContent = quantity;

        });

    }

    //--------------------------------------
    // QUANTITY MINUS
    //--------------------------------------

    if (qtyMinus) {

        qtyMinus.addEventListener("click", () => {

            if (quantity > 1) {

                quantity--;
                qtyValue.textContent = quantity;

            }

        });

    }

    //--------------------------------------
    // ADD TO BAG
    //--------------------------------------

    if (cartBtn) {

        cartBtn.addEventListener("click", (e) => {

            e.preventDefault();

            if (cartBtn.dataset.inCart === "true") {
                // Second tap -> Navigate directly to shopping bag
                window.location.href = "/cart/";
                return;
            }

            const product = {
                name: cartBtn.dataset.name,
                price: cartBtn.dataset.price,
                image: cartBtn.dataset.image,
                slug: cartBtn.dataset.slug,
                quantity: quantity
            };

            if (typeof addToCart === "function") {
                addToCart(product);
            }

            cartBtn.innerHTML = `<i class="fa-solid fa-circle-check"></i> Added! View In Bag`;
            cartBtn.classList.add("btn--in-cart");
            cartBtn.dataset.inCart = "true";

            setTimeout(() => {
                cartBtn.innerHTML = `<i class="fa-solid fa-bag-shopping"></i> View In Bag`;
            }, 1200);

        });

    }

    //--------------------------------------
    // BUY NOW
    //--------------------------------------

    if (buyNowBtn) {

        buyNowBtn.addEventListener("click", (e) => {

            e.preventDefault();

            const product = {

                name: buyNowBtn.dataset.name,
                price: buyNowBtn.dataset.price,
                image: buyNowBtn.dataset.image,
                slug: buyNowBtn.dataset.slug,
                quantity: quantity

            };

            addToCart(product);

            if (!window.IS_USER_AUTHENTICATED) {
                closeModal();
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
    // WISHLIST (HEART ICON)
    //--------------------------------------

    if (wishlistBtn) {

        wishlistBtn.addEventListener("click", (e) => {

            e.preventDefault();

            let wishlist =
                JSON.parse(localStorage.getItem("wishlist")) || [];

            const product = {

                slug: wishlistBtn.dataset.slug,
                name: wishlistBtn.dataset.name,
                price: wishlistBtn.dataset.price,
                image: wishlistBtn.dataset.image

            };

            const exists =
                wishlist.find(item => item.slug === product.slug);

            if (exists) {

                wishlist = wishlist.filter(
                    item => item.slug !== product.slug
                );

                localStorage.setItem(
                    "wishlist",
                    JSON.stringify(wishlist)
                );

                wishlistBtn.innerHTML =
                    `<i class="fa-regular fa-heart"></i>`;

            }

            else {

                wishlist.push(product);

                localStorage.setItem(
                    "wishlist",
                    JSON.stringify(wishlist)
                );

                wishlistBtn.innerHTML =
                    `<i class="fa-solid fa-heart"></i>`;

            }

        });

    }

        //--------------------------------------
    // CLOSE MODAL
    //--------------------------------------

    function closeModal() {

        modal.classList.remove("active");

        const whatsapp =
            document.getElementById("whatsappWidget");

        if (whatsapp) {

            whatsapp.classList.remove("whatsapp-hidden");

        }

        if (window.lenis) {

            window.lenis.start();

        }

        document.documentElement.classList.remove("lenis-stopped");
        document.body.style.overflow = "";

    }

    //--------------------------------------
    // CLOSE BUTTON
    //--------------------------------------

    if (closeBtn) {

        closeBtn.addEventListener("click", closeModal);

    }

    //--------------------------------------
    // CLICK OUTSIDE MODAL
    //--------------------------------------

    modal.addEventListener("click", (e) => {

        if (e.target === modal) {

            closeModal();

        }

    });

    //--------------------------------------
    // ESC KEY
    //--------------------------------------

    document.addEventListener("keydown", (e) => {

        if (
            e.key === "Escape" &&
            modal.classList.contains("active")
        ) {

            closeModal();

        }

    });

});