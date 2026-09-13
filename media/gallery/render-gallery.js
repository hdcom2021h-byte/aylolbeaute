(() => {
    const grid = document.querySelector("#gallery .gallery-grid");
    const empty = document.getElementById("galleryEmpty");
    const labels = {makeup: "الميكب", hair: "الشعر", brides: "العرائس", nails: "الأظافر"};
    (window.aylolGallery || []).forEach(photo => {
        if (!labels[photo.category] || typeof photo.src !== "string" ||
            !photo.src.startsWith("media/gallery/") || photo.src.includes("..")) return;
        const card = document.createElement("button");
        card.type = "button";
        card.className = "gallery-item";
        card.dataset.category = photo.category;
        const isVideo = photo.type === "video";
        const img = document.createElement(isVideo ? "video" : "img");
        img.alt = photo.alt || labels[photo.category] + " — أيلول بيوتي";
        img.loading = "lazy";
        img.decoding = "async";
        const brightness = Number(photo.brightness);
        if (Number.isFinite(brightness) && brightness >= 0.8 && brightness <= 1.3) {
            img.style.filter = `brightness(${brightness})`;
        }
        img.src = photo.src.split("/").map(encodeURIComponent).join("/");
        if (isVideo) {
            img.muted = true;
            img.playsInline = true;
            img.preload = "metadata";
            img.src += "#t=0.1";
            card.classList.add("gallery-video-card");
            const play = document.createElement("span");
            play.className = "gallery-play";
            play.textContent = "▶";
            play.setAttribute("aria-hidden", "true");
            card.append(play);
            card.addEventListener("click", () => {
                const dialog = document.getElementById("galleryVideoDialog");
                const player = dialog.querySelector("video");
                dialog.querySelector("h3").textContent = img.alt;
                player.src = img.src;
                dialog.showModal();
                player.play().catch(() => {});
            });
        }
        card.setAttribute("aria-label", (isVideo ? "تشغيل الفيديو: " : "عرض الصورة: ") + img.alt);
        const caption = document.createElement("span");
        caption.className = "gallery-caption";
        caption.textContent = photo.alt || labels[photo.category];
        card.append(img, caption);
        img.addEventListener("error", () => {
            card.remove();
            updateEmpty();
        });
        grid.append(card);
    });
    function updateEmpty() {
        const active = document.querySelector("#gallery .gallery-filter.active").dataset.galleryFilter;
        const available = [...grid.children].some(card => active === "all" || card.dataset.category === active);
        empty.hidden = available;
        empty.textContent = "قريبًا، لمسات جديدة من أيلول في هذا المعرض.";
    }
    document.querySelectorAll("#gallery .gallery-filter").forEach(button => {
        button.setAttribute("aria-pressed", String(button.classList.contains("active")));
        button.addEventListener("click", () => {
            document.querySelectorAll("#gallery .gallery-filter").forEach(item => {
                item.setAttribute("aria-pressed", String(item === button));
            });
            // Existing filtering updates the active button during this same click.
            queueMicrotask(updateEmpty);
        });
    });
    updateEmpty();
    const dialog = document.createElement("dialog");
    dialog.id = "galleryVideoDialog";
    dialog.setAttribute("aria-labelledby", "galleryVideoTitle");
    dialog.innerHTML = '<div class="gallery-video-top"><h3 id="galleryVideoTitle"></h3><button type="button" aria-label="إغلاق الفيديو" autofocus>×</button></div><video controls playsinline preload="none"></video>';
    document.body.append(dialog);
    let previousOverflow = "";
    dialog.addEventListener("beforetoggle", event => {
        if (event.newState === "open") {
            previousOverflow = document.body.style.overflow;
            document.body.style.overflow = "hidden";
        }
    });
    dialog.querySelector("button").addEventListener("click", () => dialog.close());
    dialog.addEventListener("keydown", event => {
        if (event.key === "Escape") event.stopPropagation();
    });
    dialog.addEventListener("click", event => {
        const r = dialog.getBoundingClientRect();
        if (event.target === dialog && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) dialog.close();
    });
    dialog.addEventListener("close", () => {
        const player = dialog.querySelector("video");
        player.pause();
        player.removeAttribute("src");
        player.load();
        document.body.style.overflow = previousOverflow;
    });
})();
