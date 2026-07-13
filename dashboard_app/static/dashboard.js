// TrendAI Dashboard Page Script

// Global page load hook called by common.js
window.loadPageData = async function(projectId, activePeriod = null) {
    if (!projectId) return;

    window.TrendAI.showLoader("Memuat data dashboard...");

    try {
        // Fetch project metadata
        const projectRes = await fetch(`/api/projects/${projectId}`);
        if (!projectRes.ok) {
            window.TrendAI.hideLoader();
            window.TrendAI.showToast("Gagal mengambil detail proyek", "error");
            return;
        }
        const projectData = await projectRes.json();
        
        // Fetch available periods for this project
        const periodsRes = await fetch(`/api/projects/${projectId}/periods`);
        let periods = [];
        if (periodsRes.ok) {
            periods = await periodsRes.json();
        }
        
        // Populate period selector dropdown
        const periodSelector = document.getElementById('dashboard-period-selector');
        if (periodSelector) {
            periodSelector.replaceChildren();
            if (periods.length === 0) {
                const opt = document.createElement('option');
                opt.value = '';
                opt.textContent = 'Semua Periode';
                periodSelector.appendChild(opt);
            } else {
                periods.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p;
                    opt.textContent = p === 'all' ? 'Semua Periode' : p;
                    if (activePeriod === p) {
                        opt.selected = true;
                    }
                    periodSelector.appendChild(opt);
                });
            }
        }
        
        // If activePeriod is not set and we have periods, default to the first one (latest)
        if (!activePeriod && periods.length > 0) {
            activePeriod = periods[0];
            if (periodSelector) periodSelector.value = activePeriod;
        }
        
        // Save selected period globally
        window.activeAnalysisPeriod = activePeriod || '';
        updateSidebarLinks(activePeriod);

        // Fetch project trend summaries for the selected period
        let trendsUrl = `/api/projects/${projectId}/trends`;
        if (activePeriod) {
            trendsUrl += `?period=${encodeURIComponent(activePeriod)}`;
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
        if (!trendsData || Object.keys(trendsData).length === 0) {
            showPlaceholderState();
            return;
        }

        // Hide placeholder and show dashboard content
        hidePlaceholderState();

        // Cache raw trends data globally
        window.rawTrendsData = trendsData;
        
        // Calculate total articles across all trends
        let totalArticles = 0;
        let uniqueSources = new Set();
        Object.values(trendsData).forEach(cat => {
            totalArticles += cat.article_count || 0;
            if (cat.articles) {
                cat.articles.forEach(art => {
                    if (art.source) uniqueSources.add(art.source);
                });
            }
        });

        // Update header project count description
        const signalCountText = document.getElementById('signals-count-description');
        if (signalCountText) {
            signalCountText.textContent = `Menganalisis ${totalArticles} artikel dari berbagai sumber industri.`;
        }


        // Render metrics
        renderMetrics(trendsData, totalArticles, uniqueSources);

        // Render Executive Summary Card
        renderExecutiveSummary(trendsData);

        // Render Trending Topics Bar Chart
        renderTrendingTopicsChart(trendsData);

        // Render Latest Insights Column
        renderLatestInsightsList(trendsData);

    } catch (e) {
        window.TrendAI.hideLoader();
        console.error("Error loading dashboard data:", e);
        window.TrendAI.showToast("Terjadi kesalahan memuat dashboard", "error");
    }
};

