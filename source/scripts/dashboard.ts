interface DashboardData {
    automation: boolean;
    telegram: boolean;
    payment: boolean;
    total_profit_today: BigInteger
}

document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch("/api/v1/dashboard", {"method": "GET", "credentials": "include"});
    const data: DashboardData = await response.json();

    if (!response.ok) {
        console.error(data);
        return;
    }

    const automationElement = document.getElementById("automation") as HTMLDivElement;
    const telegramElement = document.getElementById("telegram") as HTMLDivElement;
    const paymentElement = document.getElementById("payment") as HTMLDivElement;
    const total_profit_today = document.getElementById("total_profit_today") as HTMLDivElement;


 
    automationElement.textContent = data.automation
        ? "🟢 Automação Ativa"
        : "🔴 Automação Parada";

    telegramElement.textContent = data.telegram
        ? "📱 Telegram Salvo"
        : "📵 Telegram Não Salvo";

    paymentElement.textContent = data.payment
        ? "✅ Plano ativo até:"
        : "❌ Plano Inativo";

    total_profit_today.textContent = data.total_profit_today // falta tipar na interface corretamente, fiz com BigIntergender, mas não sei
        ? total_profit_today.textContent + data.total_profit_today
        : total_profit_today.textContent + "0"
})


// botão para quando o usuário realizar logout
document.getElementById("button_logout")?.addEventListener("click", async () => {
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;
    const response = await fetch("/api/v1/logout", {method: "POST", credentials: "include", headers: {"content-type": "application/json", "x-csrftoken": csrf.value}});
    const data = await response.json();

    if (!response.ok) { console.error(data.error); return; }

    window.location.href = "/login/";
});
