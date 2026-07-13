// TrendAI Executive Brief Page Script

// Global page load hook called by common.js
window.loadPageData = async function(projectId) {
    if (!projectId) return;

    window.TrendAI.showLoader("Memuat data laporan...");

    try {
        const urlParams = new URLSearchParams(window.location.search);
        const period = urlParams.get('period');
        
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

        // Populate Report Header Metadata
        populateReportHeader(projectId, trendsData);

        // Populate Key Indicators from real data
        populateKPIIndicators(trendsData);

        // Populate Main Narrative
        populateMainNarrative(trendsData);

        // Populate Strategic Insights List
        populateStrategicInsights(trendsData);

        // Populate Recommendations
        populateRecommendations(trendsData);

        // Populate Category Distribution Chart
        populateCategoryDistribution(trendsData);

    } catch (e) {
        window.TrendAI.hideLoader();
        console.error("Error loading executive brief data:", e);
        window.TrendAI.showToast("Terjadi kesalahan memuat laporan", "error");
    }
};

// --- Show Placeholder State if no analysis exists ---
function showPlaceholderState() {
    let placeholder = document.getElementById('brief-placeholder-overlay');
    if (!placeholder) {
        placeholder = document.createElement('div');
        placeholder.id = 'brief-placeholder-overlay';
        placeholder.className = 'a4-card border border-dashed border-slate-300 rounded-xl bg-slate-50 flex flex-col items-center justify-center text-center gap-4 my-6 no-print';
        
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
        
        const mainContent = document.querySelector('main');
        if (mainContent) {
            const reportContainer = document.querySelector('.a4-card:not(#brief-placeholder-overlay)');
            if (reportContainer) {
                reportContainer.style.display = 'none';
                mainContent.insertBefore(placeholder, reportContainer);
            } else {
                mainContent.insertBefore(placeholder, mainContent.firstChild);
            }
        }
    } else {
        placeholder.style.display = 'flex';
        const reportContainer = document.querySelector('.a4-card:not(#brief-placeholder-overlay)');
        if (reportContainer) reportContainer.style.display = 'none';
    }
}

function hidePlaceholderState() {
    const placeholder = document.getElementById('brief-placeholder-overlay');
    if (placeholder) {
        placeholder.style.display = 'none';
    }
    const reportContainer = document.querySelector('.a4-card:not(#brief-placeholder-overlay)');
    if (reportContainer) reportContainer.style.display = 'block';
}

// --- Populate report header with real data ---
function populateReportHeader(projectId, trends) {
    const periodSpan = document.getElementById('report-period-dates');
    const idSpan = document.getElementById('report-id-badge');

    // Actual date range based on article publish dates
    let allDates = [];
    Object.values(trends).forEach(cat => {
        if (cat.articles) {
            cat.articles.forEach(a => {
                if (a.publish_date) allDates.push(new Date(a.publish_date));
            });
        }
    });
    allDates = allDates.filter(d => !isNaN(d.getTime())).sort((a, b) => a - b);

    const now = new Date();
    const formatDate = (d) => d.toLocaleDateString('id-ID', { month: 'short', day: 'numeric', year: 'numeric' });
    
    if (periodSpan) {
        if (allDates.length > 0) {
            periodSpan.textContent = `Periode: ${formatDate(allDates[0])} - ${formatDate(allDates[allDates.length - 1])}`;
        } else {
            const lastWeek = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            periodSpan.textContent = `Periode: ${formatDate(lastWeek)} - ${formatDate(now)}`;
        }
    }
    if (idSpan) {
        const totalArts = Object.values(trends).reduce((sum, c) => sum + (c.article_count || 0), 0);
        idSpan.textContent = `Laporan: ${totalArts} artikel terindeks`;
    }
}

// --- Populate real KPI indicators from data ---
function populateKPIIndicators(trends) {
    const categories = Object.keys(trends);
    let totalArticles = 0;
    let totalKeywords = new Set();
    
    Object.values(trends).forEach(cat => {
        totalArticles += (cat.article_count || 0);
        if (cat.top_keywords) {
            cat.top_keywords.forEach(k => totalKeywords.add(k));
        }
    });

    // Update Sentiment Shift -> now shows total keywords found
    const shiftVal = document.getElementById('brief-sentiment-shift');
    const shiftDesc = document.getElementById('brief-sentiment-desc');
    if (shiftVal) {
        shiftVal.textContent = `${totalKeywords.size} kata kunci`;
    }
    if (shiftDesc) {
        shiftDesc.textContent = `Teridentifikasi dari ${totalArticles} artikel`;
    }

    // Competitive Noise -> shows number of categories
    const noiseVal = document.getElementById('brief-competitive-noise');
    const noiseDesc = document.getElementById('brief-noise-desc');
    if (noiseVal) {
        noiseVal.textContent = categories.length;
    }
    if (noiseDesc) {
        noiseDesc.textContent = `${categories.join(', ')}`;
    }

    // Market Volatility -> shows total articles count
    const volatilityVal = document.getElementById('brief-market-volatility');
    const volDesc = document.getElementById('brief-volatility-desc');
    if (volatilityVal) {
        volatilityVal.textContent = totalArticles;
    }
    if (volDesc) {
        volDesc.textContent = `Total artikel terproses`;
    }
}

