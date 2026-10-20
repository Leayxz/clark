interface ConfiguracaoData {
    exchange: string
    API_KEY: string
    API_SECRET: string
    API_PASSPHRASE: string
    status_automation: boolean
    marginUSD: number
    leverage: number
    percentage_profit: number
    buy_variation: number
}


// buscando todos os dados para popular o html da automação - Configuração Automação, API, Automação Ativa
document.addEventListener("DOMContentLoaded", async () => {
    await loadExchangeData();
});


function getActiveExchange(): string {
    const active = document.querySelector(".clark-exchange-card--active");
    if (active) {
        return (active as HTMLElement).dataset.exchange || "lnmarkets";
    }
    return "lnmarkets";
}


function setActiveExchange(exchange: string): void {
    document.querySelectorAll(".clark-exchange-card").forEach((btn) => {
        const card = btn as HTMLElement;
        const isActive = card.dataset.exchange === exchange;
        card.classList.toggle("clark-exchange-card--active", isActive);
        card.setAttribute("aria-checked", String(isActive));
        card.setAttribute("role", "radio");
    });
}

function getExchangeLabel(exchange: string): string {
    return exchange === "lnmarkets" ? "LNMarkets" : "Hyperliquid";
}


// Busca dados do backend para a exchange selecionada e popula os formulários
async function loadExchangeData(): Promise<void> {
    const exchange = getActiveExchange();
    const response = await fetch(`/api/v1/automation/dashboard?exchange=${exchange}`, {method: "GET", credentials: "include"});

    if (!response.ok) {
        (document.getElementById("dot_animation") as HTMLElement)!.classList.remove("active");
        (document.getElementById("dot_animation") as HTMLElement)!.classList.add("inactive");
        (document.getElementById("status_label") as HTMLParagraphElement)!.textContent = "Erro interno no servidor.";
        (document.getElementById("sub_status_automation") as HTMLParagraphElement)!.textContent = "Aguarde alguns minutos e tente novamente.";
        return;
    }

    const data: ConfiguracaoData = await response.json();

    (document.getElementById("api_key") as HTMLInputElement).value = data.API_KEY || "";
    (document.getElementById("api_secret") as HTMLInputElement).value = data.API_SECRET || "";
    (document.getElementById("api_passphrase") as HTMLInputElement).value = data.API_PASSPHRASE || "";

    // a api so esta conectada quando as duas chaves obrigatorias existem
    const api_status = document.getElementById("api-status") as HTMLDivElement;
    const api_status_text = document.getElementById("api-status-text") as HTMLSpanElement;
    const api_connected = Boolean(data.API_KEY && data.API_SECRET);

    api_status.classList.toggle("disconnected", !api_connected);
    api_status_text.textContent = api_connected
        ? "Api conectada — exchange ok"
        : "Api Desconectada — Configure Suas Chaves";

    const status_label = document.getElementById("status_label") as HTMLParagraphElement;
    const sub_status_automation = document.getElementById("sub_status_automation") as HTMLParagraphElement;
    const botao_ligar_automacao = document.getElementById("enable_automation") as HTMLButtonElement;
    const dot_animation = document.getElementById("dot_animation") as HTMLElement;

    if (data.status_automation) {
        dot_animation?.classList.add("active");
        dot_animation?.classList.remove("inactive");
        botao_ligar_automacao.classList.add("active");
        status_label.textContent = "Automação Ativa";
        sub_status_automation.textContent = "Em execução...";
        botao_ligar_automacao.textContent = "Desativar Automação";
    } else {
        dot_animation?.classList.remove("active");
        dot_animation?.classList.add("inactive");
        botao_ligar_automacao.classList.remove("active");
        status_label.textContent = "Automação Inativa";
        sub_status_automation.textContent = "Execução Parada!";
        botao_ligar_automacao.textContent = "Ativar Automação";
    }

    botao_ligar_automacao.dataset.enabled = String(data.status_automation);

    (document.getElementById("marginUSD") as HTMLInputElement).value = String(data.marginUSD);
    (document.getElementById("leverage") as HTMLInputElement).value = String(data.leverage);
    (document.getElementById("percentage_profit") as HTMLInputElement).value = String(data.percentage_profit);
    (document.getElementById("buy_variation") as HTMLInputElement).value = String(data.buy_variation);

    (document.getElementById("buy_variation_preview") as HTMLSpanElement).textContent = String(data.buy_variation);
    (document.getElementById("percentage_profit_preview") as HTMLSpanElement).textContent = String(data.percentage_profit);
    (document.getElementById("marginUSD_preview") as HTMLSpanElement).textContent = String(data.marginUSD);
    (document.getElementById("leverage_preview") as HTMLSpanElement).textContent = String(data.leverage);
}


