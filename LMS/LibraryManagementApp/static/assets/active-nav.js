document.addEventListener('DOMContentLoaded', function() {
    const currentUrl = window.location.href;
    const sidebarLinks = document.querySelectorAll('.sidebar-item');

    sidebarLinks.forEach(link => {
        if (link.querySelector('a').href === currentUrl) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
});
