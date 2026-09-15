// Main UI Controller for Timer & Dashboard
let currentScramble = "";
let lastSolve = null;
let timerInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
    const timerDisplay = document.getElementById('timer-display');
    const scrambleEl = document.getElementById('scramble-text');
    const quickActionsEl = document.getElementById('quick-actions');
    const nextScrambleBtn = document.getElementById('btn-next-scramble');
    const copyScrambleBtn = document.getElementById('btn-copy-scramble');

    // Action buttons
    const btnPlusTwo = document.getElementById('btn-plus-two');
    const btnDnf = document.getElementById('btn-dnf');
    const btnDelete = document.getElementById('btn-delete');

    // 1. Initialize Stackmat Timer
    timerInstance = new StackmatTimer(timerDisplay, async (elapsedMs) => {
        // Callback on solve completion
        if (window.IS_GUEST) {
            // Guest mode: simply display the solved time and generate next scramble!
            await loadNewScramble();
            return;
        }

        try {
            lastSolve = await API.saveSolve(elapsedMs, currentScramble, 'none');
            showQuickActions(lastSolve);
            await refreshStatsAndRecents();
            await loadNewScramble();
        } catch (err) {
            console.error("Error saving solve:", err);
        }
    });

    // 2. Load Initial Scramble
    async function loadNewScramble() {
        try {
            const data = await API.fetchScramble();
            currentScramble = data.scramble;
            scrambleEl.textContent = currentScramble;
        } catch (err) {
            scrambleEl.textContent = "R U R' U' ... (Failed to fetch scramble)";
        }
    }

    await loadNewScramble();
    if (!window.IS_GUEST) {
        await refreshStatsAndRecents();
    }

    // 3. Button Events
    if (nextScrambleBtn) {
        nextScrambleBtn.addEventListener('click', () => loadNewScramble());
    }

    if (copyScrambleBtn) {
        copyScrambleBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(currentScramble);
            const orig = copyScrambleBtn.textContent;
            copyScrambleBtn.textContent = "Скопировано!";
            setTimeout(() => copyScrambleBtn.textContent = orig, 1500);
        });
    }

    // Quick Actions Handling (+2, DNF, Delete)
    function showQuickActions(solve) {
        quickActionsEl.classList.add('visible');
        updateActionButtonsState(solve.penalty);
    }

    function updateActionButtonsState(penalty) {
        btnPlusTwo.classList.toggle('active-penalty', penalty === '+2');
        btnDnf.classList.toggle('active-penalty', penalty === 'dnf');
    }

    btnPlusTwo.addEventListener('click', async () => {
        if (!lastSolve) return;
        const newPenalty = lastSolve.penalty === '+2' ? 'none' : '+2';
        lastSolve = await API.updatePenalty(lastSolve.id, newPenalty);
        updateActionButtonsState(lastSolve.penalty);
        timerDisplay.textContent = lastSolve.formatted_time;
        await refreshStatsAndRecents();
    });

    btnDnf.addEventListener('click', async () => {
        if (!lastSolve) return;
        const newPenalty = lastSolve.penalty === 'dnf' ? 'none' : 'dnf';
        lastSolve = await API.updatePenalty(lastSolve.id, newPenalty);
        updateActionButtonsState(lastSolve.penalty);
        timerDisplay.textContent = lastSolve.formatted_time;
        await refreshStatsAndRecents();
    });

    btnDelete.addEventListener('click', async () => {
        if (!lastSolve) return;
        if (confirm("Удалить последнюю сборку?")) {
            await API.deleteSolve(lastSolve.id);
            lastSolve = null;
            quickActionsEl.classList.remove('visible');
            timerDisplay.textContent = "0.00";
            await refreshStatsAndRecents();
        }
    });

    // Keyboard Shortcuts for quick actions after solve:
    // '2' -> toggle +2
    // 'd' -> toggle DNF
    // 'Backspace' / 'Delete' -> delete last solve
    window.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (timerInstance.state === 'running' || timerInstance.state === 'holding') return;

        if (lastSolve) {
            if (e.key === '2') {
                e.preventDefault();
                btnPlusTwo.click();
            } else if (e.key.toLowerCase() === 'd') {
                e.preventDefault();
                btnDnf.click();
            } else if (e.key === 'Backspace' || e.key === 'Delete') {
                e.preventDefault();
                btnDelete.click();
            }
        }
    });
});

async function refreshStatsAndRecents() {
    try {
        // Fetch stats
        const stats = await API.fetchStats();
        if (stats) {
            document.getElementById('stat-pb').textContent = stats.pb || "--";
            document.getElementById('stat-ao5').textContent = stats.ao5 || "--";
            document.getElementById('stat-ao12').textContent = stats.ao12 || "--";
            document.getElementById('stat-ao100').textContent = stats.ao100 || "--";
            document.getElementById('stat-total').textContent = stats.total_solves;
            if (document.getElementById('stat-best-ao5')) {
                document.getElementById('stat-best-ao5').textContent = `Best: ${stats.best_ao5 || '--'}`;
            }
            if (document.getElementById('stat-best-ao12')) {
                document.getElementById('stat-best-ao12').textContent = `Best: ${stats.best_ao12 || '--'}`;
            }
        }

        // Fetch recent 10 solves
        const solves = await API.fetchSolves(10, 0);
        const recentList = document.getElementById('recent-list');
        if (recentList) {
            recentList.innerHTML = "";
            if (solves.length === 0) {
                recentList.innerHTML = `<span style="color: var(--text-muted); font-size: 0.9rem;">Нет сборок. Зажмите пробел для старта!</span>`;
            } else {
                solves.forEach((s, idx) => {
                    const chip = document.createElement('div');
                    chip.className = 'recent-chip';
                    chip.innerHTML = `
                        <span class="chip-time">${s.formatted_time}</span>
                        <span class="chip-index">#${solves.length - idx}</span>
                    `;
                    recentList.appendChild(chip);
                });
            }
        }
    } catch (err) {
        console.error("Error refreshing stats:", err);
    }
}