// --- Show Placeholder State if no analysis exists ---
function showPlaceholderState() {
    let placeholder = document.getElementById('dashboard-placeholder-overlay');
    if (!placeholder) {
        placeholder = document.createElement('div');
        placeholder.id = 'dashboard-placeholder-overlay';
        placeholder.className = 'col-span-12 p-8 border border-dashed border-slate-300 rounded-xl bg-slate-50 flex flex-col items-center justify-center text-center gap-4 my-6';
        
        const title = document.createElement('h3');
        title.className = 'font-headline-md font-bold text-slate-800';
        title.textContent = 'Analisis Proyek Belum Dijalankan';
        placeholder.appendChild(title);
        
        const desc = document.createElement('p');
        desc.className = 'font-body-md text-slate-500 max-w-md';
        desc.textContent = 'Proyek ini baru dibuat atau belum dianalisis. Silakan buka menu Pengaturan (Settings) untuk menarik berita dan menjalankan model kecerdasan buatan.';
        placeholder.appendChild(desc);
        
        const btn = document.createElement('button');
        btn.className = 'px-5 py-2.5 bg-secondary text-white font-label-md rounded-lg hover:opacity-90 transition-opacity';
        btn.textContent = 'Buka Pengaturan';
        btn.onclick = () => window.TrendAI.openSettingsModal();
        placeholder.appendChild(btn);
        
        // Find main dashboard grid and prepend
        const mainContent = document.querySelector('main');
        if (mainContent) {
            // Find insertion point (metrics grid or container)
            const metricsRow = document.getElementById('metrics-indicators-row');
            const mainGrid = document.getElementById('main-bento-grid');
            if (metricsRow) metricsRow.style.display = 'none';
            if (mainGrid) mainGrid.style.display = 'none';
            mainContent.insertBefore(placeholder, mainContent.firstChild.nextSibling.nextSibling);
        }
    } else {
        placeholder.style.display = 'flex';
        const metricsRow = document.getElementById('metrics-indicators-row');
        const mainGrid = document.getElementById('main-bento-grid');
        if (metricsRow) metricsRow.style.display = 'none';
        if (mainGrid) mainGrid.style.display = 'none';
    }
}

function hidePlaceholderState() {
    const placeholder = document.getElementById('dashboard-placeholder-overlay');
    if (placeholder) {
        placeholder.style.display = 'none';
    }
    const metricsRow = document.getElementById('metrics-indicators-row');
    const mainGrid = document.getElementById('main-bento-grid');
    if (metricsRow) metricsRow.style.display = 'grid';
    if (mainGrid) mainGrid.style.display = 'grid';
}

// --- Render Metrics indicators row ---
function renderMetrics(trends, totalArticles, uniqueSources) {
    const elProcessed = document.getElementById('metric-val-processed');
    const elSources = document.getElementById('metric-val-sources');
    const elTrends = document.getElementById('metric-val-trends');

    if (elProcessed) elProcessed.textContent = totalArticles;
    if (elSources) elSources.textContent = uniqueSources ? uniqueSources.size : 0;
    if (elTrends) elTrends.textContent = Object.keys(trends).length;
}

// --- Render Executive Summary and Opportunity/Risk Highlights ---
function renderExecutiveSummary(trends) {
    const briefTextContainer = document.getElementById('executive-summary-text-container');
    const oppContainer = document.getElementById('primary-opportunity-text');
    const riskContainer = document.getElementById('critical-risk-text');
    const timestampEl = document.getElementById('executive-summary-timestamp');

    if (!briefTextContainer) return;
    briefTextContainer.replaceChildren();

    // Set real timestamp
    if (timestampEl) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
        timestampEl.textContent = `Diperbarui ${timeStr}`;
    }

    // Collect all generative briefs
    const categories = Object.keys(trends);
    if (categories.length === 0) return;

    // Style categories with dynamic colors
    const colors = ['text-secondary', 'text-marketing-purple', 'text-behavior-orange'];
    const bgColors = ['bg-secondary/5', 'bg-marketing-purple/5', 'bg-behavior-orange/5'];

    // Show paragraphs
    categories.forEach((cat, index) => {
        const catData = trends[cat];
        const p = document.createElement('p');
        p.className = index === 0 ? 'font-body-lg text-body-lg text-primary leading-relaxed mb-stack-md' : 'font-body-md text-body-md text-on-surface-variant leading-relaxed mb-stack-md';
        
        // Highlight category name
        const boldCat = document.createElement('span');
        boldCat.className = `font-bold ${colors[index % colors.length]}`;
        boldCat.textContent = cat + ": ";
        p.appendChild(boldCat);

        // Add text snippet - get first 2 sentences of generative brief
        let briefParagraph = catData.generative_brief || catData.extractive_brief || "Belum ada ringkasan.";
        briefParagraph = briefParagraph.replace(/^\*\*Executive Brief\*\*\s*/i, '');
        const sentences = briefParagraph.match(/[^.!?]+[.!?]+/g) || [briefParagraph];
        const truncated = sentences.slice(0, 2).join(' ');
        p.appendChild(document.createTextNode(truncated));
        briefTextContainer.appendChild(p);
    });

    // Populate Opportunity and Risk from real data
    let opportunityFound = null;
    let behaviorFound = null;
    let oppCategory = '';
    let behaviorCategory = '';

    for (let cat of categories) {
        const opps = trends[cat].market_opportunities;
        if (opps && opps.length > 0 && !opportunityFound) {
            opportunityFound = opps[0];
            oppCategory = cat;
        }
        const behaviors = trends[cat].consumer_behavior;
        if (behaviors && behaviors.length > 0 && !behaviorFound) {
            behaviorFound = behaviors[0];
            behaviorCategory = cat;
        }
        if (opportunityFound && behaviorFound) break;
    }

    if (oppContainer) {
        oppContainer.replaceChildren();
        if (opportunityFound) {
            const chip = document.createElement('span');
            chip.className = 'text-[10px] font-label-sm bg-sustainability-green/10 text-sustainability-green px-1.5 py-0.5 rounded mr-2';
            chip.textContent = oppCategory;
            oppContainer.appendChild(chip);
            const strong = document.createElement('strong');
            strong.textContent = opportunityFound.title + ': ';
            oppContainer.appendChild(strong);
            oppContainer.appendChild(document.createTextNode(opportunityFound.desc));
        } else {
            oppContainer.textContent = 'Data peluang belum tersedia.';
        }
    }

    if (riskContainer) {
        riskContainer.replaceChildren();
        if (behaviorFound) {
            const chip = document.createElement('span');
            chip.className = 'text-[10px] font-label-sm bg-behavior-orange/10 text-behavior-orange px-1.5 py-0.5 rounded mr-2';
            chip.textContent = behaviorCategory;
            riskContainer.appendChild(chip);
            const strong = document.createElement('strong');
            strong.textContent = behaviorFound.title + ': ';
            riskContainer.appendChild(strong);
            riskContainer.appendChild(document.createTextNode(behaviorFound.desc));
        } else {
            riskContainer.textContent = 'Data perilaku konsumen belum tersedia.';
        }
    }

    // Update the box labels based on actual data found
    const oppLabel = document.querySelector('.executive-border + div .text-sustainability-green.font-bold');
    const riskLabel = document.querySelector('.executive-border + div .text-error.font-bold');
    if (oppLabel) oppLabel.textContent = 'PELUANG UTAMA';
    if (riskLabel) riskLabel.textContent = 'PERILAKU KONSUMEN';
}

