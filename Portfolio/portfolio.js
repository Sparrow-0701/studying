document.addEventListener('DOMContentLoaded', () => {
    const tabLinks = document.querySelectorAll('.nav-link');
    const contentTabs = document.querySelectorAll('.content-tab');

    tabLinks.forEach(link => {
        link.addEventListener('click', () => {
            const targetTabId = link.getAttribute('data-tab');

            tabLinks.forEach(navLink => {
                navLink.classList.remove('nav-link-active');
                navLink.classList.add('nav-link-inactive');
            });

            link.classList.add('nav-link-active');
            link.classList.remove('nav-link-inactive');

            contentTabs.forEach(tab => {
                if (!tab.classList.contains('hidden')) {
                    tab.classList.add('hidden');
                }
            });

            const targetTab = document.getElementById(targetTabId);
            if (targetTab) {
                targetTab.classList.remove('hidden');
            }
        });
    });
});
