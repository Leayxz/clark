interface SidebarStatusProtocol {
    last_operation: string;
    status_automation: boolean;
    status_telegram: boolean;
    leverage: number;
    percentage_profit: number;
}


// o seletor de exchange so existe na pagina de automação; nas demais assume lnmarkets
function getActiveExchange(): string {
    const active = document.querySelector(".clark-exchange-card--active") as HTMLElement | null;
    return active?.dataset.exchange || "lnmarkets";
}


export async function refreshSidebar(): Promise<void> {
    try {
        const response = await fetch(`/api/v1/sidebar?exchange=${getActiveExchange()}`, { method: "GET", credentials: "include" });
        if (response.status === 401) { window.location.href = "/"; return; }
        if (!response.ok) { return; }

        const data: SidebarStatusProtocol = await response.json();

        // Last operation
        const lastOpEl = document.getElementById("last_operation");
        if (lastOpEl) { lastOpEl.textContent = data.last_operation; }

        // Strategy
        const strategyEl = document.getElementById("estrategia_sidebar");
        if (strategyEl) { strategyEl.textContent = `Target ${data.percentage_profit}% | Leverage ${data.leverage}x`; }

        // Telegram status
        const telegramEl = document.getElementById("status_telegram");
        if (telegramEl) {
            telegramEl.textContent = data.status_telegram ? "Conectado" : "Desconectado";
        }

        // Automation status (dot + label)
        const dotEl = document.getElementById("status-dot");
        const textEl = document.getElementById("automation-text");
        const statusEl = document.querySelector(".clark-automation-status") as HTMLElement;
        const labelEl = document.querySelector(".clark-automation-label") as HTMLElement;
        if (data.status_automation) {
            dotEl?.classList.remove("inactive");
            dotEl?.classList.add("active");
            statusEl?.classList.remove("inactive");
            labelEl?.classList.remove("inactive");
            if (textEl) { textEl.textContent = "Executando"; }
        } else {
            dotEl?.classList.remove("active");
            dotEl?.classList.add("inactive");
            statusEl?.classList.add("inactive");
            labelEl?.classList.add("inactive");
            if (textEl) { textEl.textContent = "Inativo"; }
        }

    } catch {
        // silencioso: sidebar não deve bloquear navegação
    }
}


class LogOut {
    constructor() { this.start_listener(); }
    start_listener() {
        document.getElementById("button_logout")?.addEventListener("click", async () => { this.logout_user(); });
    }
    async logout_user() {
        const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;
        await fetch("/api/v1/logout", {method: "POST", credentials: "include", headers: {"content-type": "application/json", "x-csrftoken": csrf.value}});
        window.location.href = "/";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    refreshSidebar();
    new LogOut();
});