// --- Render Trending Topics volume Bar Chart ---
function renderTrendingTopicsChart(trends) {
    const chartContainer = document.getElementById('trending-topics-chart-container');
    if (!chartContainer) return;
    chartContainer.replaceChildren();

    // Generate dynamic colors for any number of categories
    const colorPalette = [
        'bg-sustainability-green',
        'bg-marketing-purple',
        'bg-behavior-orange',
        'bg-blue-500',
        'bg-pink-500',
        'bg-teal-500'
    ];

    // Calculate maximum signals to compute width percentage
    let maxSignals = 0;
    Object.values(trends).forEach(catData => {
        if (catData.article_count > maxSignals) maxSignals = catData.article_count;
    });

    Object.keys(trends).forEach((cat, idx) => {
        const catData = trends[cat];
        const signalsCount = catData.article_count || 0;
        const colorClass = colorPalette[idx % colorPalette.length];
        
        const widthPct = maxSignals > 0 ? Math.round((signalsCount / maxSignals) * 100) : 0;

        const row = document.createElement('div');
        row.className = 'space-y-2';

        const labelRow = document.createElement('div');
        labelRow.className = 'flex justify-between items-center text-label-sm font-label-sm';
        
        const nameSpan = document.createElement('span');
        nameSpan.textContent = cat;
        labelRow.appendChild(nameSpan);

        const countSpan = document.createElement('span');
        countSpan.className = 'font-bold';
        countSpan.textContent = `${signalsCount} artikel`;
        labelRow.appendChild(countSpan);

        row.appendChild(labelRow);

        const barWrapper = document.createElement('div');
        barWrapper.className = 'h-8 w-full bg-surface-container-low rounded-lg overflow-hidden group';

        const barFill = document.createElement('div');
        barFill.className = `h-full ${colorClass} transition-all duration-1000 ease-out`;
        barFill.style.width = '0%';
        
        barWrapper.appendChild(barFill);
        row.appendChild(barWrapper);
        chartContainer.appendChild(row);

        // Animate width expansion
        setTimeout(() => {
            barFill.style.width = `${widthPct}%`;
        }, 100);
    });
}

