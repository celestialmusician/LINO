//==================================================
// LINO
// CART MANAGER
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    //--------------------------------------
    // STORAGE KEY
    //--------------------------------------

    const CART_KEY = "cart";

    //--------------------------------------
    // GET CART
    //--------------------------------------

    function getCart() {

        return JSON.parse(
            localStorage.getItem(CART_KEY)
        ) || [];

    }

    //--------------------------------------
    // SAVE CART
    //--------------------------------------

    function saveCart(cart) {

        localStorage.setItem(
            CART_KEY,
            JSON.stringify(cart)
        );

    }

    //--------------------------------------
    // UPDATE CART COUNT
    //--------------------------------------

    function updateCartCount() {

        const badges =
            document.querySelectorAll(".cart-count");

        if (!badges.length) return;

        const cart = getCart();

        const total =
            cart.reduce(
                (sum, item) => sum + (item.quantity || 1),
                0
            );

        badges.forEach(badge => {

            badge.textContent = total;

        });

    }

        //--------------------------------------
    // ADD TO CART
    //--------------------------------------

    function addToCart(product) {

        let cart = getCart();

        const existing =
            cart.find(
                item => item.slug === product.slug
            );

        if (existing) {

            existing.quantity += product.quantity;

        } else {

            cart.push(product);

        }

        saveCart(cart);

        updateCartCount();

        return true;

    }

        //--------------------------------------
    // REMOVE FROM CART
    //--------------------------------------

    function removeFromCart(slug) {

        let cart =
            getCart().filter(
                item => item.slug !== slug
            );

        saveCart(cart);

        updateCartCount();

    }

    //--------------------------------------
    // CLEAR CART
    //--------------------------------------

    function clearCart() {

        localStorage.removeItem(CART_KEY);

        updateCartCount();

    }

    //--------------------------------------
    // GLOBAL FUNCTIONS
    //--------------------------------------

    window.getCart = getCart;

    window.addToCart = addToCart;

    window.removeFromCart = removeFromCart;

    window.clearCart = clearCart;

    window.updateCartCount = updateCartCount;

    //--------------------------------------
    // INITIALIZE
    //--------------------------------------

    updateCartCount();

});