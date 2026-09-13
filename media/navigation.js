(() => {
    function navigate(hash, smooth = true) {
        let id;
        try { id = decodeURIComponent(hash.slice(1)); } catch (_) { return false; }
        const section = document.getElementById(id);
        if (!section) return false;
        const headerHeight = document.getElementById('aylolHeader')?.getBoundingClientRect().height || 86;
        const availableHeight = Math.max(0, window.innerHeight - headerHeight);
        const content = section.matches('section') ? section.querySelector(':scope > .container') || section : section;
        // offsetTop excludes the reveal animation's temporary transform.
        let top = 0;
        for (let element = content; element; element = element.offsetParent) top += element.offsetTop;
        const gap = Math.max(24, (availableHeight - content.offsetHeight) / 2);
        const destination = id === 'home' ? 0 : Math.max(0, top - headerHeight - gap);
        section.querySelectorAll('.reveal').forEach(element => element.classList.add('visible'));
        if (section.classList.contains('reveal')) section.classList.add('visible');
        window.scrollTo({
            top: destination,
            behavior: smooth && !matchMedia('(prefers-reduced-motion: reduce)').matches ? 'smooth' : 'instant'
        });
        return true;
    }
    document.addEventListener('click', event => {
        const link = event.target.closest('a[href^="#"]');
        if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        const hash = link.getAttribute('href');
        if (hash.length < 2 || !document.getElementById(hash.slice(1))) return;
        event.preventDefault();
        if (location.hash !== hash) history.pushState(null, '', hash);
        // Header mobile-menu click handlers have already restored page scrolling.
        requestAnimationFrame(() => navigate(hash));
    });
    window.addEventListener('popstate', () => navigate(location.hash || '#home', false));
    window.addEventListener('hashchange', () => navigate(location.hash || '#home', false));
    window.addEventListener('aylol:components-ready', () => {
        if (location.hash) document.fonts.ready.then(() => navigate(location.hash, false));
    });
})();
