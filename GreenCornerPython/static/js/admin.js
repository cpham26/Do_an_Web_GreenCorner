document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("form[data-confirm-message]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.dataset.confirmMessage;

            if (message && !window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll("form[data-order-status-form]").forEach((form) => {
        const statusSelect = form.querySelector("select[name='Status']");
        const submitButton = form.querySelector("button[type='submit']");
        const updateButton = () => {
            if (submitButton) {
                submitButton.disabled = !statusSelect ||
                    statusSelect.value === form.dataset.initialStatus;
            }
        };

        statusSelect?.addEventListener("change", updateButton);
        updateButton();

        form.addEventListener("submit", (event) => {
            const isCancelling = statusSelect?.value === form.dataset.cancelStatus;
            const isFinalizing = statusSelect?.value === form.dataset.finalStatus;

            if (isCancelling &&
                form.dataset.cancelMessage &&
                !window.confirm(form.dataset.cancelMessage)) {
                event.preventDefault();
                return;
            }

            if (isFinalizing &&
                form.dataset.finalMessage &&
                !window.confirm(form.dataset.finalMessage)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll("form[data-role-form]").forEach((form) => {
        const select = form.querySelector("select[name='Role']");
        const button = form.querySelector("button[type='submit']");
        const initialRole = form.dataset.initialRole;
        const updateButton = () => {
            if (button) {
                button.disabled = !select || select.value === initialRole;
            }
        };

        select?.addEventListener("change", updateButton);
        updateButton();
    });

    document.querySelectorAll("form[data-role-form], form[data-admin-submit-once]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const jqueryForm = window.jQuery ? window.jQuery(form) : null;
            const passesClientValidation = form.checkValidity() &&
                (!jqueryForm || typeof jqueryForm.valid !== "function" || jqueryForm.valid());

            if (event.defaultPrevented || !passesClientValidation) {
                return;
            }

            const button = form.querySelector("button[type='submit']");
            if (button && !button.disabled) {
                button.disabled = true;
                button.setAttribute("aria-disabled", "true");
            }
        });
    });

    document.querySelectorAll("[data-admin-product-image]").forEach((image) => {
        const showFallback = () => {
            image.hidden = true;
            const fallback = image.parentElement?.querySelector(
                "[data-admin-product-fallback]"
            );

            if (fallback) {
                fallback.hidden = false;
            }
        };

        image.addEventListener("error", showFallback, { once: true });

        if (image.complete && image.naturalWidth === 0) {
            showFallback();
        }
    });

    /* =========================================================================
       ADMIN LIQUID GLASS: PROGRESS BAR & BOTANICAL AMBIENT PARTICLES
       ========================================================================= */
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Top progress bar
    const progressBar = document.getElementById("presentation-progress-bar");
    if (progressBar) {
        const updateProgressBar = () => {
            const scrollTop = window.scrollY || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            if (scrollHeight > 0) {
                const progress = Math.min(Math.max(scrollTop / scrollHeight, 0), 1);
                progressBar.style.width = `${(progress * 100).toFixed(2)}%`;
            }
        };
        window.addEventListener("scroll", updateProgressBar, { passive: true });
        updateProgressBar();
    }

    // Botanical ambient fluid particles
    const canvas = document.getElementById("botanical-ambient-canvas");
    if (canvas && !reduceMotion && canvas.getContext) {
        const ctx = canvas.getContext("2d");
        let width = (canvas.width = window.innerWidth);
        let height = (canvas.height = window.innerHeight);

        const onResize = () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        };
        window.addEventListener("resize", onResize, { passive: true });

        const particleCount = Math.min(Math.floor(window.innerWidth / 55), 24);
        const particles = [];
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                size: Math.random() * 2.6 + 1.2,
                speedX: (Math.random() - 0.5) * 0.35,
                speedY: -(Math.random() * 0.4 + 0.2),
                alpha: Math.random() * 0.3 + 0.12,
                hue: Math.random() > 0.45 ? 155 : 90,
                oscillation: Math.random() * Math.PI * 2,
                oscSpeed: Math.random() * 0.016 + 0.006
            });
        }

        let isTabVisible = true;
        let animationFrameId = null;

        document.addEventListener("visibilitychange", () => {
            isTabVisible = !document.hidden;
            if (isTabVisible && !animationFrameId) render();
        });

        const render = () => {
            if (!isTabVisible) {
                animationFrameId = null;
                return;
            }
            ctx.clearRect(0, 0, width, height);

            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                p.oscillation += p.oscSpeed;
                p.x += p.speedX + Math.sin(p.oscillation) * 0.3;
                p.y += p.speedY;

                if (p.y < -20) {
                    p.y = height + 20;
                    p.x = Math.random() * width;
                }
                if (p.x < -20) p.x = width + 20;
                if (p.x > width + 20) p.x = -20;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `hsla(${p.hue}, 70%, 55%, ${p.alpha})`;
                ctx.shadowColor = `hsla(${p.hue}, 80%, 60%, 0.5)`;
                ctx.shadowBlur = 6;
                ctx.fill();
            }
            animationFrameId = requestAnimationFrame(render);
        };
        render();
    }
});
