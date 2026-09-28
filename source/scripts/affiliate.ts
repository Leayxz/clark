/**
 * Clark — Affiliate Page Interactions v2 (2026-09-11)
 * Features: loading state, char counter, focus trap, error feedback
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formulario_afiliados') as HTMLFormElement;
    const erroDiv = document.getElementById('erro-afiliado') as HTMLDivElement;
    const erroText = document.getElementById('erro-afiliado-text') as HTMLSpanElement;

    let erroTimer: number | null = null;

    function showError(msg: string): void {
        if (erroTimer) clearTimeout(erroTimer);
        erroText.textContent = msg;
        erroDiv.hidden = false;
        erroTimer = window.setTimeout(() => { erroDiv.hidden = true; }, 5000);
    }

    function showBackendError(msg: string): void {
        const backendErrorDiv = document.getElementById('backend-error') as HTMLDivElement;
        const backendErrorText = document.getElementById('backend-error-text') as HTMLSpanElement;
        if (!backendErrorDiv || !backendErrorText) return;
        backendErrorText.textContent = msg;
        backendErrorDiv.hidden = false;
        backendErrorDiv.classList.add('visible');
    }

    // ── Modal ──────────────────────────────────────────────
    const modalOverlay = document.getElementById('clark-modal-overlay') as HTMLDivElement;
    const modalFecharBtn = document.getElementById('modal-sucesso-fechar') as HTMLButtonElement;

    function trapFocus(modal: HTMLElement): () => void {
        const focusable = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ) as NodeListOf<HTMLElement>;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const handleKeydown = (e: KeyboardEvent) => {
            if (e.key !== 'Tab') return;
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault(); last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault(); first.focus();
            }
        };
        modal.addEventListener('keydown', handleKeydown);
        return () => modal.removeEventListener('keydown', handleKeydown);
    }

    let releaseTrap: (() => void) | null = null;

    function openModal(): void {
        modalOverlay.hidden = false;
        document.body.style.overflow = 'hidden';
        modalFecharBtn.focus();
        releaseTrap = trapFocus(modalOverlay.querySelector('.clark-modal') as HTMLElement);
    }

    function closeModal(): void {
        modalOverlay.hidden = true;
        document.body.style.overflow = '';
        releaseTrap?.();
        releaseTrap = null;
    }

    modalFecharBtn.addEventListener('click', closeModal);

    modalOverlay.addEventListener('click', (e: MouseEvent) => {
        if (e.target === modalOverlay) closeModal();
    });

    document.addEventListener('keydown', (e: KeyboardEvent) => {
        if (e.key === 'Escape' && !modalOverlay.hidden) closeModal();
    });

    // ── Validate & Redirect ────────────────────────
    const openPanelBtn = document.getElementById('open-panel-btn') as HTMLAnchorElement;
    const affiliateError = document.getElementById('affiliate-error') as HTMLDivElement;

    function showAffiliateError(msg: string): void {
        if (!affiliateError) return;
        const errorText = affiliateError.querySelector('.clark-error-text') as HTMLSpanElement;
        if (errorText) errorText.textContent = msg;
        affiliateError.hidden = false;
        affiliateError.classList.add('visible');
        window.setTimeout(() => { affiliateError.hidden = true; affiliateError.classList.remove('visible'); }, 5000);
    }


    openPanelBtn?.addEventListener('click', async (event) => {
        event.preventDefault();

        try {
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement | null;

            const result = await fetch('/api/v1/affiliates/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf?.value || '',
                },
                credentials: 'same-origin',
            });

            if (result.ok) {
                window.location.href = '/affiliate/dashboard/';
                return;
            }

            showAffiliateError(
                'Você ainda não está registrado como parceiro. Faça o seu cadastro abaixo.'
            );

        } catch {
            showAffiliateError('Erro de conexão. Tente novamente.');
        }
    });


    // ── Char Counter ───────────────────────────────────────
    const descricaoInput = document.getElementById('afiliado_descricao') as HTMLTextAreaElement;
    const charCounter = document.getElementById('char-counter-count') as HTMLElement;
    const charCounterWrapper = charCounter?.closest('.clark-char-counter') as HTMLElement;
    const MAX_DESC_CHARS = 300;

    function updateCharCounter(): void {
        if (!descricaoInput || !charCounter) return;
        const length = descricaoInput.value.length;
        charCounter.textContent = String(length);
        if (length >= 10) {
            charCounterWrapper.classList.remove('clark-char-counter--invalid');
            charCounterWrapper.classList.add('clark-char-counter--valid');
        } else {
            charCounterWrapper.classList.remove('clark-char-counter--valid');
            charCounterWrapper.classList.add('clark-char-counter--invalid');
        }
    }

    descricaoInput?.addEventListener('input', updateCharCounter);

    // ── Form Submit ─────────────────────────────────────────
    const submitBtn = document.getElementById('btn-submit') as HTMLButtonElement;
    const btnSpinner = submitBtn?.querySelector('.clark-btn-spinner') as HTMLElement;

    function setLoading(isLoading: boolean): void {
        if (!submitBtn) return;
        if (isLoading) {
            submitBtn.classList.add('clark-btn-primary--loading');
            submitBtn.disabled = true;
            btnSpinner.style.display = 'block';
        } else {
            submitBtn.classList.remove('clark-btn-primary--loading');
            submitBtn.disabled = false;
            btnSpinner.style.display = 'none';
        }
    }

    form?.addEventListener('submit', async (event) => {
        event.preventDefault();

        const liquidInput = document.getElementById('afiliado_liquid') as HTMLInputElement;
        const cupomInput = document.getElementById('afiliado_cupom') as HTMLInputElement;
        const descricaoInputEl = document.getElementById('afiliado_descricao') as HTMLTextAreaElement;
        const termosInput = document.getElementById('afiliado_termos') as HTMLInputElement;

        const liquid = liquidInput.value.trim();
        const cupom = cupomInput.value.trim();
        const promotionDescription = descricaoInputEl.value.trim();
        const termos = termosInput.checked;

        if (!liquid || !cupom || !promotionDescription) {
            showError('Todos os campos são obrigatórios.');
            return;
        }

        if (!liquid.toLowerCase().startsWith('lq1')) {
            showError('O endereço deve começar com lq1 (Liquid Network).');
            liquidInput.focus();
            return;
        }
        if (liquid.replace('liquid:', '').length < 20) {
            showError('Endereço Liquid inválido.');
            liquidInput.focus();
            return;
        }
        if (cupom.length < 3) {
            showError('O cupom deve ter pelo menos 3 caracteres.');
            cupomInput.focus();
            return;
        }
        if (promotionDescription.length < 10) {
            showError('A descrição deve ter pelo menos 10 caracteres.');
            descricaoInputEl.focus();
            return;
        }
        if (!termos) {
            showError('Você precisa aceitar os termos.');
            termosInput.focus();
            return;
        }

        const csrf = document.querySelector('[name=csrfmiddlewaretoken]') as HTMLInputElement;
        const PAYLOAD = {
            liquid_address: liquid,
            coupon: cupom.toUpperCase().replace(/\s/g, ''),
            promotion_description: promotionDescription
        };

        setLoading(true);
        const backendErrorDiv = document.getElementById('backend-error') as HTMLDivElement;
        if (backendErrorDiv) { backendErrorDiv.hidden = true; backendErrorDiv.classList.remove('visible'); }

        try {
            const result = await fetch('/api/v1/affiliates/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf.value
                },
                body: JSON.stringify(PAYLOAD)
            });

            if (!result.ok) {
                const data = await result.json();
                showBackendError(data.error || 'Erro ao registrar candidatura.');
                return;
            }

            openModal();
            form.reset();
            updateCharCounter();
        } catch {
            showBackendError('Erro de conexão. Tente novamente.');
        } finally {
            setLoading(false);
        }
    });

    // Initialize
    setLoading(false);
    updateCharCounter();
});
