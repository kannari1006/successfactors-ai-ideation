document.addEventListener('DOMContentLoaded', () => {
    let lastFetchedTimestamp = '';
    let pollingInterval = null;
    let highlightInterval = null;

    const API_IDEAS = '/api/ideas';
    const API_UPDATE_CHECK = '/api/check_updates';
    const UPDATE_THRESHOLD_MS = 10 * 60 * 1000; // 10 minutes

    const banner = document.getElementById('update-banner');
    const loading = document.getElementById('loading');
    const ideasGrid = document.getElementById('ideas-grid');
    const totalCountEl = document.getElementById('total-ideas');

    let currentIdeas = []; // Global storage for filtering

    // Make it globally accessible for the onclick in HTML
    window.fetchAndRenderIdeas = fetchAndRenderIdeas;
    window.toggleDetails = function (btn) {
        const details = btn.nextElementSibling;
        if (details.style.display === 'none') {
            details.style.display = 'block';
            btn.innerHTML = '詳細を閉じる <i class="fas fa-chevron-up"></i>';
        } else {
            details.style.display = 'none';
            btn.innerHTML = '詳細を見る <i class="fas fa-chevron-down"></i>';
        }
    };

    async function fetchAndRenderIdeas() {
        try {
            const reqTime = new Date().getTime();
            const res = await fetch(API_IDEAS);
            currentIdeas = await res.json(); // Store globally

            // Hide banner since we are updating
            banner.classList.remove('visible');
            setTimeout(() => { if (!banner.classList.contains('visible')) banner.style.display = 'none'; }, 400);

            if (currentIdeas.length > 0) {
                // Determine the highest updated_at to save as our last known
                lastFetchedTimestamp = currentIdeas[0].updated_at; // since it's sorted desc from backend

                // Hide loading
                loading.classList.add('hidden');
                totalCountEl.textContent = currentIdeas.length;

                populateFilters(currentIdeas);
                renderFilteredGrid();
            } else {
                loading.innerHTML = "<p>まだアイディアがありません。AIが考案中です...</p>";
                totalCountEl.textContent = "0";
            }
        } catch (e) {
            console.error("Failed to fetch ideas", e);
        }
    }

    // Bind event listeners to filters
    document.getElementById('filter-target')?.addEventListener('change', renderFilteredGrid);
    document.getElementById('filter-module')?.addEventListener('change', renderFilteredGrid);
    document.getElementById('filter-audience')?.addEventListener('change', renderFilteredGrid);
    document.getElementById('sort-score')?.addEventListener('change', renderFilteredGrid);

    function renderFilteredGrid() {
        const targetFilter = document.getElementById('filter-target')?.value || 'all';
        const moduleFilter = document.getElementById('filter-module')?.value || 'all';
        const audienceFilter = document.getElementById('filter-audience')?.value || 'all';
        const sortOrder = document.getElementById('sort-score')?.value || 'default';

        let filtered = currentIdeas.filter(idea => {
            let matchTarget = targetFilter === 'all' || idea.target === targetFilter;
            let matchModule = moduleFilter === 'all' || (idea.modules && idea.modules.includes(moduleFilter));
            let matchAudience = audienceFilter === 'all' || (idea.target_audience && idea.target_audience.includes(audienceFilter));
            return matchTarget && matchModule && matchAudience;
        });

        if (sortOrder === 'desc') {
            filtered.sort((a, b) => (b.recommendation_score || 0) - (a.recommendation_score || 0));
        } else if (sortOrder === 'asc') {
            filtered.sort((a, b) => (a.recommendation_score || 0) - (b.recommendation_score || 0));
        }

        renderGrid(filtered);
    }

    function renderGrid(ideas) {
        ideasGrid.innerHTML = '';
        const now = new Date().getTime();

        ideas.forEach(idea => {
            const updatedAt = new Date(idea.updated_at).getTime();
            const isRecent = (now - updatedAt) <= UPDATE_THRESHOLD_MS;

            const card = document.createElement('div');
            card.className = `card ${isRecent ? 'recently-updated' : ''}`;
            card.setAttribute('data-updated-at', idea.updated_at);

            const timeStr = new Date(idea.updated_at).toLocaleString('ja-JP', {
                month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });

            let scheduleHtml = '';
            let s = null;
            if (idea.schedule) {
                if (Array.isArray(idea.schedule)) {
                    s = {
                        durations: idea.schedule.length,
                        tracks: [
                            { name: "全体スケジュール", items: [] },
                            { name: "ベンダー（導入）", items: [] },
                            { name: "企業側(人事・情シス)", items: [] }
                        ],
                        tasks: []
                    };
                    idea.schedule.forEach((phase, i) => {
                        const m = i + 1;
                        const phaseName = phase.phase || phase.month || `Phase ${m}`;

                        s.tracks[0].items.push({ name: phaseName, start: m, end: m });

                        let vendorTasks = [];
                        let clientTasks = [];

                        if (phase.tasks && Array.isArray(phase.tasks)) {
                            phase.tasks.forEach(t => {
                                let actor = t.actor || '';
                                if (!actor && t.raci) {
                                    const raciStr = t.raci;
                                    const vMatch = raciStr.match(/V:\s*([A-Za-z,]+)/);
                                    const cMatch = raciStr.match(/C:\s*([A-Za-z,]+)/);
                                    const vAr = vMatch && (vMatch[1].includes('A') || vMatch[1].includes('R'));
                                    const cAr = cMatch && (cMatch[1].includes('A') || cMatch[1].includes('R'));

                                    if (vAr && cAr) actor = '全体';
                                    else if (vAr) actor = 'ベンダー';
                                    else if (cAr) actor = '顧客';
                                    else actor = '全体';
                                }

                                s.tasks.push({ ...t, phase: phaseName, actor: actor });

                                if (actor === 'ベンダー') vendorTasks.push(t.name);
                                else if (actor === '顧客') clientTasks.push(t.name);
                            });
                        }

                        if (vendorTasks.length > 0) {
                            s.tracks[1].items.push({ name: vendorTasks.join(' / '), start: m, end: m });
                        }
                        if (clientTasks.length > 0) {
                            s.tracks[2].items.push({ name: clientTasks.join(' / '), start: m, end: m });
                        }
                    });
                } else if (idea.schedule.tracks) {
                    s = idea.schedule;
                }
            }

            if (s && s.tracks) {
                const durations = s.durations || 3;

                // Header
                let ganttHtml = `<div class="gantt-chart" style="--total-months: ${durations};">`;
                ganttHtml += `<div class="gantt-header-label" style="grid-row: 1; grid-column: 1 / 2;">担当 / フェーズ</div>`;
                for (let i = 1; i <= durations; i++) {
                    ganttHtml += `<div class="gantt-header-cell" style="grid-row: 1; grid-column: ${i + 1} / ${i + 2};">Month ${i}</div>`;
                }

                s.tracks.forEach((track, idx) => {
                    const row = idx + 2;
                    ganttHtml += `<div class="gantt-track-label" style="grid-row: ${row}; grid-column: 1 / 2;">${track.name}</div>`;

                    for (let i = 1; i <= durations; i++) {
                        ganttHtml += `<div class="gantt-bg-cell" style="grid-row: ${row}; grid-column: ${i + 1} / ${i + 2};"></div>`;
                    }

                    // Track Items (Chevron blocks)
                    track.items.forEach(item => {
                        let classStr = "gantt-bar";
                        if (idx === 0) classStr += " gantt-bar-overall";
                        else if (idx === 1) classStr += " gantt-bar-vendor";
                        else classStr += " gantt-bar-client";

                        // item.start is 1-indexed (Month 1 => start column 2)
                        // item.end is 1-indexed (end at Month 2 => end column 4)
                        const gridColStart = item.start + 1;
                        const gridColEnd = item.end + 2;

                        ganttHtml += `<div class="${classStr}" style="grid-row: ${row}; grid-column: ${gridColStart} / ${gridColEnd};" title="${item.name}"><span>${item.name}</span></div>`;
                    });
                });
                ganttHtml += `</div>`;

                // --- Task Detail Table ---
                let tasksHtml = '';
                (s.tasks || []).forEach(t => {
                    let actorBadgeClass = 'target'; // Default background (green)
                    if (t.actor === 'ベンダー') actorBadgeClass = 'vendor';
                    else if (t.actor === '全体') actorBadgeClass = 'overall';

                    tasksHtml += `
                        <tr>
                            <td><span class="task-actor-badge ${actorBadgeClass}">${t.actor || ''}</span></td>
                            <td>${t.phase || ''}</td>
                            <td>${t.name}</td>
                            <td>${t.duration}</td>
                            <td>${t.dependency}</td>
                        </tr>
                    `;
                });

                const taskTableHtml = `
                    <div class="table-responsive">
                        <table class="bordered-table">
                            <thead>
                                <tr>
                                    <th>担当 (Actor)</th>
                                    <th>フェーズ (Phase)</th>
                                    <th>タスク (Task)</th>
                                    <th>期間 (Duration)</th>
                                    <th>依存関係 (Dependency)</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tasksHtml}
                            </tbody>
                        </table>
                    </div>
                `;

                scheduleHtml = `
                    <div class="schedule-section">
                        <h4>IMPLEMENTATION SCHEDULE (導入スケジュール)</h4>
                        ${ganttHtml}
                        ${taskTableHtml}
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="update-label">10分以内の更新</div>
                <div class="card-header">
                    <span class="persona-badge">${idea.persona}</span>
                    <span class="cost-badge">${idea.cost || 'コスト未定'}</span>
                </div>
                <h3 class="card-title">${idea.title}</h3>
                <div class="card-content">
                    <div class="attribute-row">
                        <span class="attr-label">ターゲット (Target)</span>
                        <span class="attr-value target">${idea.target || '未定'}</span>
                    </div>
                    ${idea.target_audience ? `
                    <div class="attribute-row">
                        <span class="attr-label">対象層 (Audience)</span>
                        <span class="attr-value audience">${idea.target_audience}</span>
                    </div>` : ''}
                    <div class="attribute-row">
                        <span class="attr-label">関連モジュール (Modules)</span>
                        <span class="attr-value modules">${idea.modules || '未定'}</span>
                    </div>
                    ${idea.difficulty ? `
                    <div class="attribute-row difficulty-row">
                        <span class="attr-label">難易度 (Difficulty)</span>
                        <span class="attr-value difficulty">${idea.difficulty}</span>
                    </div>` : ''}
                    ${idea.reference ? `
                    <div class="attribute-row reference-row">
                        <span class="attr-label">参考ソース (Reference)</span>
                        <a href="${idea.reference}" target="_blank" class="attr-value reference">${idea.reference}</a>
                    </div>` : ''}
                    ${idea.recommendation_score ? `
                    <div class="attribute-row">
                        <span class="attr-label">AI推奨度 (Score)</span>
                        <span class="attr-value score">
                            ${'★'.repeat(idea.recommendation_score)}${'☆'.repeat(5 - idea.recommendation_score)}
                        </span>
                    </div>` : ''}
                    ${idea.viewpoint ? `
                    <div class="viewpoint-box">
                        <strong><i class="fas fa-user-tie"></i> ${idea.persona}からの提案アピール:</strong><br/>
                        ${idea.viewpoint.replace(`【${idea.persona}見解】`, '').trim()}
                    </div>
                    ` : ''}
                    ${idea.review_comment ? `
                    <div class="viewpoint-box reviewer-box">
                        <strong><i class="fas fa-search"></i> レビューフィードバック:</strong><br/>
                        ${idea.review_comment}
                    </div>
                    ` : ''}
                    
                    <button class="toggle-details" onclick="toggleDetails(this)">詳細を見る <i class="fas fa-chevron-down"></i></button>
                    
                    <div class="card-details" style="display: none;">
                        <h4>APPROACH (アプローチ)</h4>
                        <p>${(idea.approach || '').replace(/\n/g, '<br>')}</p>
                        <h4>RATIONALE (根拠)</h4>
                        <p>${(idea.rationale || '').replace(/\n/g, '<br>')}</p>
                        ${scheduleHtml}
                    </div>
                </div>
                <div class="card-footer">
                    <span>最終更新: ${timeStr}</span>
                </div>
            `;
            ideasGrid.appendChild(card);
        });
    }

    async function checkForUpdates() {
        if (!lastFetchedTimestamp) return;

        try {
            const res = await fetch(`${API_UPDATE_CHECK}?last_timestamp=${encodeURIComponent(lastFetchedTimestamp)}`);
            const data = await res.json();

            if (data.has_updates) {
                // Show banner
                banner.style.display = 'flex';
                // Trigger reflow to ensure transition runs
                void banner.offsetWidth;
                banner.classList.add('visible');
            }
        } catch (e) {
            console.error("Failed to check for updates", e);
        }
    }

    function scanForHighlights() {
        // Runs periodically to verify if cards should still have the "recently-updated" class
        const now = new Date().getTime();
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const updatedTimeStr = card.getAttribute('data-updated-at');
            if (updatedTimeStr) {
                const updatedAt = new Date(updatedTimeStr).getTime();
                if ((now - updatedAt) <= UPDATE_THRESHOLD_MS) {
                    card.classList.add('recently-updated');
                } else {
                    card.classList.remove('recently-updated');
                }
            }
        });
    }

    // Initialize
    fetchAndRenderIdeas();
    fetchEvents();

    // Poll for updates every 5 seconds without freezing GUI
    pollingInterval = setInterval(checkForUpdates, 5000);
    setInterval(fetchEvents, 3000); // Poll events frequently for the live feed feel

    // Update highlights every 30 seconds to remove expired highlights smoothly
    highlightInterval = setInterval(scanForHighlights, 30000);
});

