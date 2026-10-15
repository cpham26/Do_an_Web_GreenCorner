/**
 * Green Corner - Astra Botanical Engine & Living Space Exhibition Controller
 * Centerpiece: Architectural Bonsai Tree with Living Bio-luminescent Spores & Fireflies
 * Inspired by OpenAI GPT-6 Astra & High-end Botanical Design
 * 60 FPS, Zero Mouse Tilt, Mobile-friendly
 */

(() => {
    "use strict";

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* =========================================================================
       1. BOTANICAL AMBIENT SPORES CANVAS (Luminous Fireflies around Center Tree)
       ========================================================================= */
    const initAstraTreeAmbience = () => {
        const canvas = document.getElementById("astra-tree-ambient-canvas");
        if (!canvas) return;

        const ctx = canvas.getContext("2d", { alpha: true });
        if (!ctx) return;

        let width = 0;
        let height = 0;
        let dpr = Math.min(window.devicePixelRatio || 1, 2);
        let animationFrameId = null;
        let isVisible = true;
        let isTabActive = true;

        // Mouse coordinates for gentle spore interaction
        let mouseX = -9999;
        let mouseY = -9999;

        const SPORE_COUNT = window.innerWidth < 768 ? 45 : 95;
        const spores = [];

        const resetSpore = (p, fullRandom = false) => {
            p.x = width * 0.5 + (Math.random() - 0.5) * (width * 0.72);
            p.y = fullRandom ? Math.random() * height : height * 0.88 + Math.random() * (height * 0.12);
            p.vx = (Math.random() - 0.5) * 0.35;
            p.vy = -(Math.random() * 0.45 + 0.25); // Float upward
            p.size = Math.random() * 2.2 + 0.9;
            p.maxAlpha = Math.random() * 0.55 + 0.35;
            p.alpha = fullRandom ? Math.random() * p.maxAlpha : 0;
            p.fadeIn = true;
            p.waveOffset = Math.random() * Math.PI * 2;
            p.waveSpeed = Math.random() * 0.02 + 0.01;

            const roll = Math.random();
            if (roll < 0.50) {
                p.color = "mint"; // #34d399
            } else if (roll < 0.80) {
                p.color = "emerald"; // #10b981
            } else if (roll < 0.92) {
                p.color = "gold"; // #fcd34d
            } else {
                p.color = "white"; // #ffffff
            }
        };

        const resize = () => {
            const rect = canvas.getBoundingClientRect();
            width = rect.width || canvas.parentElement.clientWidth || 400;
            height = rect.height || canvas.parentElement.clientHeight || 400;
            dpr = Math.min(window.devicePixelRatio || 1, 2);

            canvas.width = Math.round(width * dpr);
            canvas.height = Math.round(height * dpr);
            ctx.scale(dpr, dpr);

            if (spores.length === 0) {
                for (let i = 0; i < SPORE_COUNT; i++) {
                    const p = {};
                    resetSpore(p, true);
                    spores.push(p);
                }
            }
        };

        resize();
        window.addEventListener("resize", resize, { passive: true });

        const onMouseMove = (e) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        };

        const onMouseLeave = () => {
            mouseX = -9999;
            mouseY = -9999;
        };

        window.addEventListener("mousemove", onMouseMove, { passive: true });
        window.addEventListener("mouseout", onMouseLeave, { passive: true });

        if ("IntersectionObserver" in window) {
            const observer = new IntersectionObserver((entries) => {
                isVisible = entries[0].isIntersecting;
                if (isVisible && isTabActive && !animationFrameId) {
                    loop();
                }
            }, { threshold: 0.05 });
            observer.observe(canvas);
        }

        document.addEventListener("visibilitychange", () => {
            isTabActive = !document.hidden;
            if (isTabActive && isVisible && !animationFrameId) {
                loop();
            }
        });

        const loop = () => {
            if (!isVisible || !isTabActive) {
                animationFrameId = null;
                return;
            }

            ctx.clearRect(0, 0, width, height);

            for (let i = 0; i < spores.length; i++) {
                const p = spores[i];

                p.waveOffset += p.waveSpeed;
                p.x += p.vx + Math.sin(p.waveOffset) * 0.35;
                p.y += p.vy;

                // Subtle fluid cursor push
                if (mouseX > -500 && mouseY > -500) {
                    const dx = p.x - mouseX;
                    const dy = p.y - mouseY;
                    const dist = Math.hypot(dx, dy);
                    if (dist < 80 && dist > 0.1) {
                        const force = (1 - dist / 80) * 1.2;
                        p.x += (dx / dist) * force;
                        p.y += (dy / dist) * force;
                    }
                }

                // Alpha fade lifecycle
                if (p.fadeIn) {
                    p.alpha += 0.015;
                    if (p.alpha >= p.maxAlpha) {
                        p.fadeIn = false;
                    }
                } else if (p.y < height * 0.25) {
                    p.alpha -= 0.012;
                }

                if (p.y < -10 || p.alpha <= 0) {
                    resetSpore(p, false);
                }

                // Render spore
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);

                if (p.color === "mint") {
                    ctx.fillStyle = `rgba(52, 211, 153, ${p.alpha})`;
                    ctx.shadowColor = "rgba(52, 211, 153, 0.65)";
                    ctx.shadowBlur = 8;
                } else if (p.color === "emerald") {
                    ctx.fillStyle = `rgba(16, 185, 129, ${p.alpha})`;
                    ctx.shadowColor = "rgba(16, 185, 129, 0.6)";
                    ctx.shadowBlur = 6;
                } else if (p.color === "gold") {
                    ctx.fillStyle = `rgba(252, 211, 77, ${p.alpha * 0.9})`;
                    ctx.shadowColor = "rgba(252, 211, 77, 0.55)";
                    ctx.shadowBlur = 6;
                } else {
                    ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
                    ctx.shadowColor = "rgba(255, 255, 255, 0.8)";
                    ctx.shadowBlur = 7;
                }

                ctx.fill();
            }

            ctx.shadowBlur = 0;
            animationFrameId = requestAnimationFrame(loop);
        };

        loop();
    };


    /* =========================================================================
       2. LIVING SPACE EXHIBITION WINDOW CONTROLLER (Astra Tab & Frame Switcher)
       ========================================================================= */
    const initAstraExhibition = () => {
        const tabButtons = document.querySelectorAll(".astra-tab-pill");
        const slides = document.querySelectorAll(".astra-showcase-slide");
        const counterEl = document.getElementById("astra-window-counter");
        const prevBtn = document.getElementById("astra-prev-slide");
        const nextBtn = document.getElementById("astra-next-slide");

        if (slides.length === 0) return;

        let currentIndex = 0;
        const totalSlides = slides.length;

        const updateExhibition = (index) => {
            if (index < 0) index = totalSlides - 1;
            if (index >= totalSlides) index = 0;
            currentIndex = index;

            // Slide display update
            slides.forEach((slide, idx) => {
                if (idx === currentIndex) {
                    slide.classList.add("active");
                    slide.removeAttribute("hidden");
                } else {
                    slide.classList.remove("active");
                    slide.setAttribute("hidden", "hidden");
                }
            });

            // Tab button update
            tabButtons.forEach((btn) => {
                const btnSpace = btn.dataset.spaceIndex;
                if (parseInt(btnSpace, 10) === currentIndex) {
                    btn.classList.add("active");
                    btn.setAttribute("aria-selected", "true");
                } else {
                    btn.classList.remove("active");
                    btn.setAttribute("aria-selected", "false");
                }
            });

            // Counter update (01 / 04)
            if (counterEl) {
                counterEl.textContent = `0${currentIndex + 1} / 0${totalSlides}`;
            }
        };

        tabButtons.forEach((btn) => {
            btn.addEventListener("click", () => {
                const targetIdx = parseInt(btn.dataset.spaceIndex, 10);
                if (!isNaN(targetIdx)) {
                    updateExhibition(targetIdx);
                }
            });
        });

        if (prevBtn) {
            prevBtn.addEventListener("click", () => updateExhibition(currentIndex - 1));
        }
        if (nextBtn) {
            nextBtn.addEventListener("click", () => updateExhibition(currentIndex + 1));
        }

        updateExhibition(0);
    };

    // Initialize on DOM ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => {
            initAstraTreeAmbience();
            initAstraExhibition();
        });
    } else {
        initAstraTreeAmbience();
        initAstraExhibition();
    }
})();
