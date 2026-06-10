// Vanilla JS reactive state and polling logic for A2UI Express dashboard

document.addEventListener("DOMContentLoaded", () => {
    // 1. Navigation Tab Switching
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            tabButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-target");
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add("active");
            }
        });
    });

    // 2. Data Fetching & DOM Updating
    async function fetchDashboardState() {
        try {
            // Fetch Leaderboard State
            const boardResp = await fetch("/api/leaderboard");
            if (boardResp.ok) {
                const board = await boardResp.json();
                const champId = board.reigning_champion || "gene_v1_0";
                document.getElementById("champId").textContent = champId;
                document.getElementById("reigningBadge").textContent = champId;

                const champMeta = (board.history && board.history[champId]) || {};
                document.getElementById("champHash").textContent = champMeta.content_hash || "9ba12f7b201c";

                const metrics = champMeta.metrics || {
                    output_compression: 0.65,
                    prompt_footprint_tokens: 385
                };

                // Update Output Compression
                const comp = metrics.output_compression || 0;
                document.getElementById("compScore").textContent = comp.toFixed(4);
                const compPct = (comp * 100).toFixed(1);
                document.getElementById("compPctText").textContent = `${compPct}%`;
                document.getElementById("compProgressBar").style.width = `${Math.min(100, Math.max(0, compPct))}%`;

                // Update Prompt Compactness
                const promptTokens = metrics.prompt_footprint_tokens || 385;
                document.getElementById("promptScore").innerHTML = `${promptTokens} <span style="font-size: 1rem; font-weight: 400; color: var(--text-muted);">/ 1000 max</span>`;
                const promptPct = Math.max(0, 100 - (promptTokens / 10)).toFixed(1);
                document.getElementById("promptPctText").textContent = `${promptPct}%`;
                document.getElementById("promptProgressBar").style.width = `${Math.min(100, Math.max(0, promptPct))}%`;

                // Render Lineage Graph
                renderLineageTree(board);
            }

            // Fetch Active Workers & Trajectories
            const agentsResp = await fetch("/api/agents");
            if (agentsResp.ok) {
                const agentsData = await agentsResp.json();
                renderActiveAgents(agentsData.agents || []);
                renderTerminalLogs(agentsData.recent_logs || []);
                document.getElementById("activeAgentsCount").textContent = (agentsData.agents || []).length;
            }

            // Fetch MLX Server State
            const stateResp = await fetch("/api/system_state");
            if (stateResp.ok) {
                const state = await stateResp.json();
                const dot = document.getElementById("statusDot");
                const txt = document.getElementById("statusText");
                if (state.mlx_online) {
                    dot.className = "status-dot online";
                    txt.textContent = "MLX Server: Online (8080)";
                } else {
                    dot.className = "status-dot";
                    txt.textContent = "MLX Server: Offline";
                }
            }

        } catch (err) {
            console.error("Dashboard polling error:", err);
        }
    }

    // Render Active Worker Panels
    function renderActiveAgents(agents) {
        const grid = document.getElementById("agentsGrid");
        if (!grid) return;

        if (agents.length === 0) {
            grid.innerHTML = `<div class="glass-panel agent-card" style="color: var(--text-muted);">No active background worker agent sessions discovered in Jetski brain directory.</div>`;
            return;
        }

        grid.innerHTML = agents.map(ag => `
            <div class="glass-panel agent-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="agent-id">${ag.conversation_id || "worker"}</span>
                    <span class="agent-status-badge ${ag.status === 'DONE' ? 'success' : 'running'}">${ag.status || 'RUNNING'}</span>
                </div>
                <div style="font-size: 0.9rem; color: var(--text-main); font-weight: 500;">
                    Targeting Gate: <span style="color: var(--accent-cyan);">${ag.current_gate || 'Tier 0/1 Unit Tests'}</span>
                </div>
                <div class="agent-thoughts">${escapeHtml(ag.thinking || 'Awaiting reasoning transcript...')}</div>
            </div>
        `).join("");
    }

    // Render Lineage Graph
    function renderLineageTree(board) {
        const container = document.getElementById("lineageTree");
        if (!container) return;

        const history = board.history || {};
        const keys = Object.keys(history);

        if (keys.length === 0) {
            container.innerHTML = `<div style="color: var(--text-muted);">Lineage tree empty. Baseline champion reigning unseated.</div>`;
            return;
        }

        container.innerHTML = `
            <div style="font-weight: 600; color: var(--accent-cyan); margin-bottom: 12px;">Evolutionary Divergence Lineage</div>
            <div style="display: flex; flex-direction: column; gap: 12px; font-family: var(--font-mono); font-size: 0.9rem;">
                ${keys.map(k => `
                    <div style="display: flex; align-items: center; gap: 16px; background: hsl(0, 0%, 0% / 0.4); padding: 14px 20px; border-radius: 10px; border: 1px solid var(--border-color);">
                        <span style="color: var(--accent-amber); font-weight: 700;">${k}</span>
                        <span style="color: var(--text-muted);">← parent:</span>
                        <span style="color: var(--text-main);">${history[k].parent || 'baseline'}</span>
                        <span style="margin-left: auto; color: var(--accent-emerald); font-weight: 600;">Score: ${history[k].fitness_score || '0.85'}</span>
                    </div>
                `).join("")}
            </div>
        `;
    }

    // Append Terminal Logs
    function renderTerminalLogs(logs) {
        const term = document.getElementById("terminalLogs");
        if (!term || logs.length === 0) return;

        term.innerHTML = logs.map(lg => `
            <div class="log-line">
                <span class="log-time">[${lg.created_at || 'now'}]</span>
                <span class="log-source">${lg.source || 'MODEL'}</span>
                <span class="log-msg ${lg.status === 'ERROR' ? 'error' : ''}">${escapeHtml(lg.content || lg.thinking || '')}</span>
            </div>
        `).join("");
        term.scrollTop = term.scrollHeight;
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    // Initial Fetch & Start Interval
    fetchDashboardState();
    setInterval(fetchDashboardState, 2000);
});
