(() => {
    const dialog = document.getElementById('nationalOfferDialog');
    const trigger = document.getElementById('nationalOfferDetails');
    const details = document.querySelector('#offers .national-offer-details');
    // Keep the card and dialog details identical when the offer is updated.
    dialog.querySelector('.national-dialog-details').append(details.cloneNode(true));
    let previousOverflow = '';
    trigger.addEventListener('click', () => {
        previousOverflow = document.body.style.overflow;
        dialog.showModal();
        document.body.style.overflow = 'hidden';
    });
    dialog.querySelector('.national-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
        if (event.target !== dialog) return;
        const bounds = dialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right ||
            event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
    dialog.addEventListener('keydown', event => {
        if (event.key === 'Escape') event.stopPropagation();
    });
    dialog.addEventListener('close', () => {
        document.body.style.overflow = previousOverflow;
        trigger.focus();
    });
})();
