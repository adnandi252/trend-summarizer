// TrendAI Trend Discovery Page Script

let currentSelectedTrend = null;
let currentTrendsData = null;

// Global page load hook called by common.js
window.loadPageData = async function(projectId) {
    if (!projectId) return;

    window.TrendAI.showLoader("Memuat data analisis...");

    try {
        const urlParams = new URLSearchParams(window.location.search);
        const period = urlParams.get('period');
        const urlTrend = urlParams.get('trend');
        
        updateSidebarLinks(period);

        let trendsUrl = `/api/projects/${projectId}/trends`;
        if (period) {
            trendsUrl += `?period=${encodeURIComponent(period)}`;
        }
        
        const trendsRes = await fetch(trendsUrl);
        if (!trendsRes.ok) {
            window.TrendAI.hideLoader();
            showPlaceholderState();
            return;
        }

        const trendsData = await trendsRes.json();
        window.TrendAI.hideLoader();

        // Check if trends data is empty (analysis has not run yet)
        if (Object.keys(trendsData).length === 0) {
            showPlaceholderState();
            return;
        }

        hidePlaceholderState();
        currentTrendsData = trendsData;

        // Determine which trend to show
        const availableTrends = Object.keys(trendsData);

        if (urlTrend && availableTrends.includes(urlTrend)) {
            currentSelectedTrend = urlTrend;
        } else {
            currentSelectedTrend = availableTrends[0];
        }

        // Render the Selected Trend content
        renderTrendDetails(currentSelectedTrend);

    } catch (e) {
        window.TrendAI.hideLoader();
        console.error("Error loading trend details:", e);
        window.TrendAI.showToast("Terjadi kesalahan memuat detail tren", "error");
    }
};

// --- Show Placeholder State if no analysis exists ---
function showPlaceholderState() {
    let placeholder = document.getElementById('discovery-placeholder-overlay');
    if (!placeholder) {
        placeholder = document.createElement('div');
        placeholder.id = 'discovery-placeholder-overlay';
        placeholder.className = 'w-full p-8 border border-dashed border-slate-300 rounded-xl bg-slate-50 flex flex-col items-center justify-center text-center gap-4 my-6';
        
        const title = document.createElement('h3');
        title.className = 'font-headline-md font-bold text-slate-800';
        title.textContent = 'Analisis Proyek Belum Dijalankan';
        placeholder.appendChild(title);
        
        const desc = document.createElement('p');
        desc.className = 'font-body-md text-slate-500 max-w-md';
        desc.textContent = 'Silakan buka menu Pengaturan (Settings) untuk menarik berita dan menjalankan model kecerdasan buatan.';
        placeholder.appendChild(desc);
        
        const btn = document.createElement('button');
        btn.className = 'px-5 py-2.5 bg-secondary text-white font-label-md rounded-lg hover:opacity-90 transition-opacity';
        btn.textContent = 'Buka Pengaturan';
        btn.onclick = () => window.TrendAI.openSettingsModal();
        placeholder.appendChild(btn);
        
        const mainContent = document.querySelector('main > div');
        if (mainContent) {
            // Hide the standard sub-sections
            const heroSection = document.getElementById('trend-hero-section');
            const bentoGrid = document.querySelector('.bento-grid');
            if (heroSection) heroSection.style.display = 'none';
            if (bentoGrid) bentoGrid.style.display = 'none';
            mainContent.appendChild(placeholder);
        }
    } else {
        placeholder.style.display = 'flex';
        const heroSection = document.getElementById('trend-hero-section');
        const bentoGrid = document.querySelector('.bento-grid');
        if (heroSection) heroSection.style.display = 'none';
        if (bentoGrid) bentoGrid.style.display = 'none';
    }
}

function hidePlaceholderState() {
    const placeholder = document.getElementById('discovery-placeholder-overlay');
    if (placeholder) {
        placeholder.style.display = 'none';
    }
    const heroSection = document.getElementById('trend-hero-section');
    const bentoGrid = document.querySelector('.bento-grid');
    if (heroSection) heroSection.style.display = 'block';
    if (bentoGrid) bentoGrid.style.display = 'grid';
}

