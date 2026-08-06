document.addEventListener("DOMContentLoaded", () => {
    const widget = document.getElementById("whatsappWidget");
    const closeBtn = document.getElementById("whatsappClose");
    const card = document.getElementById("whatsappCard");

    if (!widget) return;

    // Check if card was previously dismissed in this session
    if (sessionStorage.getItem("whatsapp_card_dismissed") === "true" && card) {
        card.classList.add("whatsapp-card-dismissed");
    }

    // Dismiss close button click handler
    if (closeBtn && card) {
        closeBtn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            card.style.transition = "all 0.35s cubic-bezier(0.16, 1, 0.3, 1)";
            card.style.opacity = "0";
            card.style.transform = "scale(0.8) translateY(15px)";
            setTimeout(() => {
                card.classList.add("whatsapp-card-dismissed");
            }, 350);
            sessionStorage.setItem("whatsapp_card_dismissed", "true");
        });
    }

    // Initial entrance animation
    widget.style.opacity = "0";
    widget.style.transform = "translateY(30px)";

    setTimeout(() => {
        widget.style.transition = "opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)";
        widget.style.opacity = "1";
        widget.style.transform = "translateY(0)";
    }, 600);
});