//==================================================
// LINO - SCROLL ANIMATIONS
// Fade/slide-in on scroll using IntersectionObserver
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    //--------------------------------------
    // SELECTORS TO ANIMATE
    //--------------------------------------

    const animatedSelectors = [
        ".section-heading",
        ".section-label",
        ".section-title",
        ".section-description",
        ".collection-item",
        ".product-card",
        ".brand-content",
        ".brand-image",
        ".assurance-card",
        ".note-card",
        ".spec-item",
        ".story-content",
        ".feature-card",
        ".footer-col",
        ".collections-heading",
        ".hero-content",
        ".hero-media",
    ];

    //--------------------------------------
    // PREPARE ELEMENTS
    //--------------------------------------

    const elements = document.querySelectorAll(
        animatedSelectors.join(", ")
    );

    elements.forEach((el, index) => {

        el.style.opacity    = "0";
        el.style.transform  = "translateY(32px)";
        el.style.transition = `opacity 0.7s ease ${index * 0.05}s, transform 0.7s ease ${index * 0.05}s`;

    });

    //--------------------------------------
    // OBSERVER
    //--------------------------------------

    const observer = new IntersectionObserver(
        (entries) => {

            entries.forEach(entry => {

                if (entry.isIntersecting) {

                    entry.target.style.opacity   = "1";
                    entry.target.style.transform = "translateY(0)";

                    observer.unobserve(entry.target);

                }

            });

        },
        {
            threshold: 0.12,
            rootMargin: "0px 0px -40px 0px",
        }
    );

    elements.forEach(el => observer.observe(el));

});