// --- Populate Main Trend Summary with real data ---
function populateMainNarrative(trends) {
    const container = document.getElementById('brief-narrative-container');
    if (!container) return;
    container.replaceChildren();

    // Use the generative brief of each trend as the main executive story
    const categories = Object.keys(trends);
    if (categories.length === 0) return;

    const colorMap = ['text-secondary', 'text-marketing-purple', 'text-behavior-orange', 'text-blue-600', 'text-pink-600'];

    categories.forEach((cat, idx) => {
        const data = trends[cat];
        const wrapper = document.createElement('div');
        wrapper.className = 'mb-stack-md';
        
        const header = document.createElement('h4');
        header.className = `font-label-md font-bold ${colorMap[idx % colorMap.length]} mb-1 uppercase tracking-wider`;
        header.textContent = cat;
        wrapper.appendChild(header);
        
        const text = data.generative_brief || data.extractive_brief || 'Belum ada ringkasan.';
        
        // Render 4-point structured text beautifully and safely
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
            wrapper.appendChild(lineEl);
        });
        
        container.appendChild(wrapper);
    });
}

// --- Populate Strategic Insights List from real data ---
function populateStrategicInsights(trends) {
    const container = document.getElementById('brief-insights-list');
    if (!container) return;
    container.replaceChildren();

    const palette = [
        { bg: 'bg-sustainability-green/10', text: 'text-sustainability-green', accent: 'border-l-sustainability-green' },
        { bg: 'bg-marketing-purple/10', text: 'text-marketing-purple', accent: 'border-l-marketing-purple' },
        { bg: 'bg-behavior-orange/10', text: 'text-behavior-orange', accent: 'border-l-behavior-orange' },
        { bg: 'bg-blue-100', text: 'text-blue-700', accent: 'border-l-blue-500' },
        { bg: 'bg-pink-100', text: 'text-pink-700', accent: 'border-l-pink-500' }
    ];

    Object.keys(trends).forEach((cat, idx) => {
        const data = trends[cat];
        const style = palette[idx % palette.length];
        
        const row = document.createElement('div');
        row.className = `border border-border-subtle rounded-lg p-stack-md ${style.accent} border-l-4`;

        const badgeRow = document.createElement('div');
        badgeRow.className = 'flex items-center gap-2 mb-2';
        row.appendChild(badgeRow);

        const badge = document.createElement('span');
        badge.className = `px-2 py-0.5 font-label-sm text-label-sm rounded uppercase ${style.bg} ${style.text}`;
        badge.textContent = cat;
        badgeRow.appendChild(badge);

        const kwSpan = document.createElement('span');
        kwSpan.className = 'font-label-sm text-label-sm text-text-muted';
        kwSpan.textContent = `${data.article_count || 0} artikel`;
        badgeRow.appendChild(kwSpan);

        const heading = document.createElement('h3');
        heading.className = 'font-body-md text-body-md font-bold mb-2';
        
        const oppTitle = data.market_opportunities && data.market_opportunities.length > 0 
            ? data.market_opportunities[0].title 
            : `Ringkasan Tren ${cat}`;
        heading.textContent = oppTitle;
        row.appendChild(heading);

        const desc = document.createElement('p');
        desc.className = 'font-body-sm text-body-sm text-on-surface-variant leading-snug';
        
        // Use generative brief excerpt
        let brief = data.generative_brief || data.extractive_brief || '';
        if (brief) {
            brief = brief.replace(/^\*\*Executive Brief\*\*\s*/i, '');
            const sentences = brief.match(/[^.!?]+[.!?]+/g) || [brief];
            desc.textContent = sentences.slice(0, 2).join(' ');
        } else {
            desc.textContent = `Analisis berdasarkan ${data.article_count || 0} artikel pada kategori ${cat}.`;
        }
        row.appendChild(desc);
        
        // Keywords row
        if (data.top_keywords && data.top_keywords.length > 0) {
            const kwRow = document.createElement('div');
            kwRow.className = 'flex flex-wrap gap-1 mt-2';
            data.top_keywords.slice(0, 4).forEach(kw => {
                const chip = document.createElement('span');
                chip.className = `text-[10px] px-1.5 py-0.5 rounded ${style.bg} ${style.text}`;
                chip.textContent = kw;
                kwRow.appendChild(chip);
            });
            row.appendChild(kwRow);
        }

        container.appendChild(row);
    });
}