async function fetchEvents() {
    try {
        const res = await fetch('/api/events');
        const events = await res.json();
        const eventsList = document.getElementById('events-list');

        if (events && events.length > 0) {
            eventsList.innerHTML = events.map(e => `
                <div class="event-item">
                    <div class="event-time">${new Date(e.timestamp).toLocaleString('ja-JP', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</div>
                    <div class="event-msg">${e.message}</div>
                </div>
            `).join('');
        } else {
            eventsList.innerHTML = '<p style="color:var(--text-secondary);font-size:0.85rem">まだ履歴がありません</p>';
        }
    } catch (e) { console.error("Failed to fetch events", e); }
}

// Populate Filtering Dropdowns Dynamically
function populateFilters(data) {
    const modulesSet = new Set();
    const audienceSet = new Set();

    data.forEach(item => {
        if (item.modules) {
            item.modules.split(',').forEach(m => modulesSet.add(m.trim()));
        }
        if (item.target_audience) {
            item.target_audience.split('・').forEach(a => audienceSet.add(a.trim()));
        }
    });

    const moduleSelect = document.getElementById('filter-module');
    // Keep 'all' option, remove others
    while (moduleSelect.options.length > 1) { moduleSelect.remove(1); }
    modulesSet.forEach(m => {
        moduleSelect.add(new Option(m, m));
    });

    const audienceSelect = document.getElementById('filter-audience');
    while (audienceSelect.options.length > 1) { audienceSelect.remove(1); }
    audienceSet.forEach(a => {
        audienceSelect.add(new Option(a, a));
    });
}
