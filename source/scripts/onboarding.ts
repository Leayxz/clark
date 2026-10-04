/* ============================================================
   CLARK — Onboarding (JS separado do template)
   Extraído de onboarding.html para seguir o padrão do projeto:
     - source/scripts/onboarding.ts  →  static/javascript/onboarding.js (tsc)
     - carregado via <script type="module" src="{% static 'javascript/onboarding.js' %}">
   Baseado nas notas:
     - [[MARKETING]] Seção 3.1: 5 telas, 1 CTA cada, sem menu
     - [[REGRAS MARKETING CLARK]] Seção 8: vende, não ensina
   Dark-first · terminal financeiro premium
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    const steps = document.querySelectorAll('.step') as NodeListOf<HTMLElement>;
    const fill = document.getElementById('progressFill')!;

    function show(n: number) {
        steps.forEach(s => s.classList.toggle('active', Number(s.dataset.step) === n));
        fill!.dataset.step = String(n);
        fill!.closest('.progress-bar')!.setAttribute('aria-valuenow', String(n));
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    document.querySelectorAll('[data-next]').forEach(btn => {
        btn.addEventListener('click', () => {
            if ((btn as HTMLElement).hasAttribute('disabled')) return;
            show(Number((btn as HTMLElement).dataset.next));
        });
    });

    document.querySelectorAll('[data-prev]').forEach(btn => {
        btn.addEventListener('click', () => show(Number((btn as HTMLElement).dataset.prev)));
    });

    // Sliders → atualizam label e tela de revisão
    function fmtPct(v: number): string { return v.toString().replace('.', ',') + '%'; }
    const buyVar = document.getElementById('buyVar') as HTMLInputElement;
    const profit = document.getElementById('profit') as HTMLInputElement;
    const exposure = document.getElementById('exposure') as HTMLInputElement;

    function sync(): void {
        const buyValue = parseFloat(buyVar.value);
        const profitValue = parseFloat(profit.value);
        const exposureValue = parseFloat(exposure.value);

        (document.getElementById('buyVarVal') as HTMLElement).textContent = fmtPct(buyValue);
        (document.getElementById('profitVal') as HTMLElement).textContent = fmtPct(profitValue);
        (document.getElementById('exposureVal') as HTMLElement).textContent = fmtPct(exposureValue);

        (document.getElementById('reviewExposure') as HTMLElement).textContent = fmtPct(exposureValue);
        (document.getElementById('reviewBuy') as HTMLElement).textContent = fmtPct(buyValue);
        (document.getElementById('reviewProfit') as HTMLElement).textContent = fmtPct(profitValue);

        // alocação simulada: 30% de R$ 1250
        const alloc = (exposureValue / 100) * 1250;
        (document.getElementById('reviewAllocated') as HTMLElement).textContent =
            'R$ ' + alloc.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
    }

    [buyVar, profit, exposure].forEach(el => el.addEventListener('input', sync));
    sync();

    // Checkbox habilita CTA final
    const ack = document.getElementById('riskAck') as HTMLInputElement;
    const enableBtn = document.getElementById('enableBtn') as HTMLButtonElement;
    function syncBtn(): void {
        enableBtn.disabled = !(ack.checked === true);
    }
    ack.addEventListener('click', syncBtn);
    ack.addEventListener('change', syncBtn);
    syncBtn();
});
