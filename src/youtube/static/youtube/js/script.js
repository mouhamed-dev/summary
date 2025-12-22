// Select2 init if present
if (window.jQuery && $.fn.select2) {
    $('#langue').select2({ width: '100%', minimumResultsForSearch: Infinity });
    $('#taille').select2({ width: '100%', minimumResultsForSearch: Infinity });
}

// Reset handler
resetBtn?.addEventListener('click', () => doReset());

// Static download button (server-rendered page)
staticDownloadBtn?.addEventListener('click', () => {
    const href = staticDownloadBtn.getAttribute('data-href');
    if (href) {
        window.location.href = href;
    }
});

function disableForm() {
    submitBtn?.setAttribute('disabled', 'true');
    form.querySelectorAll('input, select').forEach(el => el.setAttribute('disabled', 'true'));
    if (window.jQuery && $.fn.select2) {
        $('#langue').prop('disabled', true);
        $('#taille').prop('disabled', true);
    }
}
function enableForm() {
    submitBtn?.removeAttribute('disabled');
    form.querySelectorAll('input, select').forEach(el => el.removeAttribute('disabled'));
    if (window.jQuery && $.fn.select2) {
        $('#langue').prop('disabled', false);
        $('#taille').prop('disabled', false);
    }
}
// Reset routine
function doReset() {
    currentTaskId = null;
    form.reset();
    if (window.jQuery && $.fn.select2) {
        $('#langue').val('fr').trigger('change');
        $('#taille').val('short').trigger('change');
    }
    result.innerHTML = '';
    enableForm();
}