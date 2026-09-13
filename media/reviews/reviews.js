(() => {
    const form = document.getElementById('anonymousReviewForm');
    const radios = [...form.querySelectorAll('input[name="rating"]')];
    const note = document.getElementById('anonymousReviewNote');
    const label = document.getElementById('ratingLabel');
    const status = document.getElementById('anonymousReviewStatus');
    const cards = document.getElementById('reviewCards');
    const key = 'aylol-anonymous-review-v1';
    function paint() {
        const selected = radios.find(input => input.checked);
        const rating = selected ? Number(selected.value) : 0;
        radios.forEach(input => input.parentElement.classList.toggle('selected', Number(input.value) <= rating));
        label.textContent = rating ? rating + ' من 5 نجوم' : 'لم تختاري تقييمًا بعد';
    }
    function render(review) {
        cards.querySelector('[data-anonymous-review]')?.remove();
        const card = document.createElement('article');
        card.className = 'review-card';
        card.dataset.anonymousReview = 'true';
        const stars = document.createElement('div');
        stars.className = 'review-stars';
        stars.setAttribute('role', 'img');
        stars.setAttribute('aria-label', review.rating + ' من 5 نجوم');
        stars.textContent = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);
        const quote = document.createElement('blockquote');
        quote.textContent = review.note;
        const local = document.createElement('p');
        local.className = 'review-note';
        local.textContent = 'تقييمكِ على هذا المتصفح';
        card.append(stars);
        if (review.note) card.append(quote);
        card.append(local);
        cards.prepend(card);
    }
    radios.forEach(input => input.addEventListener('change', paint));
    try {
        const saved = JSON.parse(localStorage.getItem(key));
        if (saved && Number.isInteger(saved.rating) && saved.rating >= 1 && saved.rating <= 5 &&
            typeof saved.note === 'string' && saved.note.length <= 500) {
            radios[saved.rating - 1].checked = true;
            note.value = saved.note;
            render(saved);
        }
    } catch (_) { /* Saving may be disabled by browser settings. */ }
    paint();
    form.addEventListener('submit', event => {
        event.preventDefault();
        if (!form.reportValidity()) return;
        const review = {rating: Number(radios.find(input => input.checked).value), note: note.value.trim()};
        render(review);
        try {
            localStorage.setItem(key, JSON.stringify(review));
            status.textContent = 'شكرًا لكِ! حُفظ تقييمكِ دون اسم على هذا المتصفح.';
        } catch (_) {
            status.textContent = 'شكرًا لكِ! ظهر تقييمكِ لهذه الزيارة فقط، وتعذّر حفظه في المتصفح.';
        }
    });
})();
