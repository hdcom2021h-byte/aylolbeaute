(() => {
    const video = document.getElementById('heroVideo');
    const image = document.getElementById('heroFallbackImage');
    if (!video || !image) return;

    function showVideo() {
        video.closest('.hero-visual').classList.add('video-ready');
        video.hidden = false;
        image.hidden = true;
    }
    function showImage() {
        video.closest('.hero-visual').classList.remove('video-ready');
        video.hidden = true;
        image.hidden = false;
    }
    // Mobile browsers may defer loadeddata until the visitor presses play.
    // Keep the poster and native controls visible instead of waiting for a frame.
    video.addEventListener('error', showImage);
    video.querySelector('source')?.addEventListener('error', showImage);
    video.muted = true;
    video.defaultMuted = true;
    video.playsInline = true;
    if (video.error) {
        showImage();
        return;
    }
    showVideo();
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        video.play().catch(() => {
            // Autoplay can be blocked by mobile power/data-saving settings.
            // The visitor can still play using the visible native controls.
        });
    }
})();
