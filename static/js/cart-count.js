document.addEventListener("DOMContentLoaded", () => {

    const badges =
        document.querySelectorAll(".cart-count");

    if (!badges.length) return;

    const cart =
        JSON.parse(
            localStorage.getItem("cart")
        ) || [];

    let total = 0;

    cart.forEach(item => {

        total += item.quantity || 1;

    });

    badges.forEach(badge => {

        badge.textContent = total;

    });

});