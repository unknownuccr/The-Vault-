'use strict';

document.addEventListener('DOMContentLoaded', () => {
    const CHARSETS = {
        lower: 'abcdefghijklmnopqrstuvwxyz',
        upper: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        digits: '0123456789',
        symbols: '!@#$%^&*()-_=+[]{};:,.<>?',
    };

    function randomPassword(length, sets) {
        const pool = sets.join('');
        const out = [];
        const rand = new Uint32Array(length);
        crypto.getRandomValues(rand);
        for (let i = 0; i < length; i++) {
            out.push(pool[rand[i] % pool.length]);
        }
        // Guarantee at least one character from each selected set.
        if (sets.length > 1 && length >= sets.length) {
            const positions = new Uint32Array(sets.length);
            crypto.getRandomValues(positions);
            sets.forEach((set, i) => {
                const idx = new Uint32Array(1);
                crypto.getRandomValues(idx);
                out[positions[i] % length] = set[idx[0] % set.length];
            });
        }
        return out.join('');
    }

    // Show/hide password inputs
    document.querySelectorAll('[data-toggle-password]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const input = document.getElementById(btn.dataset.togglePassword);
            if (!input) return;
            const show = input.type === 'password';
            input.type = show ? 'text' : 'password';
            btn.classList.toggle('is-on', show);
            btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
        });
    });

    // Strength meter (segmented)
    document.querySelectorAll('[data-strength-for]').forEach((meter) => {
        const input = document.getElementById(meter.dataset.strengthFor);
        const label = meter.querySelector('[data-strength-label]');
        if (!input) return;

        const update = () => {
            const value = input.value;
            let score = 0;
            if (value.length >= 8) score++;
            if (value.length >= 14) score++;
            if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score++;
            if (/\d/.test(value)) score++;
            if (/[^A-Za-z0-9]/.test(value)) score++;
            const level = value.length === 0 ? 0 : Math.max(1, Math.min(4, score - 1));
            meter.dataset.level = level;
            const names = ['', 'Weak', 'Fair', 'Good', 'Strong'];
            if (label) label.textContent = names[level];
        };
        input.addEventListener('input', update);
    });

    // Copy buttons (generator output and any element by id)
    function flashCopied(btn) {
        btn.classList.add('is-copied');
        setTimeout(() => btn.classList.remove('is-copied'), 1400);
    }

    document.querySelectorAll('[data-copy-target]').forEach((btn) => {
        btn.addEventListener('click', async () => {
            const el = document.getElementById(btn.dataset.copyTarget);
            if (!el) return;
            try {
                await navigator.clipboard.writeText(el.textContent.trim());
                flashCopied(btn);
            } catch (err) { /* clipboard unavailable */ }
        });
    });

    // Vault rows: reveal + copy the real secret
    document.querySelectorAll('[data-reveal]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const secret = btn.closest('.vault-row').querySelector('.vault-secret');
            if (!secret) return;
            const showing = btn.classList.toggle('is-on');
            secret.textContent = showing ? secret.dataset.secret : '••••••••••••';
            btn.setAttribute('aria-label', showing ? 'Hide password' : 'Show password');
        });
    });

    document.querySelectorAll('[data-copy-secret]').forEach((btn) => {
        btn.addEventListener('click', async () => {
            const secret = btn.closest('.vault-row').querySelector('.vault-secret');
            if (!secret) return;
            try {
                await navigator.clipboard.writeText(secret.dataset.secret);
                flashCopied(btn);
            } catch (err) { /* clipboard unavailable */ }
        });
    });

    // Vault filter
    const search = document.getElementById('vault-search');
    if (search) {
        const rows = Array.from(document.querySelectorAll('.vault-row'));
        const noMatch = document.getElementById('vault-no-match');
        search.addEventListener('input', () => {
            const q = search.value.trim().toLowerCase();
            let visible = 0;
            rows.forEach((row) => {
                const hit = !q || row.dataset.site.includes(q);
                row.style.display = hit ? '' : 'none';
                if (hit) visible++;
            });
            if (noMatch) noMatch.hidden = visible > 0;
        });
    }

    // Confirm before destructive form submits
    document.querySelectorAll('form[data-confirm]').forEach((form) => {
        form.addEventListener('submit', (e) => {
            if (!window.confirm(form.dataset.confirm)) e.preventDefault();
        });
    });

    // "Suggest strong password" on the new-entry form
    document.querySelectorAll('[data-suggest-password]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const input = document.getElementById(btn.dataset.suggestPassword);
            if (!input) return;
            input.value = randomPassword(20, Object.values(CHARSETS));
            input.type = 'text';
            const toggle = document.querySelector(`[data-toggle-password="${input.id}"]`);
            if (toggle) {
                toggle.classList.add('is-on');
                toggle.setAttribute('aria-label', 'Hide password');
            }
            input.dispatchEvent(new Event('input'));
        });
    });

    // Generator page
    const gen = document.querySelector('[data-generator]');
    if (gen) {
        const output = document.getElementById('gen-output');
        const lengthInput = document.getElementById('gen-length');
        const lengthValue = document.getElementById('gen-length-value');
        const entropyEl = gen.querySelector('[data-gen-entropy]');
        const checkboxes = Array.from(gen.querySelectorAll('[data-gen-set]'));

        const selectedSets = () =>
            checkboxes.filter((c) => c.checked).map((c) => CHARSETS[c.dataset.genSet]);

        const regenerate = () => {
            const sets = selectedSets();
            const length = parseInt(lengthInput.value, 10);
            lengthValue.textContent = length;
            if (sets.length === 0) {
                output.textContent = '';
                entropyEl.textContent = 'Select at least one character set.';
                return;
            }
            output.textContent = randomPassword(length, sets);
            const poolSize = sets.join('').length;
            const bits = Math.round(length * Math.log2(poolSize));
            entropyEl.textContent = `${poolSize}-character pool · roughly ${bits} bits of entropy`;
        };

        lengthInput.addEventListener('input', regenerate);
        checkboxes.forEach((c) => c.addEventListener('change', regenerate));
        gen.querySelector('[data-gen-refresh]').addEventListener('click', regenerate);
        regenerate();
    }
});
