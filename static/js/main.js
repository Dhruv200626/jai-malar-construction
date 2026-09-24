/**
 * JAI MALHAR - Construction Site Management System
 * Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar Toggle (Mobile) ──────────────────────────────
  const sidebar = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  const menuToggle = document.getElementById('menuToggle');

  function openSidebar() {
    sidebar?.classList.add('open');
    sidebarOverlay?.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar?.classList.remove('open');
    sidebarOverlay?.classList.remove('show');
    document.body.style.overflow = '';
  }

  menuToggle?.addEventListener('click', function () {
    if (sidebar?.classList.contains('open')) {
      closeSidebar();
    } else {
      openSidebar();
    }
  });

  sidebarOverlay?.addEventListener('click', closeSidebar);

  // Close sidebar on escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeSidebar();
      closeQuickActionsMenu();
      closeMoreMenu();
    }
  });

  // ── Mobile Quick Actions FAB ─────────────────────────────
  const fabBtn = document.getElementById('fabBtn');
  const quickActionsOverlay = document.getElementById('quickActionsOverlay');
  const quickActionsMenu = document.getElementById('quickActionsMenu');
  const closeQuickActions = document.getElementById('closeQuickActions');

  function openQuickActions() {
    quickActionsOverlay?.classList.add('show');
    quickActionsMenu?.classList.add('show');
    fabBtn?.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeQuickActionsMenu() {
    quickActionsOverlay?.classList.remove('show');
    quickActionsMenu?.classList.remove('show');
    fabBtn?.classList.remove('active');
    document.body.style.overflow = '';
  }

  fabBtn?.addEventListener('click', function () {
    if (quickActionsMenu?.classList.contains('show')) {
      closeQuickActionsMenu();
    } else {
      closeMoreMenu();
      openQuickActions();
    }
  });
  quickActionsOverlay?.addEventListener('click', closeQuickActionsMenu);
  closeQuickActions?.addEventListener('click', closeQuickActionsMenu);

  // ── More Menu Drawer ──────────────────────────────────────
  const moreNavBtn = document.getElementById('moreNavBtn');
  const moreMenuOverlay = document.getElementById('moreMenuOverlay');
  const moreMenuDrawer = document.getElementById('moreMenuDrawer');
  const closeMoreMenuBtn = document.getElementById('closeMoreMenu');

  function openMoreMenu() {
    moreMenuOverlay?.classList.add('show');
    moreMenuDrawer?.classList.add('show');
    moreNavBtn?.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeMoreMenu() {
    moreMenuOverlay?.classList.remove('show');
    moreMenuDrawer?.classList.remove('show');
    moreNavBtn?.classList.remove('active');
    document.body.style.overflow = '';
  }

  moreNavBtn?.addEventListener('click', function (e) {
    e.preventDefault();
    if (moreMenuDrawer?.classList.contains('show')) {
      closeMoreMenu();
    } else {
      closeQuickActionsMenu();
      openMoreMenu();
    }
  });

  moreMenuOverlay?.addEventListener('click', closeMoreMenu);
  closeMoreMenuBtn?.addEventListener('click', closeMoreMenu);

  // Swipe down to close more menu
  let touchStartY = 0;
  moreMenuDrawer?.addEventListener('touchstart', function (e) {
    touchStartY = e.touches[0].clientY;
  });
  moreMenuDrawer?.addEventListener('touchend', function (e) {
    const diff = e.changedTouches[0].clientY - touchStartY;
    if (diff > 80) closeMoreMenu();
  });

  // ── Toast Auto-dismiss ───────────────────────────────────
  function initToasts() {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const toasts = toastContainer.querySelectorAll('.toast-item');
    toasts.forEach(function (toast) {
      // Auto dismiss after 4 seconds
      const timeout = setTimeout(function () {
        dismissToast(toast);
      }, 4000);

      // Manual close button
      const closeBtn = toast.querySelector('.toast-close');
      closeBtn?.addEventListener('click', function () {
        clearTimeout(timeout);
        dismissToast(toast);
      });
    });
  }

  function dismissToast(toast) {
    toast.style.transition = 'all 0.3s ease';
    toast.style.transform = 'translateX(120%)';
    toast.style.opacity = '0';
    setTimeout(function () {
      toast.remove();
    }, 300);
  }

  initToasts();

  // ── Password Toggle ──────────────────────────────────────
  document.querySelectorAll('.password-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const target = document.getElementById(btn.dataset.target || 'password-field');
      if (!target) return;

      if (target.type === 'password') {
        target.type = 'text';
        btn.innerHTML = '<i class="fas fa-eye-slash"></i>';
      } else {
        target.type = 'password';
        btn.innerHTML = '<i class="fas fa-eye"></i>';
      }
    });
  });

  // ── Active Nav Item ──────────────────────────────────────
  function setActiveNav() {
    const path = window.location.pathname;
    const navItems = document.querySelectorAll('.sidebar-item');

    navItems.forEach(function (item) {
      item.classList.remove('active');
      const href = item.getAttribute('href');
      if (href && path.startsWith(href) && href !== '/') {
        item.classList.add('active');
      } else if (href === '/dashboard/' && (path === '/dashboard/' || path === '/')) {
        item.classList.add('active');
      }
    });

    // Mobile nav
    const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
    mobileNavItems.forEach(function (item) {
      item.classList.remove('active');
      const href = item.getAttribute('href');
      if (href && path.startsWith(href) && href !== '/') {
        item.classList.add('active');
      }
    });
  }

  setActiveNav();

  // ── Confirm Delete Dialog ─────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      const msg = el.dataset.confirm || 'Are you sure you want to delete this item?';
      if (!confirm(msg)) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });

  // ── Global Search ─────────────────────────────────────────
  const globalSearch = document.getElementById('globalSearch');
  const searchResults = document.getElementById('searchResults');

  if (globalSearch) {
    let searchTimeout;
    globalSearch.addEventListener('input', function () {
      clearTimeout(searchTimeout);
      const query = this.value.trim();
      if (query.length < 2) {
        if (searchResults) searchResults.style.display = 'none';
        return;
      }
      searchTimeout = setTimeout(function () {
        performSearch(query);
      }, 300);
    });

    globalSearch.addEventListener('blur', function () {
      setTimeout(function () {
        if (searchResults) searchResults.style.display = 'none';
      }, 200);
    });
  }

  function performSearch(query) {
    fetch(`/api/search/?q=${encodeURIComponent(query)}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (searchResults && data.results && data.results.length > 0) {
          renderSearchResults(data.results);
        }
      })
      .catch(function () {
        // Silently fail search
      });
  }

  function renderSearchResults(results) {
    if (!searchResults) return;
    let html = '<div class="search-dropdown">';
    results.slice(0, 8).forEach(function (item) {
      html += `<a href="${item.url}" class="search-result-item">
        <span class="search-result-icon"><i class="${item.icon}"></i></span>
        <span class="search-result-text">
          <span class="search-result-title">${item.title}</span>
          <span class="search-result-type">${item.type}</span>
        </span>
      </a>`;
    });
    html += '</div>';
    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
  }

  // ── Notification Dropdown ─────────────────────────────────
  const notifBtn = document.getElementById('notifBtn');
  const notifDropdown = document.getElementById('notifDropdown');

  notifBtn?.addEventListener('click', function (e) {
    e.stopPropagation();
    notifDropdown?.classList.toggle('show');
  });

  document.addEventListener('click', function () {
    notifDropdown?.classList.remove('show');
  });

  // ── User Dropdown ─────────────────────────────────────────
  const userBtn = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdown');

  userBtn?.addEventListener('click', function (e) {
    e.stopPropagation();
    userDropdown?.classList.toggle('show');
  });

  document.addEventListener('click', function () {
    userDropdown?.classList.remove('show');
  });

  // ── Form Validation ───────────────────────────────────────
  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      let isValid = true;
      form.querySelectorAll('[required]').forEach(function (field) {
        if (!field.value.trim()) {
          field.classList.add('is-invalid');
          isValid = false;
        } else {
          field.classList.remove('is-invalid');
        }
      });
      if (!isValid) {
        e.preventDefault();
        showToast('Please fill in all required fields.', 'warning');
      }
    });
  });

  // ── CSRF Token helper ─────────────────────────────────────
  window.getCsrfToken = function () {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  };

  // ── Show Toast programmatically ───────────────────────────
  window.showToast = function (message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = {
      success: 'fa-check-circle',
      error: 'fa-times-circle',
      danger: 'fa-times-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle',
    };

    const toast = document.createElement('div');
    toast.className = `toast-item ${type}`;
    toast.innerHTML = `
      <i class="fas ${icons[type] || icons.info} toast-icon ${type}"></i>
      <span class="toast-body">${message}</span>
      <button class="toast-close"><i class="fas fa-times"></i></button>
    `;

    container.appendChild(toast);
    initToasts();
  };

  // ── Progress Bar Animation ────────────────────────────────
  function animateProgressBars() {
    document.querySelectorAll('.progress-bar-custom[data-width]').forEach(function (bar) {
      const width = bar.dataset.width;
      setTimeout(function () {
        bar.style.width = width + '%';
      }, 200);
    });
  }

  animateProgressBars();

});
