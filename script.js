window.onload = function() {
    const pages = document.querySelectorAll('.page');
    const navBtns = document.querySelectorAll('.nav-btn');

    navBtns.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.getAttribute('data-target');

            pages.forEach(page => {
                if (page.id === target) {
                    page.classList.add('active');
                } else {
                    page.classList.remove('active');
                }
            });
        });
    });

    // ...retain your existing JS for buttons, image upload, etc.
};
