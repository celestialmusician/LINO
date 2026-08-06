//==================================================
// LINO - SCROLL ANIMATIONS
// Fade/slide-in on scroll using IntersectionObserver
//==================================================

document.addEventListener("DOMContentLoaded", () => {
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
        ".footer-links",
        ".collections-heading",
        ".hero-content",
        ".hero-media",
    ];

    const elements = document.querySelectorAll(animatedSelectors.join(", "));

    elements.forEach((el) => {
        const parent = el.parentElement;
        const index = parent ? Array.from(parent.children).indexOf(el) : 0;
        const delay = Math.min(index * 0.08, 0.35);

        el.style.opacity = "0";
        el.style.transform = "translateY(24px)";
        el.style.transition = `opacity 0.75s cubic-bezier(0.16, 1, 0.3, 1) ${delay}s, transform 0.75s cubic-bezier(0.16, 1, 0.3, 1) ${delay}s`;
    });

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    el.style.opacity = "1";
                    el.style.transform = "translateY(0)";

                    // Clear inline transition after animation completes so hover styles function cleanly
                    setTimeout(() => {
                        el.style.opacity = "";
                        el.style.transform = "";
                        el.style.transition = "";
                    }, 1000);

                    observer.unobserve(el);
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: "0px 0px -30px 0px",
        }
    );

    elements.forEach(el => observer.observe(el));
});
