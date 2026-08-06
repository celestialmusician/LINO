//==================================================
// LINO - CUSTOM CURSOR (HIGH PERFORMANCE & SPEED)
// Magnetic dot + soft ring following the pointer
//==================================================

document.addEventListener("DOMContentLoaded", () => {

    // Only on non-touch devices
    if (window.matchMedia("(hover: none)").matches) return;

    //--------------------------------------
    // CREATE CURSOR ELEMENTS
    //--------------------------------------

    const dot  = document.createElement("div");
    const ring = document.createElement("div");

    dot.className  = "cursor-dot";
    ring.className = "cursor-ring";

    document.body.appendChild(dot);
    document.body.appendChild(ring);

    //--------------------------------------
    // INJECT CURSOR STYLES
    //--------------------------------------

    const style = document.createElement("style");

    style.textContent = `
        *, *::before, *::after { cursor: none !important; }

        .cursor-dot {
            position: fixed;
            top: 0; left: 0;
            width: 8px; height: 8px;
            margin-left: -4px;
            margin-top: -4px;
            background: #b8955a;
            border-radius: 50%;
            pointer-events: none;
            z-index: 99999;
            will-change: transform;
            transition: width 0.15s ease-out, height 0.15s ease-out, background 0.15s ease-out, opacity 0.15s ease-out;
        }

        .cursor-ring {
            position: fixed;
            top: 0; left: 0;
            width: 36px; height: 36px;
            margin-left: -18px;
            margin-top: -18px;
            border: 1.5px solid rgba(184, 149, 90, 0.5);
            border-radius: 50%;
            pointer-events: none;
            z-index: 99998;
            will-change: transform;
            transition: width 0.2s ease-out, height 0.2s ease-out, border-color 0.2s ease-out, opacity 0.2s ease-out;
        }

        .cursor-dot.is-hovering {
            width: 12px; height: 12px;
            margin-left: -6px;
            margin-top: -6px;
            background: #c9a96e;
        }

        .cursor-ring.is-hovering {
            width: 52px; height: 52px;
            margin-left: -26px;
            margin-top: -26px;
            border-color: rgba(184, 149, 90, 0.8);
        }

        .cursor-dot.is-clicking {
            transform: translate3d(var(--cx, -100px), var(--cy, -100px), 0) scale(0.6) !important;
        }
    `;

    document.head.appendChild(style);

    //--------------------------------------
    // TRACK MOUSE POSITION
    //--------------------------------------

    let mouseX = -100, mouseY = -100;
    let ringX  = -100, ringY  = -100;

    document.addEventListener("mousemove", (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;

        // Instant dot positioning using transform
        dot.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;
        dot.style.setProperty("--cx", `${mouseX}px`);
        dot.style.setProperty("--cy", `${mouseY}px`);
    }, { passive: true });

    //--------------------------------------
    // SMOOTH FAST RING FOLLOW (rAF)
    //--------------------------------------

    function animateRing() {
        // High speed smooth interpolation (0.35 factor for fast response)
        ringX += (mouseX - ringX) * 0.35;
        ringY += (mouseY - ringY) * 0.35;

        ring.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`;

        requestAnimationFrame(animateRing);
    }

    requestAnimationFrame(animateRing);

    //--------------------------------------
    // HOVER STATE WITH EVENT DELEGATION
    //--------------------------------------

    const hoverSelector = "a, button, .product-card, .quick-view-btn, .collection-item, input, textarea, select, label, [role='button']";

    document.addEventListener("mouseover", (e) => {
        if (e.target.closest && e.target.closest(hoverSelector)) {
            dot.classList.add("is-hovering");
            ring.classList.add("is-hovering");
        }
    }, { passive: true });

    document.addEventListener("mouseout", (e) => {
        if (e.target.closest && e.target.closest(hoverSelector)) {
            dot.classList.remove("is-hovering");
            ring.classList.remove("is-hovering");
        }
    }, { passive: true });

    //--------------------------------------
    // CLICK STATE
    //--------------------------------------

    document.addEventListener("mousedown", () => dot.classList.add("is-clicking"));
    document.addEventListener("mouseup",   () => dot.classList.remove("is-clicking"));

    //--------------------------------------
    // HIDE WHEN LEAVING WINDOW
    //--------------------------------------

    document.addEventListener("mouseleave", () => {
        dot.style.opacity  = "0";
        ring.style.opacity = "0";
    });

    document.addEventListener("mouseenter", () => {
        dot.style.opacity  = "1";
        ring.style.opacity = "1";
    });

});

