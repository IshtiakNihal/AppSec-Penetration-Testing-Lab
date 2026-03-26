document.addEventListener("DOMContentLoaded", () => {
    const badge = document.createElement("div");
    badge.id = "dom-xss-badge";
    badge.style.marginTop = "12px";
    badge.innerHTML = window.name;
    document.body.appendChild(badge);

    if (window.location.hash) {
        const target = document.getElementById("preview");
        if (target) {
            target.innerHTML = window.location.hash.substring(1);
        }
    }
});
