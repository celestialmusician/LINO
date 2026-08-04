//==================================================
// LINO - WISHLIST COUNT
// Updates all wishlist badge elements from localStorage
//==================================================

(function updateWishlistCount() {

    const wishlist = JSON.parse(localStorage.getItem("wishlist")) || [];

    const count = wishlist.length;

    document.querySelectorAll(".wishlist-count").forEach(badge => {

        badge.textContent = count;

        badge.style.display = count > 0 ? "flex" : "none";

    });

})();

// Also update on storage changes (e.g. another tab)
window.addEventListener("storage", (e) => {

    if (e.key === "wishlist") {

        const wishlist = JSON.parse(e.newValue || "[]");

        document.querySelectorAll(".wishlist-count").forEach(badge => {

            badge.textContent = wishlist.length;

            badge.style.display = wishlist.length > 0 ? "flex" : "none";

        });

    }

});