// --- Render Latest Insight Cards Column ---
function renderLatestInsightsList(trends) {
    const listContainer = document.getElementById('latest-insights-list-container');
    if (!listContainer) return;
    listContainer.replaceChildren();

    // Generate dynamic tag styles for any category
    const tagStyles = [
        { bg: 'bg-sustainability-green/10', text: 'text-sustainability-green', border: 'border-sustainability-green/20' },
        { bg: 'bg-marketing-purple/10', text: 'text-marketing-purple', border: 'border-marketing-purple/20' },
        { bg: 'bg-behavior-orange/10', text: 'text-behavior-orange', border: 'border-behavior-orange/20' },
        { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' },
        { bg: 'bg-pink-100', text: 'text-pink-700', border: 'border-pink-200' },
        { bg: 'bg-teal-100', text: 'text-teal-700', border: 'border-teal-200' }
    ];

    Object.keys(trends).forEach((cat, idx) => {
        const catData = trends[cat];
        const tags = tagStyles[idx % tagStyles.length];
        
        const card = document.createElement('div');
        card.className = 'p-4 rounded-xl border border-border-subtle hover:border-secondary transition-all cursor-pointer bg-surface-container-lowest group';
        card.style.transition = 'transform 0.2s ease, border-color 0.2s ease';
        
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-2px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });

        // Navigation click handler
        card.onclick = function() {
            const periodParam = window.activeAnalysisPeriod ? `&period=${encodeURIComponent(window.activeAnalysisPeriod)}` : '';
            window.location.href = `/trend_discovery.html?trend=${encodeURIComponent(cat)}${periodParam}`;
        };

        const headerRow = document.createElement('div');
        headerRow.className = 'flex justify-between items-start mb-2';

        const badge = document.createElement('span');
        badge.className = `px-2 py-0.5 rounded text-[10px] font-label-sm uppercase tracking-wider ${tags.bg} ${tags.text} border ${tags.border}`;
        badge.textContent = cat;
        headerRow.appendChild(badge);

        // Real timestamp from first article's publish date
        let timeLabel = 'Baru';
        if (catData.articles && catData.articles.length > 0) {
            const dates = catData.articles.map(a => a.publish_date).filter(Boolean).sort().reverse();
            if (dates.length > 0) {
                const d = new Date(dates[0]);
                if (!isNaN(d.getTime())) {
                    timeLabel = d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' });
                }
            }
        }
        const timeSpan = document.createElement('span');
        timeSpan.className = 'text-[10px] font-label-sm text-text-muted';
        timeSpan.textContent = timeLabel;
        headerRow.appendChild(timeSpan);
        card.appendChild(headerRow);

        const heading = document.createElement('h4');
        heading.className = 'font-headline-md text-[16px] leading-tight text-primary mb-2 group-hover:text-secondary transition-colors';
        
        const oppTitle = catData.market_opportunities && catData.market_opportunities.length > 0 
            ? catData.market_opportunities[0].title 
            : `Analisis Tren ${cat}`;
        heading.textContent = oppTitle;
        card.appendChild(heading);

        const snippet = document.createElement('p');
        snippet.className = 'font-body-sm text-body-sm text-on-surface-variant mb-3 line-clamp-2';
        
        const briefExcerpt = catData.extractive_brief 
            ? catData.extractive_brief.split(/[.!?]+/).slice(0, 2).join('. ') + '.'
            : `Analisis dari ${catData.article_count || 0} artikel pada klaster ${cat}.`;
        snippet.textContent = briefExcerpt;
        card.appendChild(snippet);

        const footerRow = document.createElement('div');
        footerRow.className = 'flex items-center gap-2';

        const sourceSpan = document.createElement('span');
        sourceSpan.className = 'text-[10px] font-label-sm text-text-muted';
        
        // Count unique sources for this category
        const artSources = new Set();
        if (catData.articles) {
            catData.articles.forEach(a => { if (a.source) artSources.add(a.source); });
        }
        sourceSpan.textContent = `${artSources.size} portal sumber`;
        footerRow.appendChild(sourceSpan);
        
        // Add keyword chips
        if (catData.top_keywords && catData.top_keywords.length > 0) {
            const kwChip = document.createElement('span');
            kwChip.className = 'text-[10px] font-label-sm text-text-muted ml-auto';
            kwChip.textContent = catData.top_keywords.slice(0, 3).join(', ');
            footerRow.appendChild(kwChip);
        }
        
        card.appendChild(footerRow);

        listContainer.appendChild(card);
    });
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

// Event delegation for period dropdown selection
document.addEventListener('change', function(e) {
    if (e.target && e.target.id === 'dashboard-period-selector') {
        const projectId = window.TrendAI?.activeProjectId;
        if (projectId) {
            window.loadPageData(projectId, e.target.value);
        }
    }
});
