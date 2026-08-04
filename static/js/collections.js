//==================================================
// LINO - COLLECTIONS PAGE HELPERS
// Filter pill active state, sort, and card animations
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    //--------------------------------------
    // FILTER PILLS – active state toggle
    //--------------------------------------

    const filterBtns = document.querySelectorAll(".filter-btn");

    filterBtns.forEach(btn => {

        btn.addEventListener("click", () => {

            filterBtns.forEach(b => b.classList.remove("active"));

            btn.classList.add("active");

        });

    });

    //--------------------------------------
    // PRODUCT CARD – hover image scale
    //--------------------------------------

    const cards = document.querySelectorAll(".product-card");

    cards.forEach(card => {

        const img = card.querySelector("img");

        card.addEventListener("mouseenter", () => {
            if (img) img.style.transform = "scale(1.06)";
        });

        card.addEventListener("mouseleave", () => {
            if (img) img.style.transform = "scale(1)";
        });

    });

    //--------------------------------------
    // WISHLIST HEART on collection cards
    //--------------------------------------

    const wishlistBtns = document.querySelectorAll(".product-wishlist");

    wishlistBtns.forEach(btn => {

        const card = btn.closest(".product-card");

        if (!card) return;

        const slug = card.dataset.slug;

        // Initial state
        let wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];

        const icon = btn.querySelector("i");

        if (icon && wishlist.some(item => item.slug === slug)) {
            icon.classList.replace("fa-regular", "fa-solid");
        }

        btn.addEventListener("click", (e) => {

            e.stopPropagation();

            wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];

            const exists = wishlist.some(item => item.slug === slug);

            if (exists) {

                const updated = wishlist.filter(item => item.slug !== slug);
                localStorage.setItem("wishlist", JSON.stringify(updated));
                if (icon) icon.classList.replace("fa-solid", "fa-regular");

            } else {

                wishlist.push({
                    slug : card.dataset.slug,
                    name : card.dataset.name,
                    price: card.dataset.price,
                    image: card.dataset.image,
                });

                localStorage.setItem("wishlist", JSON.stringify(wishlist));

                if (icon) icon.classList.replace("fa-regular", "fa-solid");

            }

            // Update wishlist count badges
            const saved = JSON.parse(localStorage.getItem("wishlist")) || [];
            document.querySelectorAll(".wishlist-count").forEach(badge => {
                badge.textContent = saved.length;
            });

        });

    });

});
