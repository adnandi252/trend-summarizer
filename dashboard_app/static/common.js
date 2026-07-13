// TrendAI Rebuilt Common JavaScript Engine
// Manages shared UI states, alerts, loader, active project selection, and Settings Modal.

window.TrendAI = {
    activeProjectId: null,
    projects: [],
    logPollingInterval: null,
    statusPollingInterval: null,

    // --- Loading Overlay ---
    showLoader: function(message = "Memuat...") {
        let loader = document.getElementById('global-loader-overlay');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'global-loader-overlay';
            loader.className = 'global-loader';
            
            const spinner = document.createElement('div');
            spinner.className = 'loader-spinner';
            
            const text = document.createElement('p');
            text.id = 'global-loader-text';
            text.className = 'font-label-md text-slate-700';
            text.textContent = message;
            
            loader.appendChild(spinner);
            loader.appendChild(text);
            document.body.appendChild(loader);
        } else {
            document.getElementById('global-loader-text').textContent = message;
        }
        // Force reflow
        loader.offsetHeight;
        loader.classList.add('active');
    },

    hideLoader: function() {
        const loader = document.getElementById('global-loader-overlay');
        if (loader) {
            loader.classList.remove('active');
        }
    },

    // --- Toast Notifications ---
    showToast: function(message, type = 'success') {
        let container = document.getElementById('toast-notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-notification-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const textSpan = document.createElement('span');
        textSpan.className = 'font-body-sm font-medium text-slate-800';
        textSpan.textContent = message;
        toast.appendChild(textSpan);
        
        const closeBtn = document.createElement('span');
        closeBtn.className = 'toast-close';
        closeBtn.textContent = '×';
        closeBtn.onclick = function() {
            toast.classList.remove('active');
            setTimeout(() => toast.remove(), 300);
        };
        toast.appendChild(closeBtn);
        
        container.appendChild(toast);
        
        // Force reflow and animate in
        toast.offsetHeight;
        toast.classList.add('active');
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.remove('active');
                setTimeout(() => toast.remove(), 300);
            }
        }, 4000);
    },

    // --- Initialize Projects list ---
    initProjects: async function() {
        try {
            const response = await fetch('/api/projects');
            if (response.ok) {
                this.projects = await response.json();
                this.updateProjectSelectors();
            } else {
                console.error("Failed to fetch projects list");
            }
        } catch (e) {
            console.error("Error fetching projects:", e);
        }
    },

    // --- Update page project selector dropdowns ---
    updateProjectSelectors: function() {
        const selectors = document.querySelectorAll('.project-selector');
        selectors.forEach(select => {
            select.replaceChildren(); // clear old options securely
            
            if (this.projects.length === 0) {
                const opt = document.createElement('option');
                opt.value = "";
                opt.textContent = "Belum Ada Proyek";
                select.appendChild(opt);
                return;
            }

            this.projects.forEach(proj => {
                const opt = document.createElement('option');
                opt.value = proj.id;
                opt.textContent = proj.name;
                select.appendChild(opt);
            });

            // Set value to currently active project
            if (this.activeProjectId) {
                select.value = this.activeProjectId;
            }
        });
    },

    // --- Switch Active Project ---
    switchProject: function(projectId) {
        if (!projectId) return;
        this.activeProjectId = parseInt(projectId);
        localStorage.setItem('trendai_active_project_id', this.activeProjectId);
        
        // Update all selectors on the page
        const selectors = document.querySelectorAll('.project-selector');
        selectors.forEach(s => s.value = this.activeProjectId);
        
        this.showToast(`Proyek aktif dialihkan ke: ${this.getProjectName(this.activeProjectId)}`);

        // Trigger page-specific data loading
        if (typeof window.loadPageData === 'function') {
            window.loadPageData(this.activeProjectId);
        }
    },

    getProjectName: function(id) {
        const p = this.projects.find(proj => proj.id === id);
        return p ? p.name : "Proyek #" + id;
    },

    // --- Modal Initialization ---
    initSettingsModal: function() {
        // Find Settings link in sidebar
        const settingsLinks = document.querySelectorAll('.nav-link-settings, #nav-settings, aside nav a[href*="settings"]');
        settingsLinks.forEach(link => {
            // Prevent default navigation
            link.setAttribute('href', 'javascript:void(0)');
            link.addEventListener('click', () => this.openSettingsModal());
        });

        // Add dynamic settings modal HTML structure if missing
        if (!document.getElementById('settings-modal-overlay')) {
            this.createSettingsModalDOM();
        }
    },

    createSettingsModalDOM: function() {
        const overlay = document.createElement('div');
        overlay.id = 'settings-modal-overlay';
        overlay.className = 'modal-overlay';
        
        const content = document.createElement('div');
        content.className = 'modal-content';
        
        // Header
        const header = document.createElement('div');
        header.className = 'modal-header';
        
        const title = document.createElement('h3');
        title.className = 'font-headline-md text-slate-900 font-bold';
        title.textContent = 'TrendAI Settings & Workspace';
        header.appendChild(title);
        
        const closeBtn = document.createElement('span');
        closeBtn.className = 'text-2xl text-slate-400 hover:text-slate-600 cursor-pointer font-bold';
        closeBtn.textContent = '×';
        closeBtn.onclick = () => this.closeSettingsModal();
        header.appendChild(closeBtn);
        
        content.appendChild(header);
        
        // Body
        const body = document.createElement('div');
        body.className = 'modal-body';
        
        // Subtitle
        const sub1 = document.createElement('p');
        sub1.className = 'font-body-sm text-slate-500 mb-4';
        sub1.textContent = 'Kelola topik riset pasar, scraping berita industri, dan peringkasan otomatis AI.';
        body.appendChild(sub1);
        
        // Table list wrapper
        const tableWrapper = document.createElement('div');
        tableWrapper.className = 'mb-6 max-h-48 overflow-y-auto border border-slate-200 rounded-lg';
        
        const table = document.createElement('table');
        table.className = 'custom-table';
        
        const thead = document.createElement('thead');
        const trHeader = document.createElement('tr');
        ['Nama Proyek', 'Kata Kunci', 'Aksi'].forEach(txt => {
            const th = document.createElement('th');
            th.textContent = txt;
            trHeader.appendChild(th);
        });
        thead.appendChild(trHeader);
        table.appendChild(thead);
        
        const tbody = document.createElement('tbody');
        tbody.id = 'modal-projects-tbody';
        table.appendChild(tbody);
        
        tableWrapper.appendChild(table);
        body.appendChild(tableWrapper);
        
        // Add project Form
        const formTitle = document.createElement('h4');
        formTitle.className = 'font-label-md text-slate-800 font-bold mb-3';
        formTitle.textContent = 'Buat Proyek Baru';
        body.appendChild(formTitle);
        
        const form = document.createElement('form');
        form.onsubmit = (e) => this.handleCreateProject(e);
        
        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-2 gap-4 mb-4';
        
        const col1 = document.createElement('div');
        col1.className = 'flex flex-col gap-1';
        const lblName = document.createElement('label');
        lblName.className = 'font-label-sm text-slate-600 font-bold';
        lblName.textContent = 'Nama Proyek:';
        col1.appendChild(lblName);
        const inputName = document.createElement('input');
        inputName.id = 'new-project-name';
        inputName.required = true;
        inputName.className = 'form-input';
        inputName.placeholder = 'Misal: FMCG Sustainability';
        col1.appendChild(inputName);
        grid.appendChild(col1);
        
        const col2 = document.createElement('div');
        col2.className = 'flex flex-col gap-1';
        const lblKws = document.createElement('label');
        lblKws.className = 'font-label-sm text-slate-600 font-bold';
        lblKws.textContent = 'Kata Kunci (Koma-separated, maks 5):';
        col2.appendChild(lblKws);
        const inputKws = document.createElement('input');
        inputKws.id = 'new-project-keywords';
        inputKws.required = true;
        inputKws.className = 'form-input';
        inputKws.placeholder = 'Misal: ramah lingkungan, ESG ritel';
        col2.appendChild(inputKws);
        grid.appendChild(col2);
        
        form.appendChild(grid);
        
        const col3 = document.createElement('div');
        col3.className = 'flex flex-col gap-1 mb-4';
        const lblDesc = document.createElement('label');
        lblDesc.className = 'font-label-sm text-slate-600 font-bold';
        lblDesc.textContent = 'Deskripsi Proyek (Opsional):';
        col3.appendChild(lblDesc);
        const inputDesc = document.createElement('textarea');
        inputDesc.id = 'new-project-desc';
        inputDesc.rows = 2;
        inputDesc.className = 'form-input';
        inputDesc.placeholder = 'Tulis deskripsi singkat...';
        col3.appendChild(inputDesc);
        form.appendChild(col3);
        const submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'px-4 py-2 bg-secondary text-white font-label-md rounded-lg hover:opacity-90 transition-opacity';
        submitBtn.textContent = 'Simpan Proyek';
        form.appendChild(submitBtn);
        
        body.appendChild(form);
        content.appendChild(body);
        
        // Footer
        const footer = document.createElement('div');
        footer.className = 'modal-footer';
        const closeFooterBtn = document.createElement('button');
        closeFooterBtn.className = 'px-4 py-2 bg-slate-200 text-slate-700 font-label-md rounded-lg hover:bg-slate-300 transition-colors';
        closeFooterBtn.textContent = 'Tutup';
        closeFooterBtn.onclick = () => this.closeSettingsModal();
        footer.appendChild(closeFooterBtn);
        
        content.appendChild(footer);
        overlay.appendChild(content);
        document.body.appendChild(overlay);
    },

    openSettingsModal: function() {
        this.initProjects().then(() => {
            this.renderProjectsTable();
            
            const overlay = document.getElementById('settings-modal-overlay');
            if (overlay) {
                overlay.classList.add('active');
            }
        });
    },

    closeSettingsModal: function() {
        const overlay = document.getElementById('settings-modal-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    },



    // --- Tab 1: Render projects table ---
    renderProjectsTable: function() {
        const tbody = document.getElementById('modal-projects-tbody');
        if (!tbody) return;
        tbody.replaceChildren();
        
        if (this.projects.length === 0) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.setAttribute('colspan', '3');
            td.className = 'text-center text-slate-400 py-4 font-body-sm';
            td.textContent = 'Belum ada proyek ditambahkan.';
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        this.projects.forEach(proj => {
            const tr = document.createElement('tr');
            
            // Name cell
            const tdName = document.createElement('td');
            const strong = document.createElement('strong');
            strong.textContent = proj.name;
            tdName.appendChild(strong);
            
            // Check active indicator
            if (proj.id === this.activeProjectId) {
                const badge = document.createElement('span');
                badge.className = 'ml-2 text-[10px] bg-sky-100 text-sky-700 px-1.5 py-0.5 rounded font-bold';
                badge.textContent = 'Aktif';
                tdName.appendChild(badge);
            }
            tr.appendChild(tdName);
            
            // Keywords cell
            const tdKws = document.createElement('td');
            try {
                const kwsList = JSON.parse(proj.keywords);
                tdKws.textContent = kwsList.join(', ');
            } catch (e) {
                tdKws.textContent = proj.keywords;
            }
            tr.appendChild(tdKws);
            
            // Action cell
            const tdAction = document.createElement('td');
            
            // Switch button if not active
            if (proj.id !== this.activeProjectId) {
                const switchBtn = document.createElement('button');
                switchBtn.className = 'text-xs text-sky-600 hover:text-sky-800 font-bold mr-3';
                switchBtn.textContent = 'Gunakan';
                switchBtn.onclick = () => {
                    this.switchProject(proj.id);
                    this.renderProjectsTable();
                };
                tdAction.appendChild(switchBtn);
            }
            
            const delBtn = document.createElement('button');
            delBtn.className = 'text-xs text-red-600 hover:text-red-800 font-bold';
            delBtn.textContent = 'Hapus';
            delBtn.onclick = () => this.handleDeleteProject(proj.id);
            tdAction.appendChild(delBtn);
            
            tr.appendChild(tdAction);
            tbody.appendChild(tr);
        });
    },

    handleCreateProject: async function(e) {
        e.preventDefault();
        const name = document.getElementById('new-project-name').value.trim();
        const keywordsStr = document.getElementById('new-project-keywords').value.trim();
        const description = document.getElementById('new-project-desc').value.trim();
        
        if (!name || !keywordsStr) return;
        
        const keywords = keywordsStr.split(',').map(k => k.trim()).filter(k => k.length > 0);
        
        this.showLoader("Membuat proyek baru...");
        try {
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description, keywords })
            });
            
            this.hideLoader();
            if (response.ok) {
                const newProj = await response.json();
                this.showToast("Proyek berhasil dibuat!");
                
                // Clear fields
                document.getElementById('new-project-name').value = '';
                document.getElementById('new-project-keywords').value = '';
                document.getElementById('new-project-desc').value = '';
                
                // Set as active if it is the first or by default
                if (!this.activeProjectId) {
                    this.activeProjectId = newProj.id;
                    localStorage.setItem('trendai_active_project_id', this.activeProjectId);
                }
                
                await this.initProjects();
                this.renderProjectsTable();
            } else {
                const err = await response.json();
                this.showToast(err.detail || "Gagal membuat proyek", "error");
            }
        } catch (err) {
            this.hideLoader();
            this.showToast("Gagal menyambung ke server", "error");
        }
    },

    handleDeleteProject: async function(id) {
        if (!confirm("Apakah Anda yakin ingin menghapus proyek ini beserta seluruh datanya?")) return;
        
        this.showLoader("Menghapus proyek...");
        try {
            const response = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
            this.hideLoader();
            
            if (response.ok) {
                this.showToast("Proyek berhasil dihapus");
                if (this.activeProjectId === id) {
                    this.activeProjectId = null;
                    localStorage.removeItem('trendai_active_project_id');
                }
                
                await this.initProjects();
                
                // Set new active project if available
                if (!this.activeProjectId && this.projects.length > 0) {
                    this.activeProjectId = this.projects[0].id;
                    localStorage.setItem('trendai_active_project_id', this.activeProjectId);
                }
                
                this.renderProjectsTable();
                
                // Trigger page load for new active project
                if (typeof window.loadPageData === 'function') {
                    window.loadPageData(this.activeProjectId);
                }
            } else {
                this.showToast("Gagal menghapus proyek", "error");
            }
        } catch (e) {
            this.hideLoader();
            this.showToast("Gagal menyambung ke server", "error");
        }
    },

};

