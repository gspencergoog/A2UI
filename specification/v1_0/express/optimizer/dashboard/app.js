// Vanilla JS SSE streaming client and selective DOM reconciliation (Scroll lock)

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

    // 2. Establish Persistent SSE Stream Connection
    let renderedLogKeys = new Set();
    const evtSource = new EventSource("/api/stream");

    evtSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            // A. Update Leaderboard Metrics Selectively
            const board = data.leaderboard || {};
            const champId = board.reigning_champion || "gene_v1_0";
            document.getElementById("champId").textContent = champId;
            document.getElementById("reigningBadge").textContent = champId;

            const champMeta = (board.history && board.history[champId]) || {};
            document.getElementById("champHash").textContent = champMeta.content_hash || "9ba12f7b201c";

            const metrics = champMeta.metrics || { output_compression: 0.65, prompt_footprint_tokens: 385 };

            const comp = metrics.output_compression || 0;
            document.getElementById("compScore").textContent = comp.toFixed(4);
            const compPct = (comp * 100).toFixed(1);
            document.getElementById("compPctText").textContent = `${compPct}%`;
            document.getElementById("compProgressBar").style.width = `${Math.min(100, Math.max(0, compPct))}%`;

            const promptTokens = metrics.prompt_footprint_tokens || 385;
            document.getElementById("promptScore").innerHTML = `${promptTokens} <span style="font-size: 1rem; font-weight: 400; color: var(--text-muted);">/ 1000 max</span>`;
            const promptPct = Math.max(0, 100 - (promptTokens / 10)).toFixed(1);
            document.getElementById("promptPctText").textContent = `${promptPct}%`;
            document.getElementById("promptProgressBar").style.width = `${Math.min(100, Math.max(0, promptPct))}%`;

            renderLineageTree(board);

            // B. Reconcile Active Workers (Preserving Scroll Position)
            const agentsData = data.agents_data || {};
            updateActiveAgentsGrid(agentsData.agents || []);
            document.getElementById("activeAgentsCount").textContent = (agentsData.agents || []).length;

            // C. Append Terminal Logs Selectively
            appendTerminalLogs(agentsData.recent_logs || []);

            // D. Update MLX Server Badge
            const sysState = data.system_state || {};
            const dot = document.getElementById("statusDot");
            const txt = document.getElementById("statusText");
            if (sysState.mlx_online) {
                dot.className = "status-dot online";
                txt.textContent = "MLX Server: Online (8080)";
            } else {
                dot.className = "status-dot";
                txt.textContent = "MLX Server: Offline";
            }

        } catch (err) {
            console.error("SSE Packet parsing error:", err);
        }
    };

    evtSource.onerror = () => {
        console.warn("SSE Stream disconnected. Attempting automatic reconnection...");
    };

    // Reconcile Active Workers (Selective DOM Node Updates)
    function updateActiveAgentsGrid(agents) {
        const grid = document.getElementById("agentsGrid");
        if (!grid) return;

        if (agents.length === 0) {
            grid.innerHTML = `<div class="glass-panel agent-card" style="color: var(--text-muted);">No active background worker agent sessions discovered in Jetski brain directory.</div>`;
            return;
        }

        // Remove stale cards
        const activeIds = new Set(agents.map(ag => `agent-card-${ag.conversation_id}`));
        Array.from(grid.children).forEach(child => {
            if (child.id && child.id.startsWith("agent-card-") && !activeIds.has(child.id)) {
                grid.removeChild(child);
            }
        });

        // Update or append cards selectively
        agents.forEach(ag => {
            const cardId = `agent-card-${ag.conversation_id}`;
            let card = document.getElementById(cardId);

            if (!card) {
                // Construct new card container
                card = document.createElement("div");
                card.id = cardId;
                card.className = "glass-panel agent-card";
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="agent-id">${ag.conversation_id || "worker"}</span>
                        <span class="agent-status-badge"></span>
                    </div>
                    <div style="font-size: 0.9rem; color: var(--text-main); font-weight: 500;">
                        Targeting Gate: <span class="current-gate" style="color: var(--accent-cyan);"></span>
                    </div>
                    <div class="agent-thoughts"></div>
                `;
                grid.appendChild(card);
            }

            // Selectively update text spans
            const badge = card.querySelector(".agent-status-badge");
            const statusText = ag.status || "RUNNING";
            if (badge.textContent !== statusText) {
                badge.textContent = statusText;
                badge.className = `agent-status-badge ${statusText === "DONE" ? "success" : "running"}`;
            }

            const gateSpan = card.querySelector(".current-gate");
            const gateText = ag.current_gate || "Tier 0/1 Unit Tests";
            if (gateSpan.textContent !== gateText) {
                gateSpan.textContent = gateText;
            }

            // Update multiline thoughts box with scroll lock
            const box = card.querySelector(".agent-thoughts");
            const newThoughts = ag.thinking || "Awaiting reasoning transcript...";
            if (box.textContent !== newThoughts) {
                const isAtBottom = Math.abs((box.scrollHeight - box.scrollTop) - box.clientHeight) < 15;
                box.textContent = newThoughts;
                if (isAtBottom) {
                    box.scrollTop = box.scrollHeight;
                }
            }
        });
    }

    // Append Terminal Logs Selectively
    function appendTerminalLogs(logs) {
        const term = document.getElementById("terminalLogs");
        if (!term || logs.length === 0) return;

        let appended = false;
        const isAtBottom = Math.abs((term.scrollHeight - term.scrollTop) - term.clientHeight) < 20;

        logs.forEach(lg => {
            const key = `${lg.created_at}-${(lg.content || "").slice(0, 20)}`;
            if (!renderedLogKeys.has(key)) {
                renderedLogKeys.add(key);
                const div = document.createElement("div");
                div.className = "log-line";
                div.innerHTML = `
                    <span class="log-time">[${lg.created_at || "now"}]</span>
                    <span class="log-source">${lg.source || "MODEL"}</span>
                    <span class="log-msg ${lg.status === "ERROR" ? "error" : ""}">${escapeHtml(lg.content || lg.thinking || "")}</span>
                `;
                term.appendChild(div);
                appended = true;
            }
        });

        // Cap max DOM entries in terminal view
        while (term.children.length > 200) {
            term.removeChild(term.firstChild);
        }

        if (appended && isAtBottom) {
            term.scrollTop = term.scrollHeight;
        }
    }

    function renderLineageTree(board) {
        const container = document.getElementById("lineageTree");
        if (!container) return;

        const history = board.history || {};
        const keys = Object.keys(history);

        if (keys.length === 0) return;

        container.innerHTML = `
            <div style="font-weight: 600; color: var(--accent-cyan); margin-bottom: 12px;">Evolutionary Divergence Lineage</div>
            <div style="display: flex; flex-direction: column; gap: 12px; font-family: var(--font-mono); font-size: 0.9rem;">
                ${keys.map(k => `
                    <div style="display: flex; align-items: center; gap: 16px; background: hsl(0, 0%, 0% / 0.4); padding: 14px 20px; border-radius: 10px; border: 1px solid var(--border-color);">
                        <span style="color: var(--accent-amber); font-weight: 700;">${k}</span>
                        <span style="color: var(--text-muted);">← parent:</span>
                        <span style="color: var(--text-main);">${history[k].parent || "baseline"}</span>
                        <span style="margin-left: auto; color: var(--accent-emerald); font-weight: 600;">Score: ${history[k].fitness_score || "0.85"}</span>
                    </div>
                `).join("")}
            </div>
        `;
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
});
