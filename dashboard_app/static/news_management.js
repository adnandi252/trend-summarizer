// TrendAI News Management Script
// Handles scraping triggers, AI analysis triggers, client-side filtering, and article modal viewing.

(function() {
    let allArticles = [];
    let filteredArticles = [];
    let currentPage = 1;
    const itemsPerPage = 10;
    
    let logPollingInterval = null;
    let statusPollingInterval = null;

    // Global page load hook called by common.js
    window.loadPageData = async function(projectId) {
        if (!projectId) return;

        window.TrendAI.showLoader("Memuat data berita...");
        
        // Stop any active polling from previous project
        stopPolling();

        try {
            const urlParams = new URLSearchParams(window.location.search);
            const period = urlParams.get('period');
            updateSidebarLinks(period);

            // 1. Fetch available analysis periods and update sidebar links
            const periodsRes = await fetch(`/api/projects/${projectId}/periods`);
            if (periodsRes.ok) {
                const periods = await periodsRes.json();
                if (periods.length > 0 && !period) {
                    // Update links with latest period if query param is missing
                    updateSidebarLinks(periods[0]);
                }
            }

            // 2. Fetch all articles for the project
            // Fetching a large limit (e.g. 200) to allow client-side searching and filtering
            const articlesRes = await fetch(`/api/projects/${projectId}/articles?limit=200`);
            if (articlesRes.ok) {
                const data = await articlesRes.json();
                allArticles = data.articles || [];
            } else {
                allArticles = [];
                window.TrendAI.showToast("Gagal mengambil daftar artikel", "error");
            }

            // 3. Update UI states
            populateCategoryFilter();
            applyFiltersAndRender();
            updateKPIMetrics();
            
            // 4. Update project details and check status (scraping/processing)
            await checkProjectPipelineStatus(projectId);

            window.TrendAI.hideLoader();
        } catch (e) {
            window.TrendAI.hideLoader();
            console.error("Error loading news management page data:", e);
            window.TrendAI.showToast("Terjadi kesalahan memuat data halaman", "error");
        }
    };

    // --- Update KPI Metrics based on loaded articles ---
    function updateKPIMetrics() {
        const totalEl = document.getElementById('kpi-total-articles');
        const todayEl = document.getElementById('kpi-today-articles');
        const growthBadge = document.getElementById('kpi-today-growth-badge');
        const yesterdayEl = document.getElementById('kpi-yesterday-comparison');
        const topCatEl = document.getElementById('kpi-top-category');
        const topCatCountEl = document.getElementById('kpi-top-category-count');

        if (!totalEl) return;

        // 1. Total Articles
        totalEl.textContent = allArticles.length;

        // 2. Today and Yesterday Articles count
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        yesterday.setHours(0, 0, 0, 0);

        let countToday = 0;
        let countYesterday = 0;

        allArticles.forEach(art => {
            if (!art.publish_date) return;
            const pubDate = new Date(art.publish_date);
            if (isNaN(pubDate.getTime())) return;

            const pubDay = new Date(pubDate);
            pubDay.setHours(0, 0, 0, 0);

            if (pubDay.getTime() === today.getTime()) {
                countToday++;
            } else if (pubDay.getTime() === yesterday.getTime()) {
                countYesterday++;
            }
        });

        todayEl.textContent = countToday;
        if (yesterdayEl) {
            yesterdayEl.textContent = `${countYesterday} artikel kemarin`;
        }

        // Growth Percentage calculation
        if (growthBadge) {
            growthBadge.replaceChildren();
            growthBadge.className = 'inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold font-label-sm ';

            if (countYesterday === 0) {
                if (countToday === 0) {
                    growthBadge.textContent = '0%';
                    growthBadge.classList.add('bg-slate-100', 'text-slate-500');
                } else {
                    growthBadge.textContent = '+100%';
                    growthBadge.classList.add('bg-green-100', 'text-green-700');
                    const icon = document.createElement('span');
                    icon.className = 'material-symbols-outlined text-[10px] font-bold';
                    icon.textContent = 'arrow_upward';
                    growthBadge.prepend(icon);
                }
            } else {
                const pct = Math.round(((countToday - countYesterday) / countYesterday) * 100);
                if (pct > 0) {
                    growthBadge.textContent = `+${pct}%`;
                    growthBadge.classList.add('bg-green-100', 'text-green-700');
                    const icon = document.createElement('span');
                    icon.className = 'material-symbols-outlined text-[10px] font-bold';
                    icon.textContent = 'arrow_upward';
                    growthBadge.prepend(icon);
                } else if (pct < 0) {
                    growthBadge.textContent = `${pct}%`;
                    growthBadge.classList.add('bg-red-100', 'text-red-700');
                    const icon = document.createElement('span');
                    icon.className = 'material-symbols-outlined text-[10px] font-bold';
                    icon.textContent = 'arrow_downward';
                    growthBadge.prepend(icon);
                } else {
                    growthBadge.textContent = '0%';
                    growthBadge.classList.add('bg-slate-100', 'text-slate-500');
                }
            }
        }

        // 3. Top Trend Category (based on articles from the last 7 days)
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        sevenDaysAgo.setHours(0, 0, 0, 0);

        const counts = {};
        allArticles.forEach(art => {
            if (!art.publish_date) return;
            const pubDate = new Date(art.publish_date);
            if (isNaN(pubDate.getTime())) return;

            if (pubDate >= sevenDaysAgo) {
                const cat = art.trend_category;
                if (cat && cat !== 'Unclustered' && cat !== 'Uncategorized') {
                    counts[cat] = (counts[cat] || 0) + 1;
                }
            }
        });

        let maxCat = '-';
        let maxCount = 0;
        for (const [cat, val] of Object.entries(counts)) {
            if (val > maxCount) {
                maxCount = val;
                maxCat = cat;
            }
        }

        if (topCatEl) {
            topCatEl.textContent = maxCat;
        }
        if (topCatCountEl) {
            if (maxCount > 0) {
                topCatCountEl.textContent = `${maxCount} artikel (7 hari terakhir)`;
            } else {
                topCatCountEl.textContent = 'Belum terklasifikasi (7 hari terakhir)';
            }
        }
    }

    // --- Check and Sync Project Status and start polling if busy ---
    async function checkProjectPipelineStatus(projectId) {
        try {
            const res = await fetch(`/api/projects/${projectId}`);
            if (res.ok) {
                const proj = await res.json();
                updateStatusUI(proj.status);
                
                if (proj.status === 'scraping' || proj.status === 'processing') {
                    startPolling(projectId);
                }
            }
        } catch (e) {
            console.error("Error checking project status:", e);
        }
    }

    // --- Update Project pipeline status badge and button states ---
    function updateStatusUI(status) {
        const badge = document.getElementById('pipeline-status-badge');
        const scrapeBtn = document.getElementById('trigger-scrape-btn');
        const analyzeBtn = document.getElementById('trigger-analyze-btn');
        
        if (badge) {
            badge.textContent = status;
            badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold font-label-sm uppercase';
            
            if (status === 'completed') {
                badge.classList.add('bg-green-100', 'text-green-700');
            } else if (status === 'failed') {
                badge.classList.add('bg-red-100', 'text-red-700');
            } else if (status === 'scraping' || status === 'processing') {
                badge.classList.add('bg-amber-100', 'text-amber-700', 'animate-pulse');
            } else {
                badge.classList.add('bg-slate-100', 'text-slate-700');
            }
        }

        const isBusy = status === 'scraping' || status === 'processing';
        if (scrapeBtn) {
            scrapeBtn.disabled = isBusy;
            if (isBusy) {
                scrapeBtn.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                scrapeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        }
        if (analyzeBtn) {
            analyzeBtn.disabled = isBusy;
            if (isBusy) {
                analyzeBtn.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                analyzeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        }
    }

    // --- Dynamic Category dropdown populator ---
    function populateCategoryFilter() {
        const select = document.getElementById('article-category-filter');
        if (!select) return;

        // Collect unique categories
        const categories = new Set();
        allArticles.forEach(art => {
            if (art.trend_category) {
                categories.add(art.trend_category);
            }
        });

        // Clear except first two options (All, Unclustered)
        select.replaceChildren();
        
        const optAll = document.createElement('option');
        optAll.value = "";
        optAll.textContent = "Semua Kategori";
        select.appendChild(optAll);

        const optUnclustered = document.createElement('option');
        optUnclustered.value = "Unclustered";
        optUnclustered.textContent = "Belum Diklasifikasi";
        select.appendChild(optUnclustered);

        categories.forEach(cat => {
            if (cat !== 'Unclustered' && cat !== 'Uncategorized') {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat;
                select.appendChild(opt);
            }
        });
    }

    // --- Filter logic and Render ---
    function applyFiltersAndRender() {
        const searchQuery = document.getElementById('article-search').value.toLowerCase().trim();
        const selectedCategory = document.getElementById('article-category-filter').value;
        const startDateVal = document.getElementById('article-start-date-filter').value;
        const endDateVal = document.getElementById('article-end-date-filter').value;

        let parsedStart = startDateVal ? new Date(startDateVal) : null;
        let parsedEnd = endDateVal ? new Date(endDateVal) : null;

        // Set start time to beginning of day and end time to end of day for precise comparisons
        if (parsedStart) parsedStart.setHours(0, 0, 0, 0);
        if (parsedEnd) parsedEnd.setHours(23, 59, 59, 999);

        filteredArticles = allArticles.filter(art => {
            // 1. Search Query (Title or Source)
            if (searchQuery) {
                const titleMatch = art.title && art.title.toLowerCase().includes(searchQuery);
                const sourceMatch = art.source && art.source.toLowerCase().includes(searchQuery);
                if (!titleMatch && !sourceMatch) return false;
            }

            // 2. Category
            if (selectedCategory) {
                if (selectedCategory === 'Unclustered') {
                    if (art.trend_category && art.trend_category !== 'Unclustered' && art.trend_category !== 'Uncategorized') {
                        return false;
                    }
                } else {
                    if (art.trend_category !== selectedCategory) return false;
                }
            }

            // 3. Date Range Filter
            if (parsedStart || parsedEnd) {
                if (!art.publish_date) return false;
                const pubDate = new Date(art.publish_date);
                if (isNaN(pubDate.getTime())) return false;

                if (parsedStart && pubDate < parsedStart) return false;
                if (parsedEnd && pubDate > parsedEnd) return false;
            }

            return true;
        });

        currentPage = 1;
        renderArticlesTable();
    }

    // --- Render Table Page ---
    function renderArticlesTable() {
        const tbody = document.getElementById('articles-tbody');
        const counter = document.getElementById('table-results-counter');
        const indicator = document.getElementById('total-articles-indicator');
        const prevBtn = document.getElementById('prev-page-btn');
        const nextBtn = document.getElementById('next-page-btn');

        if (!tbody) return;
        tbody.replaceChildren();

        if (indicator) {
            indicator.textContent = `Total terunduh: ${allArticles.length} artikel`;
        }

        if (filteredArticles.length === 0) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.setAttribute('colspan', '5');
            td.className = 'py-8 text-center text-slate-400 font-body-md';
            td.textContent = 'Tidak ada artikel berita yang cocok dengan filter.';
            tr.appendChild(td);
            tbody.appendChild(tr);

            if (counter) counter.textContent = 'Menampilkan 0 dari 0 artikel';
            if (prevBtn) prevBtn.disabled = true;
            if (nextBtn) nextBtn.disabled = true;
            return;
        }

        // Calculate pagination bounds
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = Math.min(startIndex + itemsPerPage, filteredArticles.length);
        const pageItems = filteredArticles.slice(startIndex, endIndex);

        pageItems.forEach(art => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-border-subtle hover:bg-surface-container-low transition-colors';

            // 1. Title Column
            const tdTitle = document.createElement('td');
            tdTitle.className = 'py-4 px-4 font-bold max-w-sm truncate';
            const titleLink = document.createElement('a');
            titleLink.href = art.url || '#';
            titleLink.target = '_blank';
            titleLink.rel = 'noopener noreferrer';
            titleLink.className = 'text-primary hover:text-secondary transition-colors hover:underline';
            titleLink.textContent = art.title || 'Untitled';
            tdTitle.appendChild(titleLink);
            tr.appendChild(tdTitle);

            // 2. Source Column
            const tdSource = document.createElement('td');
            tdSource.className = 'py-4 px-4 text-text-muted';
            const sourceBadge = document.createElement('span');
            sourceBadge.className = 'px-1.5 py-0.5 bg-surface-container-low rounded text-[11px] font-medium border border-border-subtle';
            sourceBadge.textContent = art.source || 'Unknown';
            tdSource.appendChild(sourceBadge);
            tr.appendChild(tdSource);

            // 3. Date Column
            const tdDate = document.createElement('td');
            tdDate.className = 'py-4 px-4 text-text-muted whitespace-nowrap text-[13px]';
            try {
                const d = new Date(art.publish_date);
                if (!isNaN(d.getTime())) {
                    tdDate.textContent = d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
                } else {
                    tdDate.textContent = art.publish_date || '-';
                }
            } catch (e) {
                tdDate.textContent = art.publish_date || '-';
            }
            tr.appendChild(tdDate);

            // 4. Category Badge Column
            const tdCat = document.createElement('td');
            tdCat.className = 'py-4 px-4';
            const catBadge = document.createElement('span');
            
            const isUnclustered = !art.trend_category || art.trend_category === 'Unclustered' || art.trend_category === 'Uncategorized';
            if (isUnclustered) {
                catBadge.className = 'px-2 py-0.5 text-[10px] font-bold font-label-sm bg-slate-100 text-slate-500 rounded border border-slate-200';
                catBadge.textContent = 'Belum Diklasifikasi';
            } else {
                catBadge.className = 'px-2 py-0.5 text-[10px] font-bold font-label-sm bg-sky-50 text-sky-700 rounded border border-sky-100';
                catBadge.textContent = art.trend_category;
            }
            tdCat.appendChild(catBadge);
            tr.appendChild(tdCat);

            // 5. Actions Column
            const tdAction = document.createElement('td');
            tdAction.className = 'py-4 px-4 text-right';
            const viewBtn = document.createElement('button');
            viewBtn.className = 'px-3 py-1 bg-secondary text-white text-[11px] font-label-md rounded hover:opacity-95 transition-all font-bold';
            viewBtn.textContent = 'Lihat Konten';
            viewBtn.onclick = () => openArticleDetailsModal(art.id);
            tdAction.appendChild(viewBtn);
            tr.appendChild(tdAction);

            tbody.appendChild(tr);
        });

        // Update Pagination Counter
        if (counter) {
            counter.textContent = `Menampilkan ${startIndex + 1}-${endIndex} dari ${filteredArticles.length} artikel`;
        }

        if (prevBtn) prevBtn.disabled = currentPage === 1;
        if (nextBtn) nextBtn.disabled = endIndex >= filteredArticles.length;
    }

    // --- Fetch Article Detail and Open Modal ---
    async function openArticleDetailsModal(articleId) {
        const projectId = window.TrendAI.activeProjectId;
        if (!projectId) return;

        window.TrendAI.showLoader("Memuat isi berita...");
        try {
            const res = await fetch(`/api/projects/${projectId}/articles/${articleId}`);
            window.TrendAI.hideLoader();
            
            if (res.ok) {
                const art = await res.json();
                
                // Set modal titles safely
                document.getElementById('modal-article-title').textContent = art.title || 'Untitled';
                
                // Format dates safely
                let formattedDate = art.publish_date || '';
                try {
                    const d = new Date(art.publish_date);
                    if (!isNaN(d.getTime())) {
                        formattedDate = d.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
                    }
                } catch (e) {}

                document.getElementById('modal-article-meta').textContent = `Sumber: ${art.source || 'Unknown'} | Tanggal Terbit: ${formattedDate}`;
                
                const isUnclustered = !art.trend_category || art.trend_category === 'Unclustered' || art.trend_category === 'Uncategorized';
                const badge = document.getElementById('modal-article-category-badge');
                if (badge) {
                    if (isUnclustered) {
                        badge.textContent = 'Belum Diklasifikasi';
                        badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold font-label-sm bg-slate-100 text-slate-600 border border-slate-200';
                    } else {
                        badge.textContent = art.trend_category;
                        badge.className = 'px-2 py-0.5 rounded text-[10px] font-bold font-label-sm bg-sky-100 text-sky-700 border border-sky-200';
                    }
                }

                // Display main text body safely using textContent
                const bodyText = art.raw_text || art.clean_text || '(Tidak ada isi berita terdeteksi)';
                document.getElementById('modal-article-body').textContent = bodyText;
                
                // Setup URL button
                const urlBtn = document.getElementById('modal-article-url-btn');
                if (urlBtn) {
                    if (art.url) {
                        urlBtn.href = art.url;
                        urlBtn.style.display = 'inline-block';
                    } else {
                        urlBtn.style.display = 'none';
                    }
                }

                // Show modal overlay
                document.getElementById('article-detail-modal').classList.add('active');
            } else {
                window.TrendAI.showToast("Gagal mengambil detail artikel", "error");
            }
        } catch (e) {
            window.TrendAI.hideLoader();
            console.error("Error loading article details:", e);
            window.TrendAI.showToast("Terjadi kesalahan memuat isi artikel", "error");
        }
    }

    function closeArticleDetailsModal() {
        document.getElementById('article-detail-modal').classList.remove('active');
    }

    // --- Polling logs & status ---
    function startPolling(projectId) {
        if (logPollingInterval) clearInterval(logPollingInterval);
        if (statusPollingInterval) clearInterval(statusPollingInterval);

        const fetchLogs = async () => {
            const consoleBox = document.getElementById('pipeline-console');
            if (!consoleBox) return;

            try {
                const res = await fetch(`/api/projects/${projectId}/logs`);
                if (res.ok) {
                    const logs = await res.json();
                    consoleBox.replaceChildren();

                    if (logs.length === 0) {
                        const line = document.createElement('div');
                        line.className = 'console-line';
                        line.textContent = '[info] Belum ada log eksekusi tersedia...';
                        consoleBox.appendChild(line);
                    } else {
                        logs.forEach(msg => {
                            const line = document.createElement('div');
                            line.className = 'console-line';
                            line.textContent = msg;

                            if (msg.includes('✓') || msg.includes('berhasil') || msg.includes('SELESAI')) {
                                line.classList.add('success');
                            } else if (msg.includes('GAGAL') || msg.includes('FAILED') || msg.includes('❌')) {
                                line.classList.add('error');
                            } else if (msg.includes('⚠') || msg.includes('warning')) {
                                line.classList.add('warning');
                            }
                            consoleBox.appendChild(line);
                        });
                    }
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                }
            } catch (e) {
                console.error("Error polling logs:", e);
            }
        };

        const checkStatus = async () => {
            try {
                const res = await fetch(`/api/projects/${projectId}`);
                if (res.ok) {
                    const proj = await res.json();
                    updateStatusUI(proj.status);

                    if (proj.status === 'completed' || proj.status === 'failed') {
                        stopPolling();
                        window.TrendAI.showToast(`Proses pipeline selesai dengan status: ${proj.status.toUpperCase()}`);
                        
                        // Wait briefly then refresh the article database list automatically
                        setTimeout(() => {
                            if (window.TrendAI.activeProjectId) {
                                window.loadPageData(window.TrendAI.activeProjectId);
                            }
                        }, 1000);
                    }
                }
            } catch (e) {
                console.error("Error polling status:", e);
            }
        };

        fetchLogs();
        logPollingInterval = setInterval(fetchLogs, 1500);
        statusPollingInterval = setInterval(checkStatus, 2000);
    }

    function stopPolling() {
        if (logPollingInterval) {
            clearInterval(logPollingInterval);
            logPollingInterval = null;
        }
        if (statusPollingInterval) {
            clearInterval(statusPollingInterval);
            statusPollingInterval = null;
        }
    }

    // --- Button Triggers ---
    async function triggerScraping() {
        const projectId = window.TrendAI.activeProjectId;
        if (!projectId) {
            window.TrendAI.showToast("Pilih atau buat proyek terlebih dahulu!", "warning");
            return;
        }

        const limit = parseInt(document.getElementById('scrape-limit').value);
        const range = document.getElementById('scrape-range').value;

        window.TrendAI.showLoader("Memicu penarikan berita...");
        try {
            const res = await fetch(`/api/projects/${projectId}/scrape`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ limit_per_query: limit, time_range: range })
            });
            window.TrendAI.hideLoader();

            if (res.ok) {
                window.TrendAI.showToast("Penarikan berita di latar belakang dimulai!");
                updateStatusUI('scraping');
                startPolling(projectId);
            } else {
                const err = await res.json();
                window.TrendAI.showToast(err.detail || "Gagal memulai penarikan berita", "error");
            }
        } catch (e) {
            window.TrendAI.hideLoader();
            window.TrendAI.showToast("Gagal menyambung ke server", "error");
        }
    }

    async function triggerAnalysis() {
        const projectId = window.TrendAI.activeProjectId;
        if (!projectId) {
            window.TrendAI.showToast("Pilih atau buat proyek terlebih dahulu!", "warning");
            return;
        }

        const source = document.getElementById('analyze-source').value;
        const model = document.getElementById('analyze-model').value;
        const startDate = document.getElementById('analyze-start-date').value || null;
        const endDate = document.getElementById('analyze-end-date').value || null;

        window.TrendAI.showLoader("Memicu analisis AI...");
        try {
            const res = await fetch(`/api/projects/${projectId}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model_source: source,
                    groq_model: model,
                    start_date: startDate,
                    end_date: endDate
                })
            });
            window.TrendAI.hideLoader();

            if (res.ok) {
                window.TrendAI.showToast("Proses analisis kluster AI dimulai!");
                updateStatusUI('processing');
                startPolling(projectId);
            } else {
                const err = await res.json();
                window.TrendAI.showToast(err.detail || "Gagal memulai analisis", "error");
            }
        } catch (e) {
            window.TrendAI.hideLoader();
            window.TrendAI.showToast("Gagal menyambung ke server", "error");
        }
    }

    // --- Period Helper to update Sidebar Links ---
    function updateSidebarLinks(period) {
        const pParam = period ? `?period=${encodeURIComponent(period)}` : '';
        const briefLink = document.querySelector('a[href*="executive_brief.html"]');
        const discoveryLink = document.querySelector('a[href*="trend_discovery.html"]');
        const dashboardLink = document.querySelector('a[href*="dashboard.html"]');
        const newsLink = document.querySelector('a[href*="news_management.html"]');
        
        if (briefLink) briefLink.href = `/executive_brief.html${pParam}`;
        if (discoveryLink) discoveryLink.href = `/trend_discovery.html${pParam}`;
        if (dashboardLink) dashboardLink.href = `/dashboard.html${pParam}`;
        if (newsLink) newsLink.href = `/news_management.html${pParam}`;
    }

    // --- DOM Event Listeners ---
    document.addEventListener('DOMContentLoaded', () => {
        // Trigger Buttons
        const scrapeBtn = document.getElementById('trigger-scrape-btn');
        if (scrapeBtn) scrapeBtn.addEventListener('click', triggerScraping);

        const analyzeBtn = document.getElementById('trigger-analyze-btn');
        if (analyzeBtn) analyzeBtn.addEventListener('click', triggerAnalysis);

        // Hide model select if using local offline T5
        const sourceSelect = document.getElementById('analyze-source');
        const modelGroup = document.getElementById('analyze-model-group');
        if (sourceSelect && modelGroup) {
            sourceSelect.addEventListener('change', (e) => {
                if (e.target.value === 'groq') {
                    modelGroup.style.display = 'flex';
                } else {
                    modelGroup.style.display = 'none';
                }
            });
        }

        // Search & Filtering events
        const searchInput = document.getElementById('article-search');
        if (searchInput) searchInput.addEventListener('input', applyFiltersAndRender);

        const categoryFilter = document.getElementById('article-category-filter');
        if (categoryFilter) categoryFilter.addEventListener('change', applyFiltersAndRender);

        const startDateFilter = document.getElementById('article-start-date-filter');
        if (startDateFilter) startDateFilter.addEventListener('change', applyFiltersAndRender);

        const endDateFilter = document.getElementById('article-end-date-filter');
        if (endDateFilter) endDateFilter.addEventListener('change', applyFiltersAndRender);

        // Clear Date filter button
        const clearDateBtn = document.getElementById('clear-date-filter-btn');
        if (clearDateBtn) {
            clearDateBtn.addEventListener('click', () => {
                if (startDateFilter) startDateFilter.value = '';
                if (endDateFilter) endDateFilter.value = '';
                applyFiltersAndRender();
            });
        }

        // Refresh articles button
        const refreshBtn = document.getElementById('refresh-articles-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                const projectId = window.TrendAI.activeProjectId;
                if (!projectId) return;
                
                const icon = refreshBtn.querySelector('.material-symbols-outlined');
                if (icon) icon.classList.add('animate-spin');
                
                await window.loadPageData(projectId);
                
                setTimeout(() => {
                    if (icon) icon.classList.remove('animate-spin');
                }, 500);
            });
        }

        // Table Pagination buttons
        const prevBtn = document.getElementById('prev-page-btn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    renderArticlesTable();
                }
            });
        }

        const nextBtn = document.getElementById('next-page-btn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const startIndex = currentPage * itemsPerPage;
                if (startIndex < filteredArticles.length) {
                    currentPage++;
                    renderArticlesTable();
                }
            });
        }

        // Close Modal events
        const closeBtn1 = document.getElementById('close-article-modal-btn');
        if (closeBtn1) closeBtn1.addEventListener('click', closeArticleDetailsModal);

        const closeBtn2 = document.getElementById('close-article-modal-footer-btn');
        if (closeBtn2) closeBtn2.addEventListener('click', closeArticleDetailsModal);

        const modalOverlay = document.getElementById('article-detail-modal');
        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) {
                    closeArticleDetailsModal();
                }
            });
        }
    });

})();