// --- Page Bootstrap and Nav logic ---
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Parse active project from localStorage
    const savedId = localStorage.getItem('trendai_active_project_id');
    if (savedId) {
        window.TrendAI.activeProjectId = parseInt(savedId);
    }
    
    // 2. Fetch projects and update page selectors
    await window.TrendAI.initProjects();
    
    // 3. If no active project, set to the first one available
    if (!window.TrendAI.activeProjectId && window.TrendAI.projects.length > 0) {
        window.TrendAI.switchProject(window.TrendAI.projects[0].id);
    }

    // 4. Initialize Settings Modal
    window.TrendAI.initSettingsModal();

    // 5. Update Sidebar Links to work as standard local routes
    const links = document.querySelectorAll('aside nav a');
    links.forEach(link => {
        const text = link.textContent.trim();
        if (text.includes("Dashboard")) {
            link.setAttribute('href', '/dashboard.html');
            if (window.location.pathname === '/' || window.location.pathname.includes('dashboard.html')) {
                link.className = 'flex items-center gap-3 px-4 py-3 rounded-lg text-secondary dark:text-secondary-fixed font-bold bg-surface-container-low dark:bg-surface-variant transition-colors';
            } else {
                link.className = 'flex items-center gap-3 px-4 py-3 rounded-lg text-text-muted dark:text-on-surface-variant hover:bg-surface-container-low dark:hover:bg-surface-variant transition-colors';
            }
        } else if (text.includes("Trend Discovery")) {
            link.setAttribute('href', '/trend_discovery.html');
            if (window.location.pathname.includes('trend_discovery.html')) {
                link.className = 'flex items-center gap-3 px-4 py-3 rounded-lg text-secondary dark:text-secondary-fixed font-bold bg-surface-container-low dark:bg-surface-variant transition-colors';
            } else {
                link.className = 'flex items-center gap-3 px-4 py-3 rounded-lg text-text-muted dark:text-on-surface-variant hover:bg-surface-container-low dark:hover:bg-surface-variant transition-colors';
            }
        } else if (text.includes("Executive Briefs")) {
            link.setAttribute('href', '/executive_brief.html');
            if (window.location.pathname.includes('executive_brief.html')) {
                link.className = 'flex items-center gap-3 px-4 py-3 rounded-lg text-secondary dark:text-secondary-fixed font-bold bg-surface-container-low dark:bg-surface-variant transition-colors';
            } else {
                link.className = 'flex items-center gap-3 px-4 py-3 rounded-lg text-text-muted dark:text-on-surface-variant hover:bg-surface-container-low dark:hover:bg-surface-variant transition-colors';
            }
        } else if (text.includes("Manajemen Berita")) {
            link.setAttribute('href', '/news_management.html');
            if (window.location.pathname.includes('news_management.html')) {
                link.className = 'flex items-center gap-3 px-4 py-3 rounded-lg text-secondary dark:text-secondary-fixed font-bold bg-surface-container-low dark:bg-surface-variant transition-colors';
            } else {
                link.className = 'flex items-center gap-3 px-4 py-3 rounded-lg text-text-muted dark:text-on-surface-variant hover:bg-surface-container-low dark:hover:bg-surface-variant transition-colors';
            }
        }
    });

    // 6. Bind listener to page-level project selector change
    const selectors = document.querySelectorAll('.project-selector');
    selectors.forEach(select => {
        select.addEventListener('change', (e) => {
            window.TrendAI.switchProject(e.target.value);
        });
    });

    // 7. Update copyright year dynamically
    const copyrightElements = document.querySelectorAll('#copyright-year');
    const currentYear = new Date().getFullYear();
    copyrightElements.forEach(el => {
        el.textContent = currentYear;
    });

    // 8. Initial loading call for page content
    if (window.TrendAI.activeProjectId && typeof window.loadPageData === 'function') {
        window.loadPageData(window.TrendAI.activeProjectId);
    }
});
