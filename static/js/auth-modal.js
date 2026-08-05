//==================================================
// LINO - MANDATORY AUTHENTICATION MODAL JS
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    const modalOverlay = document.getElementById("mandatoryAuthModal");
    if (!modalOverlay) return;

    const closeBtn = document.getElementById("authModalClose");
    const tabLoginBtn = document.getElementById("tabLoginBtn");
    const tabRegisterBtn = document.getElementById("tabRegisterBtn");

    const panelLogin = document.getElementById("authPanelLogin");
    const panelRegister = document.getElementById("authPanelRegister");

    const loginForm = document.getElementById("authModalLoginForm");
    const registerForm = document.getElementById("authModalRegisterForm");
    const alertBox = document.getElementById("authModalAlert");

    let pendingRedirectUrl = "/checkout/";

    //--------------------------------------
    // TAB SWITCHING
    //--------------------------------------
    window.switchAuthTab = function(tab) {
        hideAlert();
        if (tab === "login") {
            tabLoginBtn.classList.add("active");
            tabRegisterBtn.classList.remove("active");
            panelLogin.classList.add("active");
            panelRegister.classList.remove("active");
        } else {
            tabRegisterBtn.classList.add("active");
            tabLoginBtn.classList.remove("active");
            panelRegister.classList.add("active");
            panelLogin.classList.remove("active");
        }
    };

    if (tabLoginBtn) tabLoginBtn.addEventListener("click", () => switchAuthTab("login"));
    if (tabRegisterBtn) tabRegisterBtn.addEventListener("click", () => switchAuthTab("register"));

    //--------------------------------------
    // OPEN / CLOSE MODAL
    //--------------------------------------
    window.openAuthModal = function(reason = "checkout", redirectUrl = "/checkout/", tab = "login") {
        pendingRedirectUrl = redirectUrl || "/checkout/";

        // Update hidden next input fields
        document.querySelectorAll('#mandatoryAuthModal input[name="next"]').forEach(inp => {
            inp.value = pendingRedirectUrl;
        });

        // Update title/subtitle based on context
        const titleEl = document.getElementById("authModalTitle");
        const subtitleEl = document.getElementById("authModalSubtitle");

        if (reason === "checkout" || reason === "buy_now") {
            if (titleEl) titleEl.textContent = "Sign In Required";
            if (subtitleEl) subtitleEl.textContent = "Please sign in or create an account to complete your perfume order.";
        } else if (reason === "profile") {
            if (titleEl) titleEl.textContent = "Account Access";
            if (subtitleEl) subtitleEl.textContent = "Please sign in or create an account to access your luxury profile.";
        }

        switchAuthTab(tab);
        modalOverlay.classList.add("active");

        if (window.lenis) window.lenis.stop();
        document.documentElement.classList.add("lenis-stopped");
        document.body.style.overflow = "hidden";
    };

    window.closeAuthModal = function() {
        modalOverlay.classList.remove("active");
        if (window.lenis) window.lenis.start();
        document.documentElement.classList.remove("lenis-stopped");
        document.body.style.overflow = "";
    };

    if (closeBtn) closeBtn.addEventListener("click", closeAuthModal);

    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) closeAuthModal();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modalOverlay.classList.contains("active")) {
            closeAuthModal();
        }
    });

    //--------------------------------------
    // ALERT BANNERS
    //--------------------------------------
    function showAlert(msg, type = "error") {
        if (!alertBox) return;
        alertBox.className = `auth-modal-alert auth-modal-alert--${type}`;
        alertBox.textContent = msg;
        alertBox.style.display = "block";
    }

    function hideAlert() {
        if (alertBox) alertBox.style.display = "none";
    }

    //--------------------------------------
    // AJAX LOGIN FORM SUBMIT
    //--------------------------------------
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            hideAlert();

            const submitBtn = document.getElementById("authLoginSubmitBtn");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.querySelector("span").textContent = "Signing in...";
            }

            const formData = new FormData(loginForm);
            fetch(loginForm.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.json().catch(() => ({ status: "ERROR", message: "Server response error." })))
            .then(data => {
                if (data.status === "SUCCESS") {
                    window.IS_USER_AUTHENTICATED = true;
                    showAlert(data.message || "Signed in successfully!", "success");

                    setTimeout(() => {
                        window.location.href = data.redirect || pendingRedirectUrl;
                    }, 600);
                } else {
                    showAlert(data.message || "Invalid credentials. Please try again.", "error");
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.querySelector("span").textContent = "Sign In to Continue";
                    }
                }
            })
            .catch(err => {
                showAlert("Network error during sign in.", "error");
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.querySelector("span").textContent = "Sign In to Continue";
                }
            });
        });
    }

    //--------------------------------------
    // AJAX REGISTER FORM SUBMIT
    //--------------------------------------
    if (registerForm) {
        registerForm.addEventListener("submit", (e) => {
            e.preventDefault();
            hideAlert();

            const pass = registerForm.querySelector('[name="password"]').value;
            const confirmPass = registerForm.querySelector('[name="confirm_password"]').value;

            if (pass !== confirmPass) {
                showAlert("Passwords do not match.", "error");
                return;
            }

            const submitBtn = document.getElementById("authRegisterSubmitBtn");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.querySelector("span").textContent = "Creating Account...";
            }

            const formData = new FormData(registerForm);
            fetch(registerForm.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.json().catch(() => ({ status: "ERROR", message: "Server response error." })))
            .then(data => {
                if (data.status === "SUCCESS") {
                    window.IS_USER_AUTHENTICATED = true;
                    showAlert(data.message || "Account created successfully!", "success");

                    setTimeout(() => {
                        window.location.href = data.redirect || pendingRedirectUrl;
                    }, 600);
                } else {
                    showAlert(data.message || "Error creating account.", "error");
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.querySelector("span").textContent = "Create Account & Place Order";
                    }
                }
            })
            .catch(err => {
                showAlert("Network error during account registration.", "error");
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.querySelector("span").textContent = "Create Account & Place Order";
                }
            });
        });
    }

    //--------------------------------------
    // AUTO OPEN MODAL IF ON CHECKOUT OR IF REQUIRE_AUTH IS SET
    //--------------------------------------
    if (window.REQUIRE_MANDATORY_AUTH && !window.IS_USER_AUTHENTICATED) {
        setTimeout(() => {
            window.openAuthModal("checkout", "/checkout/");
        }, 200);
    }

});
