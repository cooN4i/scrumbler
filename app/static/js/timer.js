// Stackmat WCA Timer Engine
class StackmatTimer {
    constructor(displayElement, onSolveFinish) {
        this.display = displayElement;
        this.onSolveFinish = onSolveFinish;

        // States: 'idle', 'holding', 'ready', 'running', 'stopped'
        this.state = 'idle';

        this.holdStartTime = 0;
        this.holdTimer = null;
        this.HOLD_REQUIRED_MS = 350; // WCA-style readiness hold time

        this.startTime = 0;
        this.elapsedMs = 0;
        this.animationFrameId = null;

        this.spacePressed = false;
        this.enabled = true;

        this.initEvents();
    }

    initEvents() {
        window.addEventListener('keydown', (e) => this.handleKeyDown(e));
        window.addEventListener('keyup', (e) => this.handleKeyUp(e));

        // Touch support for mobile / tablets
        this.display.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.handleKeyDown({ code: 'Space', preventDefault: () => {} });
        });
        this.display.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.handleKeyUp({ code: 'Space', preventDefault: () => {} });
        });
    }

    setEnabled(enabled) {
        this.enabled = enabled;
    }

    handleKeyDown(e) {
        if (!this.enabled) return;

        // Ignore typing in input fields
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        // If timer is currently running, pressing ANY key stops it immediately!
        if (this.state === 'running') {
            e.preventDefault();
            this.stopTimer();
            return;
        }

        // Only Space triggers the holding/ready states
        if (e.code === 'Space' && !this.spacePressed) {
            e.preventDefault();
            this.spacePressed = true;

            if (this.state === 'idle' || this.state === 'stopped') {
                this.startHolding();
            }
        }
    }

    handleKeyUp(e) {
        if (!this.enabled) return;
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.code === 'Space') {
            this.spacePressed = false;

            if (this.state === 'holding') {
                // Released too early before turning green!
                this.cancelHolding();
            } else if (this.state === 'ready') {
                // Released when green -> Start solving!
                this.startRunning();
            }
        }
    }

    startHolding() {
        this.state = 'holding';
        this.display.classList.remove('state-ready', 'state-running');
        this.display.classList.add('state-holding');

        this.holdStartTime = performance.now();

        // After HOLD_REQUIRED_MS turns to 'ready' (green)
        this.holdTimer = setTimeout(() => {
            if (this.state === 'holding' && this.spacePressed) {
                this.state = 'ready';
                this.display.classList.remove('state-holding');
                this.display.classList.add('state-ready');
            }
        }, this.HOLD_REQUIRED_MS);
    }

    cancelHolding() {
        clearTimeout(this.holdTimer);
        this.state = 'idle';
        this.display.classList.remove('state-holding', 'state-ready');
    }

    startRunning() {
        clearTimeout(this.holdTimer);
        this.state = 'running';
        this.display.classList.remove('state-holding', 'state-ready');
        this.display.classList.add('state-running');

        this.startTime = performance.now();
        this.updateLoop();
    }

    updateLoop() {
        if (this.state !== 'running') return;

        const now = performance.now();
        this.elapsedMs = Math.floor(now - this.startTime);
        this.display.textContent = this.formatDisplay(this.elapsedMs);

        this.animationFrameId = requestAnimationFrame(() => this.updateLoop());
    }

    stopTimer() {
        cancelAnimationFrame(this.animationFrameId);
        const now = performance.now();
        this.elapsedMs = Math.floor(now - this.startTime);

        this.state = 'stopped';
        this.display.classList.remove('state-running', 'state-holding', 'state-ready');
        this.display.textContent = this.formatDisplay(this.elapsedMs);

        if (this.onSolveFinish) {
            this.onSolveFinish(this.elapsedMs);
        }
    }

    reset() {
        cancelAnimationFrame(this.animationFrameId);
        clearTimeout(this.holdTimer);
        this.state = 'idle';
        this.display.classList.remove('state-running', 'state-holding', 'state-ready');
        this.display.textContent = "0.00";
    }

    formatDisplay(ms) {
        const totalSeconds = ms / 1000;
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = (totalSeconds % 60).toFixed(2);

        if (minutes > 0) {
            const secStr = (totalSeconds % 60) < 10 ? `0${seconds}` : seconds;
            return `${minutes}:${secStr}`;
        }
        return seconds;
    }
}
