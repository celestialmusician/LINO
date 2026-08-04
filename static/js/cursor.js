//==================================================
// LINO - CUSTOM CURSOR
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
            background: #b8955a;
            border-radius: 50%;
            pointer-events: none;
            z-index: 99999;
            transform: translate(-50%, -50%);
            transition: width 0.2s, height 0.2s, background 0.2s;
            will-change: transform;
        }

        .cursor-ring {
            position: fixed;
            top: 0; left: 0;
            width: 36px; height: 36px;
            border: 1.5px solid rgba(184, 149, 90, 0.5);
            border-radius: 50%;
            pointer-events: none;
            z-index: 99998;
            transform: translate(-50%, -50%);
            transition: width 0.3s, height 0.3s, border-color 0.3s;
            will-change: transform;
        }

        .cursor-dot.is-hovering {
            width: 12px; height: 12px;
            background: #c9a96e;
        }

        .cursor-ring.is-hovering {
            width: 52px; height: 52px;
            border-color: rgba(184, 149, 90, 0.8);
        }

        .cursor-dot.is-clicking {
            transform: translate(-50%, -50%) scale(0.6);
        }
    `;

    document.head.appendChild(style);

    //--------------------------------------
    // TRACK MOUSE POSITION
    //--------------------------------------

    let mouseX = 0, mouseY = 0;
    let ringX  = 0, ringY  = 0;

    document.addEventListener("mousemove", (e) => {

        mouseX = e.clientX;
        mouseY = e.clientY;

        dot.style.left = mouseX + "px";
        dot.style.top  = mouseY + "px";

    });

    //--------------------------------------
    // SMOOTH RING FOLLOW (rAF)
    //--------------------------------------

    function animateRing() {

        ringX += (mouseX - ringX) * 0.14;
        ringY += (mouseY - ringY) * 0.14;

        ring.style.left = ringX + "px";
        ring.style.top  = ringY + "px";

        requestAnimationFrame(animateRing);

    }

    animateRing();

    //--------------------------------------
    // HOVER STATE ON INTERACTIVE ELEMENTS
    //--------------------------------------

    const hoverTargets = "a, button, .product-card, .quick-view-btn, .collection-item, input, textarea, select, label";

    document.querySelectorAll(hoverTargets).forEach(el => {

        el.addEventListener("mouseenter", () => {
            dot.classList.add("is-hovering");
            ring.classList.add("is-hovering");
        });

        el.addEventListener("mouseleave", () => {
            dot.classList.remove("is-hovering");
            ring.classList.remove("is-hovering");
        });

    });

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
