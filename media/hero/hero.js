(() => {
    const video = document.getElementById('heroVideo');
    const image = document.getElementById('heroFallbackImage');
    function showVideo() {
        video.closest('.hero-visual').classList.add('video-ready');
        video.hidden = false;
        image.hidden = true;
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            video.muted = true;
            video.play().catch(() => { /* Native controls allow manual playback. */ });
        }
    }
    function showImage() {
        video.closest('.hero-visual').classList.remove('video-ready');
        video.hidden = true;
        image.hidden = false;
    }
    video.addEventListener('loadeddata', showVideo, {once: true});
    video.addEventListener('error', showImage);
    video.querySelector('source').addEventListener('error', showImage);
    if (video.readyState >= 2) showVideo();
})();
