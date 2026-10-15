/**
 * Green Corner - Liquid Glass System & Cinematic Video Scrubbing Engine
 * (Apple VisionOS & GPT-6 Astra Scrollytelling Experience)
 */

document.addEventListener("DOMContentLoaded", () => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* =========================================================================
       1. REVEAL OBSERVER (Chuyển động mượt mà khi phần tử vào viewport)
       ========================================================================= */
    const revealElements = document.querySelectorAll("[data-reveal]");
    revealElements.forEach((element, index) => {
        element.classList.add("reveal-ready");
        element.style.setProperty("--reveal-delay", `${Math.min(index % 4, 3) * 60}ms`);
    });

    if (reduceMotion || !("IntersectionObserver" in window)) {
        revealElements.forEach((element) => element.classList.add("is-visible"));
    } else {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        }, {
            threshold: 0.08,
            rootMargin: "0px 0px -30px"
        });

        revealElements.forEach((element) => revealObserver.observe(element));
    }


    /* =========================================================================
       2. PRESENTATION PROGRESS SCRUB ENGINE
       ========================================================================= */
    const progressBar = document.getElementById("presentation-progress-bar");
    const stageScenes = document.querySelectorAll(".stage-scene");
    const hudButtons = document.querySelectorAll(".stage-hud-btn");
    const hudCounter = document.getElementById("stage-active-counter");

    // Cập nhật thanh tiến trình cuộn trang mượt mà
    const updatePresentationScrub = () => {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        if (scrollHeight <= 0) return;

        const progress = Math.min(Math.max(scrollTop / scrollHeight, 0), 1);
        const progressPercent = (progress * 100).toFixed(2);

        // Cập nhật thanh tiến trình scrubber
        if (progressBar) {
            progressBar.style.width = `${progressPercent}%`;
            progressBar.setAttribute("aria-valuenow", Math.round(progress * 100));
        }
    };

    window.addEventListener("scroll", updatePresentationScrub, { passive: true });
    updatePresentationScrub();


    /* =========================================================================
       3. CAMERA DEPTH-OF-FIELD (FOCAL RACK & SHARPNESS PULL)
       ========================================================================= */
    // Tạo hiệu ứng như ống kính máy quay lấy nét: Khi cuộn tới tâm mắt thì nét căng, khi xa thì bokeh nhẹ
    const focalFrames = document.querySelectorAll(".cinematic-focal-frame");

    if (focalFrames.length > 0 && "IntersectionObserver" in window && !reduceMotion) {
        focalFrames.forEach((frame) => frame.classList.add("focal-out"));

        const focalObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting && entry.intersectionRatio >= 0.25) {
                    entry.target.classList.add("focal-in");
                    entry.target.classList.remove("focal-out");
                } else {
                    entry.target.classList.add("focal-out");
                    entry.target.classList.remove("focal-in");
                }
            });
        }, {
            threshold: [0.1, 0.25, 0.5, 0.75],
            rootMargin: "-5% 0px -10% 0px"
        });

        focalFrames.forEach((frame) => focalObserver.observe(frame));
    } else {
        focalFrames.forEach((frame) => frame.classList.add("focal-in"));
    }


    /* =========================================================================
       4. STAGE TIMELINE OBSERVER & HUD NAVIGATION
       ========================================================================= */
    if (stageScenes.length > 0 && "IntersectionObserver" in window) {
        const stageObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                const stageId = entry.target.id;
                const stageIndex = entry.target.dataset.stageIndex || "1";

                if (entry.isIntersecting) {
                    // Cập nhật nút tương ứng trên HUD
                    hudButtons.forEach((btn) => {
                        const target = btn.dataset.stageTarget;
                        if (target === stageId) {
                            btn.classList.add("active");
                        } else {
                            btn.classList.remove("active");
                        }
                    });

                    // Cập nhật bộ đếm HUD (01/05 -> 05/05)
                    if (hudCounter) {
                        hudCounter.textContent = `0${stageIndex}/05`;
                    }
                }
            });
        }, {
            threshold: [0.2, 0.5],
            rootMargin: "-10% 0px -20% 0px"
        });

        stageScenes.forEach((scene) => stageObserver.observe(scene));
    }

    // Xử lý click nhảy nhanh phân cảnh trên HUD
    hudButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.dataset.stageTarget;
            const targetElement = targetId ? document.getElementById(targetId) : null;
            if (targetElement) {
                const headerOffset = 70;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                window.scrollTo({
                    top: offsetPosition,
                    behavior: reduceMotion ? "auto" : "smooth"
                });
            }
        });
    });

    // Nút scroll next trên Hero ("Bắt đầu thước phim")
    document.querySelectorAll("[data-stage-scroll-next]").forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.dataset.stageScrollNext;
            const targetElement = targetId ? document.getElementById(targetId) : null;
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: reduceMotion ? "auto" : "smooth",
                    block: "start"
                });
            }
        });
    });


    /* =========================================================================
       5. BOTANICAL AMBIENT FLUID PARTICLES (Hạt mầm trôi êm đềm nền)
       ========================================================================= */
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

        // Khởi tạo 26 đốm sáng sinh học êm đềm
        const particleCount = Math.min(Math.floor(window.innerWidth / 55), 28);
        const particles = [];

        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                size: Math.random() * 2.8 + 1.2,
                speedX: (Math.random() - 0.5) * 0.35,
                speedY: -(Math.random() * 0.45 + 0.2),
                alpha: Math.random() * 0.35 + 0.12,
                hue: Math.random() > 0.45 ? 155 : 90,
                oscillation: Math.random() * Math.PI * 2,
                oscSpeed: Math.random() * 0.018 + 0.006
            });
        }

        let animationFrameId = null;
        let isTabVisible = true;

        document.addEventListener("visibilitychange", () => {
            isTabVisible = !document.hidden;
            if (isTabVisible && !animationFrameId) {
                render();
            }
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

                // Tái sinh hạt khi trôi ra khỏi màn hình
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


    /* =========================================================================
       6. TIỆN ÍCH FORM & BẢO VỆ GIAO DỊCH
       ========================================================================= */

    // Ẩn/hiện mật khẩu
    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.setAttribute("aria-pressed", "false");
        button.addEventListener("click", () => {
            const targetId = button.dataset.passwordTarget;
            const input = targetId ? document.getElementById(targetId) : null;

            if (!input) return;

            const shouldShow = input.type === "password";
            input.type = shouldShow ? "text" : "password";
            button.textContent = shouldShow ? "Ẩn" : "Hiện";
            button.setAttribute("aria-label", shouldShow ? "Ẩn mật khẩu" : "Hiện mật khẩu");
            button.setAttribute("aria-pressed", shouldShow ? "true" : "false");
        });
    });

    // Fallback ảnh sản phẩm lỗi
    document.querySelectorAll("[data-product-image]").forEach((image) => {
        const showFallback = () => {
            image.hidden = true;
            const fallback = image.parentElement?.querySelector("[data-product-image-fallback]");
            if (fallback) {
                fallback.hidden = false;
            }
        };

        image.addEventListener("error", showFallback, { once: true });

        if (image.complete && image.naturalWidth === 0) {
            showFallback();
        }
    });

    // Chống bấm đúp Submit form
    document.querySelectorAll("[data-cart-form], [data-submit-once]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const confirmationMessage = form.dataset.confirmMessage;
            if (confirmationMessage && !window.confirm(confirmationMessage)) {
                event.preventDefault();
                return;
            }

            const jqueryForm = window.jQuery ? window.jQuery(form) : null;
            const passesClientValidation = form.checkValidity() &&
                (!jqueryForm || typeof jqueryForm.valid !== "function" || jqueryForm.valid());

            if (event.defaultPrevented || !passesClientValidation) {
                return;
            }

            const button = form.querySelector("button[type='submit']");
            if (!button || button.disabled) {
                return;
            }

            button.disabled = true;
            button.setAttribute("aria-disabled", "true");

            if (button.dataset.loadingText) {
                button.textContent = button.dataset.loadingText;
            }
        });
    });

    // Xác nhận form tổng quát
    document.querySelectorAll("form[data-confirm-message]:not([data-cart-form]):not([data-submit-once])").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.dataset.confirmMessage;
            if (message && !window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Thông báo Toast / Notice tự động đóng
    document.querySelectorAll("[data-site-notice]").forEach((notice) => {
        const closeNotice = () => {
            notice.classList.add("is-hiding");
            window.setTimeout(() => notice.remove(), reduceMotion ? 0 : 190);
        };

        notice.querySelector("[data-notice-close]")?.addEventListener("click", closeNotice);

        if (notice.hasAttribute("data-notice-auto-close")) {
            let closeTimer;
            const scheduleClose = () => {
                window.clearTimeout(closeTimer);
                closeTimer = window.setTimeout(closeNotice, 5000);
            };
            const pauseClose = () => window.clearTimeout(closeTimer);

            notice.addEventListener("mouseenter", pauseClose);
            notice.addEventListener("mouseleave", scheduleClose);
            notice.addEventListener("focusin", pauseClose);
            notice.addEventListener("focusout", scheduleClose);
            scheduleClose();
        }
    });
});
