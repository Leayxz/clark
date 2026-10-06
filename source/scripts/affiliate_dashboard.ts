/**
 * Clark — Affiliate Dashboard
 * Busca /api/v1/affiliates/dashboard e preenche os cards, o progresso de tier
 * e a tabela de pagamentos. O template carrega com placeholders e só mostra
 * os dados reais depois desta chamada.
 */

interface AffiliatePayment {
    date: string;
    coupon: string;
    amount_brl: number;
    commission_brl: number;
    status: string;
}

interface AffiliateDashboard {
    coupon_code: string;
    tier: string;
    tier_percentual: number;
    total_commissions_brl: number;
    paying_users: number;
    paying_users_threshold: number;
    next_tier: string;
    next_tier_percentual: number;
    remaining_to_next: number;
    payments: AffiliatePayment[];
}

// o backend devolve o status em ingles; a pagina rotula e colore por aqui
const STATUS_LABEL: Record<string, string> = {
    PENDING: "Pendente",
    PAID: "Confirmado",
    PROCESSED: "Pago",
    REFUNDED: "Reembolsado",
};

const STATUS_CLASS: Record<string, string> = {
    PENDING: "clark-status--pending",
    PAID: "clark-status--ok",
    PROCESSED: "clark-status--paid",
    REFUNDED: "clark-status--refund",
};

// o tier chega capitalizado do repository; a classe do css é em minusculo
const TIER_CLASS: Record<string, string> = {
    Bronze: "clark-tier-hero-tier--bronze",
    Prata: "clark-tier-hero-tier--prata",
    Ouro: "clark-tier-hero-tier--ouro",
};

function setText(id: string, value: string): void {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function formatBrl(value: number): string {
    return value.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function renderTier(dashboard: AffiliateDashboard): void {
    const hero = document.getElementById("tier_hero");
    if (!hero) return;

    hero.textContent = dashboard.tier;
    hero.className = `clark-tier-hero-tier ${TIER_CLASS[dashboard.tier] ?? ""}`.trim();

    setText("tier_hero_pct", `${dashboard.tier_percentual}%`);

    if (dashboard.next_tier === "—") {
        setText("tier_cta", "Você já está no tier mais alto");
        setText("tier_reward", `${dashboard.tier_percentual}%`);
        return;
    }

    setText("tier_cta", `Faltam ${dashboard.remaining_to_next} para o ${dashboard.next_tier}`);
    setText("tier_reward", `${dashboard.next_tier_percentual}%`);
}

function renderPayments(payments: AffiliatePayment[]): void {
    const body = document.getElementById("payments_body");
    if (!body) return;

    body.innerHTML = "";

    if (!payments.length) {
        body.innerHTML = '<tr><td colspan="5" class="clark-table-empty">Nenhum pagamento ainda.</td></tr>';
        return;
    }

    for (const payment of payments) {
        const row = document.createElement("tr");
        const statusClass = STATUS_CLASS[payment.status] ?? "clark-status--pending";
        const statusLabel = STATUS_LABEL[payment.status] ?? payment.status;

        row.innerHTML = `
            <td class="clark-table-date">${payment.date}</td>
            <td class="clark-table-mono">${payment.coupon}</td>
            <td>R$ ${formatBrl(payment.amount_brl)}</td>
            <td class="clark-table-up">+R$ ${formatBrl(payment.commission_brl)}</td>
            <td><span class="clark-status ${statusClass}">${statusLabel}</span></td>
        `;
        body.appendChild(row);
    }
}

async function loadDashboard(): Promise<void> {
    try {
        const response = await fetch("/api/v1/affiliates/dashboard", { method: "GET", credentials: "include" });

        if (response.status === 401) { window.location.href = "/login/"; return; }
        if (!response.ok) return;

        const dashboard: AffiliateDashboard = await response.json();

        setText("stat_commissions", formatBrl(dashboard.total_commissions_brl));
        setText("stat_tier", dashboard.tier);
        setText("stat_tier_pct", `/${dashboard.tier_percentual}%`);
        setText("stat_coupon", dashboard.coupon_code);
        setText("stat_paying", String(dashboard.paying_users));
        setText("stat_paying_threshold", dashboard.paying_users_threshold > 0 ? `/${dashboard.paying_users_threshold}` : "");
        setText("coupon_code", dashboard.coupon_code);

        renderTier(dashboard);
        renderPayments(dashboard.payments);
    } catch {
        // silencioso: a página já carrega com placeholders
    }
}

document.addEventListener("DOMContentLoaded", () => { loadDashboard(); });
