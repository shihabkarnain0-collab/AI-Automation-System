"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const progress = document.getElementById("scrollProgress");
    const menuToggle = document.getElementById("menuToggle");
    const navigation = document.getElementById("navigation");
    const year = document.getElementById("currentYear");

    // Automatically update the copyright year.
    if (year) {
        year.textContent = new Date().getFullYear();
    }

    // Reading progress indicator.
    function updateProgress() {
        if (!progress) return;

        const scrollable = document.documentElement.scrollHeight - window.innerHeight;
        const percentage = scrollable > 0
            ? (window.scrollY / scrollable) * 100
            : 0;

        progress.style.width = `${Math.min(100, percentage)}%`;
    }

    window.addEventListener("scroll", updateProgress, { passive: true });
    updateProgress();

    // Accessible mobile navigation.
    function closeMenu() {
        if (!menuToggle || !navigation) return;

        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "Open navigation");
        navigation.classList.remove("open");
        document.body.classList.remove("menu-open");
    }

    if (menuToggle && navigation) {
        menuToggle.addEventListener("click", () => {
            const isOpen = menuToggle.getAttribute("aria-expanded") === "true";

            menuToggle.setAttribute("aria-expanded", String(!isOpen));
            menuToggle.setAttribute(
                "aria-label",
                isOpen ? "Open navigation" : "Close navigation"
            );

            navigation.classList.toggle("open", !isOpen);
            document.body.classList.toggle("menu-open", !isOpen);
        });

        navigation.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", closeMenu);
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") closeMenu();
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth > 700) closeMenu();
        });
    }

    // Reveal elements as they enter the viewport.
    const revealElements = document.querySelectorAll(".reveal");

    if ("IntersectionObserver" in window) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: "0px 0px -35px 0px"
        });

        revealElements.forEach((element) => revealObserver.observe(element));
    } else {
        revealElements.forEach((element) => element.classList.add("is-visible"));
    }

    // Subtle pointer response for the orbital artwork.
    const orbitScene = document.querySelector(".orbit-scene");

    if (orbitScene && window.matchMedia("(hover: hover)").matches) {
        let animationFrame = null;

        document.addEventListener("pointermove", (event) => {
            if (animationFrame !== null) {
                cancelAnimationFrame(animationFrame);
            }

            animationFrame = requestAnimationFrame(() => {
                const x = (event.clientX / window.innerWidth - 0.5) * 10;
                const y = (event.clientY / window.innerHeight - 0.5) * 10;

                orbitScene.style.translate = `${x}px ${y}px`;
                animationFrame = null;
            });
        }, { passive: true });
    }

    // Respect reduced-motion preferences.
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        document.documentElement.classList.add("reduced-motion");
    }

    console.info("THE OBSERVER initialized.");
});