// Botões de troca de exchange
document.querySelectorAll(".clark-exchange-card").forEach((btn) => {
    btn.addEventListener("click", async () => {
        const card = btn as HTMLElement;
        const exchange = card.dataset.exchange!;
        setActiveExchange(exchange);
        await loadExchangeData();
    });
});


// botão para salvar novas configurações
document.getElementById("configuration_form")?.addEventListener("submit", async (event) => { event.preventDefault();

    const exchange = getActiveExchange();
    const exchange_label = getExchangeLabel(exchange);
    const message = document.getElementById("configuration_message") as HTMLParagraphElement;

    const body = {
        exchange: exchange,
        marginUSD: (document.getElementById("marginUSD") as HTMLInputElement).value,
        leverage: (document.getElementById("leverage") as HTMLInputElement).value,
        buy_variation: (document.getElementById("buy_variation") as HTMLInputElement).value,
        percentage_profit: (document.getElementById("percentage_profit") as HTMLInputElement).value,
    }

    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;

    // Warning: salvando
    message.hidden = true;
    message.textContent = `Salvando configuração para ${exchange_label}...`;
    message.className = "temporary_message warning";
    message.hidden = false;

    const response = await fetch("/api/v1/automation/configuration", {method: "POST", credentials: "include", headers: {"Content-Type": "application/json", "x-csrftoken": csrf.value}, body: JSON.stringify(body)});

    if (!response.ok) {
        message.textContent = `Erro ao salvar configuração para ${exchange_label}. Tente novamente.`;
        message.className = "temporary_message error";
        message.hidden = false;
        return;
    }

    const data = await response.json();

    if (data.message) {
        message.className = "temporary_message success";
        message.textContent = `Configuração salva com sucesso para ${exchange_label}.`;
        setTimeout(() => {message.hidden = true; window.location.href = "/automation/"}, 2000);
    }
})


// botão para salvar a api do usuário em cache por 30 dias
document.getElementById("form_api")?.addEventListener("submit", async (event) => { event.preventDefault();

    const exchange = getActiveExchange();
    const exchange_label = getExchangeLabel(exchange);
    const api_message = document.getElementById("api_message") as HTMLParagraphElement;

    const api_key = (document.getElementById("api_key") as HTMLInputElement).value.trim();
    const api_secret = (document.getElementById("api_secret") as HTMLInputElement).value.trim();
    const api_passphrase = (document.getElementById("api_passphrase") as HTMLInputElement).value.trim();

    if (!api_key || !api_secret) {
        api_message.textContent = "Api Key e Secret Key são obrigatórios.";
        api_message.className = "temporary_message error";
        api_message.hidden = false;
        return;
    }

    const payload = {
        exchange: exchange,
        API_KEY: api_key,
        API_SECRET: api_secret,
        API_PASSPHRASE: api_passphrase,
    }

    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;

    // Warning: salvando
    api_message.hidden = true;
    api_message.textContent = `Salvando conexão da API para ${exchange_label}...`;
    api_message.className = "temporary_message warning";
    api_message.hidden = false;

    const response = await fetch("/api/v1/automation/api", {method: "POST", credentials: "include", headers: {"content-type": "application/json", "x-csrftoken": csrf.value}, body: JSON.stringify(payload)});

    if (!response.ok) {
        api_message.textContent = `Erro ao salvar API para ${exchange_label}. Tente novamente.`;
        api_message.className = "temporary_message error";
        api_message.hidden = false;
        return;
    }

    const data = await response.json();

    // mensagem temporaria de api salva e depois redireciona para buscar estado atual no dom
    if (data.message) {
        api_message.textContent = `API salva com sucesso para ${exchange_label}.`;
        api_message.className = "temporary_message success";
        setTimeout(() => {api_message.hidden = true; api_message.textContent = "";}, 2000);
    }
})


// botão para ligar a automação, clica em ligar e a página é atualizada buscando o estado da automação atual
document.getElementById("enable_automation")?.addEventListener("click", async () => {

    const status_botao = document.getElementById("enable_automation") as HTMLButtonElement;

    const endpoint = status_botao.dataset.enabled == "true"
        ? "/api/v1/automation/disable"
        : "/api/v1/automation/enable";

    const exchange = getActiveExchange();
    const payload = {exchange: exchange};
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;

    const response = await fetch(endpoint, {method: "POST", credentials: "include", headers: {"content-type": "application/json", "x-csrftoken": csrf.value}, body: JSON.stringify(payload)});

    if (!response.ok) {
        status_botao.textContent = status_botao.dataset.enabled == "true" ? "Desativar Automação" : "Ativar Automação";
        return;
    }

    window.location.href = "/automation/";
});