// --- Render selected trend data views ---
function renderTrendDetails(trendName) {
    const data = currentTrendsData[trendName];
    if (!data) return;

    const allCategories = Object.keys(currentTrendsData);
    const otherCategories = allCategories.filter(c => c !== trendName);

    // Update Header and Page title
    const pageHeading = document.getElementById('discovery-page-heading');
    if (pageHeading) pageHeading.textContent = trendName;

    const heroTitle = document.getElementById('trend-hero-title');
    if (heroTitle) heroTitle.textContent = trendName;

    // Update badge and timestamp
    const badgeLabel = document.getElementById('trend-badge-label');
    if (badgeLabel) badgeLabel.textContent = 'KATEGORI TREN';
    
    const updatedEl = document.getElementById('trend-last-updated');
    if (updatedEl) {
        // Find the latest publish date among articles
        let latestDate = null;
        if (data.articles && data.articles.length > 0) {
            data.articles.forEach(a => {
                if (a.publish_date) {
                    const d = new Date(a.publish_date);
                    if (!isNaN(d.getTime()) && (!latestDate || d > latestDate)) latestDate = d;
                }
            });
        }
        if (latestDate) {
            updatedEl.textContent = `Pembaruan: ${latestDate.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}`;
        } else {
            updatedEl.textContent = 'Beberapa waktu lalu';
        }
    }

    // 1. Indicators Row with real data
    const kpiVal1 = document.getElementById('kpi-aggregate-interest');
    const kpiSources = document.getElementById('kpi-article-sources');
    const kpiVal2 = document.getElementById('kpi-sentiment');
    const kpiSentimentDesc = document.getElementById('kpi-sentiment-desc');

    // Article count
    const signalCount = data.article_count || 0;
    if (kpiVal1) kpiVal1.textContent = signalCount;
    
    // Count unique sources
    const sources = new Set();
    if (data.articles) data.articles.forEach(a => { if (a.source) sources.add(a.source); });
    if (kpiSources) {
        kpiSources.innerHTML = `<span class="material-symbols-outlined text-sm">article</span> ${sources.size} portal sumber`;
    }
    
    // Top keywords
    if (kpiVal2) {
        const keywords = data.top_keywords || [];
        kpiVal2.textContent = keywords.length > 0 ? keywords.slice(0, 3).join(', ') : 'Belum ada';
    }
    if (kpiSentimentDesc) {
        kpiSentimentDesc.textContent = `${signalCount} artikel dianalisis`;
    }
    


    // 2. Executive Brief Narrative from real data
    const narrativeContainer = document.getElementById('trend-narrative-container');
    if (narrativeContainer) {
        narrativeContainer.replaceChildren();
        const text = data.generative_brief || data.extractive_brief || '';
        if (text) {
            // Split by single newline and parse each line
            const lines = text.split('\n');
            lines.forEach(line => {
                const trimmed = line.trim();
                if (!trimmed) return;
                
                const lineEl = document.createElement('p');
                lineEl.className = 'font-body-md text-body-md text-on-surface leading-relaxed mb-2';
                
                // Check if it's the header **Executive Brief**
                if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
                    const headerText = trimmed.replace(/\*\*/g, '');
                    const strong = document.createElement('strong');
                    strong.className = 'block font-headline-sm font-bold text-slate-800 mt-3 mb-1';
                    strong.textContent = headerText;
                    lineEl.appendChild(strong);
                } 
                // Check if it starts with a numbered pattern like "1. Tren Utama:" or "2. Ringkasan:"
                else if (/^\d+\.\s+[^:]+:/.test(trimmed)) {
                    const match = trimmed.match(/^(\d+\.\s+[^:]+:)(.*)$/);
                    if (match) {
                        const labelText = match[1];
                        const contentText = match[2];
                        
                        const strong = document.createElement('strong');
                        strong.className = 'font-bold text-slate-800';
                        strong.textContent = labelText;
                        
                        lineEl.appendChild(strong);
                        lineEl.appendChild(document.createTextNode(contentText));
                    } else {
                        lineEl.textContent = trimmed;
                    }
                } else {
                    lineEl.textContent = trimmed;
                }
                narrativeContainer.appendChild(lineEl);
            });
        } else {
            const p = document.createElement('p');
            p.className = 'font-body-lg text-body-lg text-on-surface mb-stack-md leading-relaxed';
            p.textContent = `Belum ada narasi analisis untuk kategori ${trendName}. Jalankan pipeline analisis untuk menghasilkan ringkasan.`;
            narrativeContainer.appendChild(p);
        }
    }

    // 3. Key Strategic Drivers from real keywords
    const driversList = document.getElementById('key-strategic-drivers-list');
    if (driversList) {
        driversList.replaceChildren();
        const keywords = data.top_keywords || [];
        
        if (keywords.length > 0) {
            // Show all top keywords as chips with context
            keywords.slice(0, 6).forEach(kw => {
                const li = document.createElement('li');
                li.className = 'flex items-center gap-2';
                
                const chip = document.createElement('span');
                chip.className = 'px-2 py-0.5 bg-secondary/10 text-secondary text-[11px] font-label-sm rounded';
                chip.textContent = kw;
                li.appendChild(chip);
                
                driversList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'Belum ada kata kunci terdeteksi.';
            li.className = 'text-text-muted';
            driversList.appendChild(li);
        }
    }

    // 4. Actionable Insights from real market_opportunities
    const insightsList = document.getElementById('actionable-insights-list');
    if (insightsList) {
        insightsList.replaceChildren();
        const opps = data.market_opportunities || [];
        
        if (opps.length > 0) {
            opps.forEach(opp => {
                const li = document.createElement('li');
                li.className = 'flex gap-2 items-start';
                
                const dot = document.createElement('span');
                dot.className = 'text-secondary font-bold mt-1';
                dot.textContent = '•';
                li.appendChild(dot);
                
                const textSpan = document.createElement('span');
                const strong = document.createElement('strong');
                strong.textContent = opp.title + ': ';
                textSpan.appendChild(strong);
                textSpan.appendChild(document.createTextNode(opp.desc));
                
                li.appendChild(textSpan);
                insightsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.className = 'text-text-muted';
            li.textContent = 'Belum ada peluang pasar teridentifikasi.';
            insightsList.appendChild(li);
        }
    }

    // 5. Related Nodes (links to switch trends) from real category list
    const relatedNodesList = document.getElementById('related-nodes-list');
    if (relatedNodesList) {
        relatedNodesList.replaceChildren();
        
        const iconList = ['eco', 'hub', 'inventory_2', 'trending_up', 'analytics'];
        const colorList = ['text-sustainability-green', 'text-marketing-purple', 'text-behavior-orange', 'text-blue-600', 'text-pink-600'];

        otherCategories.forEach((cat, idx) => {
            const catData = currentTrendsData[cat];
            const row = document.createElement('div');
            row.className = 'flex items-center justify-between p-3 bg-surface-container-low rounded group hover:bg-surface-container-high cursor-pointer transition-colors';
            row.onclick = () => {
                currentSelectedTrend = cat;
                renderTrendDetails(cat);
            };

            const leftDiv = document.createElement('div');
            leftDiv.className = 'flex items-center gap-3';
            
            const iconSpan = document.createElement('span');
            iconSpan.className = `material-symbols-outlined text-xl ${colorList[idx % colorList.length]}`;
            iconSpan.textContent = iconList[idx % iconList.length];
            leftDiv.appendChild(iconSpan);

            const titleSpan = document.createElement('span');
            titleSpan.className = 'font-body-md font-bold';
            titleSpan.textContent = cat;
            leftDiv.appendChild(titleSpan);
            
            // Show article count
            const countBadge = document.createElement('span');
            countBadge.className = 'text-[10px] bg-surface-container px-1.5 py-0.5 rounded text-text-muted';
            countBadge.textContent = `${catData.article_count || 0} artikel`;
            leftDiv.appendChild(countBadge);
            
            row.appendChild(leftDiv);

            const chevron = document.createElement('span');
            chevron.className = 'material-symbols-outlined text-text-muted group-hover:translate-x-1 transition-transform';
            chevron.textContent = 'chevron_right';
            row.appendChild(chevron);

            relatedNodesList.appendChild(row);
        });
    }

    // 6. Supporting Sources Table from real articles
    const tableBody = document.getElementById('supporting-sources-tbody');
    if (tableBody) {
        tableBody.replaceChildren();
        
        const articles = data.articles || [];
        
        if (articles.length === 0) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.setAttribute('colspan', '4');
            td.className = 'py-4 text-center text-slate-400';
            td.textContent = 'Tidak ada artikel pendukung.';
            tr.appendChild(td);
            tableBody.appendChild(tr);
        } else {
            articles.forEach(art => {
                const tr = document.createElement('tr');
                tr.className = 'border-b border-border-subtle hover:bg-surface-container-low transition-colors';
                
                // Title
                const tdTitle = document.createElement('td');
                tdTitle.className = 'py-4 font-bold pr-4 max-w-xs truncate';
                tdTitle.textContent = art.title;
                tr.appendChild(tdTitle);
                
                // Source
                const tdSource = document.createElement('td');
                tdSource.className = 'py-4 text-text-muted';
                const sourceBadge = document.createElement('span');
                sourceBadge.className = 'px-1.5 py-0.5 bg-surface-container-low rounded text-[11px]';
                sourceBadge.textContent = art.source || 'Unknown';
                tdSource.appendChild(sourceBadge);
                tr.appendChild(tdSource);
                
                // Date
                const tdDate = document.createElement('td');
                tdDate.className = 'py-4 text-text-muted whitespace-nowrap text-[13px]';
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
                
                // Link
                const tdLink = document.createElement('td');
                tdLink.className = 'py-4 text-right';
                const a = document.createElement('a');
                a.className = 'inline-flex items-center gap-1 text-secondary hover:underline font-bold text-label-sm';
                a.href = art.url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                a.textContent = 'Baca';
                tdLink.appendChild(a);
                tr.appendChild(tdLink);
                
                tableBody.appendChild(tr);
            });
        }
    }

    // 7. Done loading
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
