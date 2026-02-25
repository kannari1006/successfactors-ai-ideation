import streamlit as st
import json
import os
import threading
import asyncio
from datetime import datetime, timezone
import re
from ai_worker import run_ai_simulation

# --- Page Config ---
# Must be the very first Streamlit command
st.set_page_config(
    page_title="SuccessFactors AI Ideation Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialization & Background Worker ---

# Start background AI simulation in a separate thread, running an asyncio loop
@st.cache_resource
def start_worker():
    def _run():
        try:
            asyncio.run(run_ai_simulation())
        except Exception as e:
            print(f"Background worker failed: {e}")
            
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t

# Ensure the worker starts once
start_worker()

# --- CSS Injection ---
def load_css():
    try:
        with open("static/style.css", "r", encoding="utf-8") as f:
            css = f.read()
            
        # Add Streamlit-specific overrides to make the app feel like the custom UI
        st_overrides = """
        <style>
        /* Hide default Streamlit header */
        header[data-testid="stHeader"] { display: none; }
        
        /* Maximize width and fix padding */
        .block-container {
            padding-top: 1rem !important;
            max-width: 1400px !important;
        }
        
        /* Streamlit background matching */
        .stApp {
            background-color: #0b0f19;
        }
        
        /* Details/Summary implementation for the toggle feature to mimic button */
        details.idea-details {
            margin-top: 15px;
        }
        details.idea-details summary {
            cursor: pointer;
            padding: 8px 12px;
            color: var(--text-muted);
            font-size: 0.9rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.03);
            display: block;
            text-align: center;
            transition: all 0.2s ease;
            list-style: none;
        }
        details.idea-details summary::-webkit-details-marker {
            display: none;
        }
        details.idea-details summary:hover {
            border-color: var(--primary);
            color: var(--primary);
            background: rgba(100, 255, 218, 0.05);
        }
        details.idea-details[open] summary::before { content: "詳細を閉じる ▲"; }
        details.idea-details:not([open]) summary::before { content: "詳細を見る ▼"; }
        
        .card-details {
            padding-top: 15px;
            margin-top: 15px;
            border-top: 1px dashed var(--border-color);
        }
        </style>
        """
        st.markdown(re.sub(r'\n\s*', '', f"<style>{css}</style>{st_overrides}"), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load CSS: {e}")

load_css()

# --- Data Loading ---
def load_ideas():
    if not os.path.exists("ideas.json"):
        return []
    with open("ideas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return sorted(data, key=lambda x: x.get("updated_at", ""), reverse=True)

def load_events():
    if not os.path.exists("events.json"):
        return []
    with open("events.json", "r", encoding="utf-8") as f:
        return json.load(f)

# --- Components ---
def create_gantt_html(schedule):
    if not isinstance(schedule, dict) or 'tracks' not in schedule:
        return "<p style='color: #8892b0; font-size: 0.8rem;'>スケジュール情報がありません</p>"
        
    durations = schedule.get("durations", 3)
    tracks = schedule.get("tracks", [])
    
    html = f'<div class="gantt-chart" style="--total-months: {durations};">'
    html += '<div class="gantt-header-label" style="grid-row: 1; grid-column: 1 / 2;">担当 / フェーズ</div>'
    for i in range(1, durations + 1):
        html += f'<div class="gantt-header-cell" style="grid-row: 1; grid-column: {i + 1} / {i + 2};">Month {i}</div>'
        
    for idx, track in enumerate(tracks):
        row = idx + 2
        html += f'<div class="gantt-track-label" style="grid-row: {row}; grid-column: 1 / 2;">{track.get("name", "Track")}</div>'
        
        for i in range(1, durations + 1):
            html += f'<div class="gantt-bg-cell" style="grid-row: {row}; grid-column: {i + 1} / {i + 2};"></div>'
            
        for item in track.get("items", []):
            class_str = "gantt-bar"
            if idx == 0:
                class_str += " gantt-bar-overall"
            elif idx == 1:
                class_str += " gantt-bar-vendor"
            else:
                class_str += " gantt-bar-client"
                
            start = item.get('start', 1)
            end = item.get('end', 1)
            grid_col_start = start + 1
            grid_col_end = end + 2
            
            item_name = item.get('name', 'Task')
            html += f'<div class="{class_str}" style="grid-row: {row}; grid-column: {grid_col_start} / {grid_col_end};" title="{item_name}"><span>{item_name}</span></div>'
            
    html += "</div>"
    return html

def render_idea_card(idea):
    score = idea.get('recommendation_score', 3)
    stars_html = f"{'★' * score}{'☆' * (5 - score)}"
    
    diff_text = str(idea.get('difficulty', '未設定'))
    
    vp_html = ""
    if idea.get('viewpoint'):
        vp_text = idea['viewpoint'].replace(f"【{idea.get('persona', '')}見解】", "").strip()
        vp_html = f"""
        <div class="viewpoint-box" style="border-left-color: var(--primary);">
            <strong><i class="fas fa-lightbulb"></i> {idea.get('persona', '提案者')}からの提案アピール:</strong><br/>
            {vp_text}
        </div>
        """
        
    rev_html = ""
    if idea.get('review_comment'):
        rev_html = f"""
        <div class="viewpoint-box reviewer-box">
            <strong><i class="fas fa-search"></i> レビューフィードバック:</strong><br/>
            {idea['review_comment']}
        </div>
        """
        
    ref_html = ""
    if idea.get('reference'):
        ref_html = f"""
        <div class="attribute-row reference-row">
            <span class="attr-label">参考ソース (Reference)</span>
            <a href="{idea['reference']}" target="_blank" class="attr-value reference">{idea['reference']}</a>
        </div>
        """
        
    aud_html = ""
    if idea.get('target_audience'):
        aud_html = f"""
        <div class="attribute-row">
            <span class="attr-label">対象層 (Audience)</span>
            <span class="attr-value audience">{idea['target_audience']}</span>
        </div>
        """

    raw_schedule = idea.get('schedule', {})
    schedule_data = {}
    
    if isinstance(raw_schedule, dict):
        schedule_data = raw_schedule
    elif isinstance(raw_schedule, list):
        durations = len(raw_schedule)
        tracks = [
            {"name": "全体スケジュール", "items": []},
            {"name": "ベンダー（導入）", "items": []},
            {"name": "企業側(人事・情シス)", "items": []}
        ]
        tasks = []
        for i, phase in enumerate(raw_schedule):
            m = i + 1
            phase_name = phase.get('phase') or phase.get('month') or f"Phase {m}"
            tracks[0]["items"].append({
                "name": phase_name,
                "start": m,
                "end": m
            })
            
            v_tasks = []
            c_tasks = []
            
            for t in phase.get('tasks', []):
                new_t = t.copy()
                new_t['phase'] = phase_name
                
                actor = new_t.get('actor', '')
                if not actor and 'raci' in new_t:
                    raci_str = new_t['raci']
                    import re
                    v_match = re.search(r'V:\s*([A-Za-z,]+)', raci_str)
                    c_match = re.search(r'C:\s*([A-Za-z,]+)', raci_str)
                    v_ar = bool(v_match and ('A' in v_match.group(1) or 'R' in v_match.group(1)))
                    c_ar = bool(c_match and ('A' in c_match.group(1) or 'R' in c_match.group(1)))
                    
                    if v_ar and c_ar:
                        actor = '全体'
                    elif v_ar:
                        actor = 'ベンダー'
                    elif c_ar:
                        actor = '顧客'
                    else:
                        actor = '全体'
                        
                new_t['actor'] = actor
                tasks.append(new_t)
                
                if actor == 'ベンダー':
                    v_tasks.append(new_t.get('name', ''))
                elif actor == '顧客':
                    c_tasks.append(new_t.get('name', ''))
                    
            if v_tasks:
                tracks[1]["items"].append({"name": " / ".join(v_tasks), "start": m, "end": m})
            if c_tasks:
                tracks[2]["items"].append({"name": " / ".join(c_tasks), "start": m, "end": m})
        
        schedule_data = {
            "durations": durations,
            "tracks": tracks,
            "tasks": tasks
        }
        
    tasks = schedule_data.get('tasks', [])
    task_html = ""
    if tasks:
        task_html = """
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
        """
        for t in tasks:
            if isinstance(t, dict):
                actor = t.get('actor', '')
                actor_badge_class = 'target'
                if actor == 'ベンダー':
                    actor_badge_class = 'vendor'
                elif actor == '全体':
                    actor_badge_class = 'overall'
                
                task_html += f"<tr><td><span class='task-actor-badge {actor_badge_class}'>{actor}</span></td><td>{t.get('phase', '')}</td><td>{t.get('name', '')}</td><td>{t.get('duration', '')}</td><td>{t.get('dependency', '')}</td></tr>"
            else:
                task_html += f"<tr><td colspan='5'>{str(t)}</td></tr>"
        task_html += "</tbody></table></div>"
        
    schedule_html = ""
    if schedule_data:
        schedule_html = f"""
        <div class="schedule-section">
            <h4>IMPLEMENTATION SCHEDULE (導入スケジュール)</h4>
            {create_gantt_html(schedule_data)}
            {task_html}
        </div>
        """

    card_html = f"""
    <div class="card" data-updated-at="{idea.get('updated_at', '')}">
        <div class="card-header">
            <span class="persona-badge">{idea.get('persona', 'Unknown')}</span>
            <span class="cost-badge">{idea.get('cost', 'コスト未定')}</span>
        </div>
        <h3 class="card-title">{idea.get('title', 'No Title')}</h3>
        
        <div class="card-content">
            <div class="attribute-row">
                <span class="attr-label">ターゲット (Target)</span>
                <span class="attr-value target">{idea.get('target', '未定')}</span>
            </div>
            {aud_html}
            <div class="attribute-row">
                <span class="attr-label">関連モジュール (Modules)</span>
                <span class="attr-value modules">{idea.get('modules', '未定')}</span>
            </div>
            <div class="attribute-row difficulty-row">
                <span class="attr-label">難易度 (Difficulty)</span>
                <span class="attr-value difficulty">{diff_text}</span>
            </div>
            {ref_html}
            <div class="attribute-row">
                <span class="attr-label">AI推奨度 (Score)</span>
                <span class="attr-value score">{stars_html}</span>
            </div>
            
            {vp_html}
            {rev_html}
            
            <details class="idea-details">
                <summary></summary>
                <div class="card-details">
                    <h4>APPROACH (アプローチ)</h4>
                    <p>{idea.get('approach', '').replace('\n', '<br>')}</p>
                    <h4>RATIONALE (根拠)</h4>
                    <p>{idea.get('rationale', '').replace('\n', '<br>')}</p>
                    {schedule_html}
                </div>
            </details>
        </div>
        <div class="card-footer">
            <span>最終更新: {idea.get('updated_at', '')[:10]}</span>
        </div>
    </div>
    """
    return re.sub(r'\n\s*', '', card_html)


# --- Main Application ---
def main():
    ideas = load_ideas()
    events = load_events()
    
    # Render Streamlit Sidebar Filters
    st.sidebar.title("フィルター & ソート")
    st.sidebar.markdown("---")
    
    target_options = ["すべて"] + sorted(list(set(i.get("target", "") for i in ideas if i.get("target"))))
    sel_target = st.sidebar.selectbox("ターゲット", target_options)
    
    module_options = ["すべて"] + sorted(list(set(i.get("modules", "") for i in ideas if i.get("modules"))))
    sel_module = st.sidebar.selectbox("モジュール", module_options)
    
    sort_options = {
        "推奨度：標準 (更新順)": "default",
        "推奨度：高い順": "desc",
        "推奨度：低い順": "asc"
    }
    sel_sort = st.sidebar.selectbox("並び替え", list(sort_options.keys()))
    
    st.sidebar.markdown("---")
    if st.sidebar.button("↻ データを再読み込み", use_container_width=True):
        st.rerun()

    # Filtering Logic
    filtered_ideas = ideas
    if sel_target != "すべて":
        filtered_ideas = [i for i in filtered_ideas if i.get("target") == sel_target]
    if sel_module != "すべて":
        filtered_ideas = [i for i in filtered_ideas if i.get("modules") == sel_module]
        
    sort_type = sort_options[sel_sort]
    if sort_type == "desc":
        filtered_ideas = sorted(filtered_ideas, key=lambda x: (x.get("recommendation_score", 0), x.get("updated_at", "")), reverse=True)
    elif sort_type == "asc":
        filtered_ideas = sorted(filtered_ideas, key=lambda x: (x.get("recommendation_score", 0), x.get("updated_at", "")))
    # default is already sorted by updated_at desc during load

    # Render Main Dashboard Header
    st.markdown("""
        <div class="dashboard-header" style="margin-bottom: 20px;">
            <div class="header-top">
                <div class="header-content">
                    <h1>SuccessFactors <span class="gradient-text">AI Evolution</span></h1>
                    <p>6種類の専門AIによる継続的なサービス改善プラン</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Render Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("稼働中のAI", "6名", "Active")
    col2.metric("総提案数", f"{len(ideas)}件")
    col3.metric("表示中", f"{len(filtered_ideas)}件")
    
    # Render AI Sequence Diagram / Events List (Horizontal)
    st.markdown("### <i class='fas fa-history' style='color:#ff6464;'></i> LIVE: AI検討履歴", unsafe_allow_html=True)
    
    if events:
        events_html = f"<div class='events-list-horizontal' id='events-list' style='margin-bottom: 20px;'>"
        for e in events[:5]: # show latest 5
            icon = "🤖"
            if "提出" in e['message']: icon = "💡"
            elif "レビュー" in e['message'] or "指摘" in e['message']: icon = "🔍"
            elif "破棄" in e['message'] or "整理" in e['message']: icon = "🗑️"
            
            time_str = e.get('timestamp', '')[11:19]
            events_html += f"""
            <div class='event-card-horiz {e.get('type','info')}'>
                <div class='event-icon-horiz'>{icon}</div>
                <div class='event-content-horiz'>
                    <span>{e['message']}</span>
                    <small>{time_str}</small>
                </div>
            </div>
            """
        events_html += "</div>"
        st.markdown(re.sub(r'\n\s*', '', events_html), unsafe_allow_html=True)
        
    # Render Ideas Grid
    st.markdown("---")
    if not filtered_ideas:
        st.warning("条件に一致するアイディアがありません。")
    else:
        grid_html = '<div class="ideas-grid">'
        for idea in filtered_ideas:
            grid_html += render_idea_card(idea)
        grid_html += "</div>"
        
        st.markdown(grid_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