// --- Populate Recommendations from real data ---
function populateRecommendations(trends) {
    const list = document.getElementById('brief-recommendations-list');
    if (!list) return;
    list.replaceChildren();

    let counter = 0;
    const priorityLabels = ['Prioritas Tinggi', 'Rencana Jangka Pendek', 'Inisiatif Strategis'];

    Object.keys(trends).forEach(cat => {
        const opps = trends[cat].market_opportunities || [];
        opps.forEach(opp => {
            if (counter >= 3) return;

            const row = document.createElement('div');
            row.className = 'flex gap-4';

            const numBox = document.createElement('div');
            numBox.className = `flex-shrink-0 w-8 h-8 rounded-full bg-secondary text-on-secondary flex items-center justify-center font-label-md text-label-md`;
            numBox.textContent = `0${counter + 1}`;
            row.appendChild(numBox);

            const contentDiv = document.createElement('div');
            
            const title = document.createElement('h4');
            title.className = 'font-body-md text-body-md font-bold';
            title.textContent = opp.title;
            contentDiv.appendChild(title);

            const catLabel = document.createElement('span');
            catLabel.className = 'font-label-sm text-label-sm text-secondary';
            catLabel.textContent = `Kategori: ${cat}`;
            contentDiv.appendChild(catLabel);

            const desc = document.createElement('p');
            desc.className = 'font-body-sm text-body-sm text-on-surface-variant mt-2 leading-relaxed';
            desc.textContent = opp.desc;
            contentDiv.appendChild(desc);

            row.appendChild(contentDiv);
            list.appendChild(row);

            counter++;
        });
    });

    if (counter === 0) {
        const emptyMsg = document.createElement('p');
        emptyMsg.className = 'font-body-sm text-text-muted';
        emptyMsg.textContent = 'Belum ada rekomendasi dari data analisis.';
        list.appendChild(emptyMsg);
    }
}

// --- Populate Category Distribution bar chart ---
function populateCategoryDistribution(trends) {
    const container = document.getElementById('brief-performance-chart-container');
    if (!container) return;
    container.replaceChildren();

    // 1. Calculate total articles
    let totalCount = 0;
    const categories = Object.keys(trends);
    categories.forEach(cat => {
        totalCount += trends[cat].article_count || 0;
    });

    if (totalCount === 0) {
        container.textContent = 'Tidak ada data artikel.';
        container.className = 'flex items-center justify-center h-full text-xs text-text-muted';
        return;
    }

    container.className = 'w-full flex flex-col gap-3.5 py-1';

    // 2. Color palette matching other visual elements
    const palette = [
        { bar: 'bg-secondary', text: 'text-secondary' },
        { bar: 'bg-marketing-purple', text: 'text-marketing-purple' },
        { bar: 'bg-behavior-orange', text: 'text-behavior-orange' },
        { bar: 'bg-blue-500', text: 'text-blue-500' },
        { bar: 'bg-pink-500', text: 'text-pink-500' }
    ];

    // 3. Render rows
    categories.forEach((cat, idx) => {
        const count = trends[cat].article_count || 0;
        const pct = Math.round((count / totalCount) * 100);
        const style = palette[idx % palette.length];

        const row = document.createElement('div');
        row.className = 'flex items-center justify-between text-xs font-body-sm text-slate-700 mt-0.5';

        // Label column
        const labelCol = document.createElement('div');
        labelCol.className = 'w-24 truncate font-bold text-slate-800';
        labelCol.textContent = cat;
        row.appendChild(labelCol);

        // Bar column
        const barCol = document.createElement('div');
        barCol.className = 'flex-grow mx-4 relative';
        
        const track = document.createElement('div');
        track.className = 'h-2 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200/50';
        
        const fill = document.createElement('div');
        fill.className = `h-full rounded-full transition-all duration-500 ${style.bar}`;
        fill.style.width = `${pct}%`;
        
        track.appendChild(fill);
        barCol.appendChild(track);
        
        // Percent badge overlay
        const pctText = document.createElement('span');
        pctText.className = 'absolute right-0 -top-4 text-[9px] font-bold text-text-muted';
        pctText.textContent = `${pct}%`;
        barCol.appendChild(pctText);

        row.appendChild(barCol);

        // Count column
        const countCol = document.createElement('div');
        countCol.className = 'w-8 text-right font-label-sm font-bold';
        countCol.textContent = count;
        row.appendChild(countCol);

        container.appendChild(row);
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


