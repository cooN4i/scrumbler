// API Service for Scrumbler
const API = {
    async fetchScramble() {
        const res = await fetch('/api/solves/scramble');
        return await res.json();
    },

    async saveSolve(raw_time_ms, scramble, penalty = 'none') {
        const res = await fetch('/api/solves', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ raw_time_ms, scramble, penalty })
        });
        if (res.status === 401) {
            alert('Сессия истекла. Пожалуйста, войдите снова.');
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        if (!res.ok) throw new Error('Failed to save solve');
        return await res.json();
    },

    async updatePenalty(solveId, penalty) {
        const res = await fetch(`/api/solves/${solveId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ penalty })
        });
        if (!res.ok) throw new Error('Failed to update penalty');
        return await res.json();
    },

    async deleteSolve(solveId) {
        const res = await fetch(`/api/solves/${solveId}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error('Failed to delete solve');
        return true;
    },

    async fetchStats() {
        const res = await fetch('/api/solves/stats');
        if (!res.ok) return null;
        return await res.json();
    },

    async fetchSolves(limit = 20, offset = 0) {
        const res = await fetch(`/api/solves?limit=${limit}&offset=${offset}`);
        if (!res.ok) return [];
        return await res.json();
    },

    async getMe() {
        try {
            const res = await fetch('/api/auth/me');
            if (res.ok) return await res.json();
            return null;
        } catch {
            return null;
        }
    },

    async logout() {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    }
};
