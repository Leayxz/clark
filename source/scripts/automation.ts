interface ConfiguracaoData {
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
    const response = await fetch("/api/v1/automation/dashboard", {"method": "GET", "credentials": "include"})
    const data: ConfiguracaoData = await response.json();

    if (!response.ok) {
        console.error(data);
        return;
    }

    (document.getElementById("api-key") as HTMLInputElement).value = data.API_KEY;
    (document.getElementById("api-secret") as HTMLInputElement).value = data.API_SECRET;
    (document.getElementById("api-passphrase") as HTMLInputElement).value = data.API_PASSPHRASE;

    let status_automation = document.getElementById("status_automation") as HTMLParagraphElement
    let botao_ligar_automacao = document.getElementById("enable_automation") as HTMLButtonElement;


    status_automation.textContent = data.status_automation
        ? "🟢 Sessão rodando!"
        : "🔴 Sessão parada";

    botao_ligar_automacao.textContent = data.status_automation
        ? "Desligar Automação"
        : "Ligar Automação";

    // alimenta o botão de ligar com "true" para o próximo click bater no endpoint "disable" e desligar a automação
    botao_ligar_automacao.dataset.enabled = String(data.status_automation);


    (document.getElementById("marginUSD") as HTMLInputElement).value = String(data.marginUSD);
    (document.getElementById("leverage") as HTMLInputElement).value = String(data.leverage);
    (document.getElementById("percentage_profit") as HTMLInputElement).value = String(data.percentage_profit);
    (document.getElementById("buy_variation") as HTMLInputElement).value = String(data.buy_variation);
})



// botão para salvar novas configurações
document.getElementById("configuration-form")?.addEventListener("submit", async (event) => { event.preventDefault();
    
    const body = {
        marginUSD: (document.getElementById("marginUSD") as HTMLInputElement).value,
        leverage: (document.getElementById("leverage") as HTMLInputElement).value,
        buy_variation: (document.getElementById("buy_variation") as HTMLInputElement).value,
        percentage_profit: (document.getElementById("percentage_profit") as HTMLInputElement).value,
    }

    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;
    const response = await fetch("/api/v1/automation/configuration", {"method": "POST", "credentials": "include", "headers": {"Content-Type": "application/json", "x-csrftoken": csrf.value}, "body": JSON.stringify(body)});
    const data = await response.json();

    if (!response.ok) {
        console.error(data.error);
        return;
    }

    
    // deve mostrar mensagem temporaria de configuração salva com sucesso, desaparecendo em alguns segundos
    if (data.message) {
        let message = (document.getElementById("message") as HTMLParagraphElement);
        message.textContent = data.message;
        message.hidden = false;
        // temporizador da mensagem de sucesso e
        setTimeout(() => {message.hidden = true; message.textContent = "";}, 3000)
    }
})





// botão para salvar a api do usuário em cache por 30 dias
document.getElementById("form-api")?.addEventListener("submit", async (event) => { event.preventDefault()

    // busca os campos do form, api key e secret
    const payload = {
        API_KEY: (document.getElementById("api-key") as HTMLInputElement).value,
        API_SECRET: (document.getElementById("api-secret") as HTMLInputElement).value,
        API_PASSPHRASE: (document.getElementById("api-passphrase") as HTMLInputElement).value,
        exchange: "lnmarkets"
    }

    // faz o fetch para o servidor salvar os dados
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;
    const response = await fetch("/api/v1/automation/api", {method: "POST", credentials: "include", headers: {"content-type": "application/json", "x-csrftoken": csrf.value}, body: JSON.stringify(payload)})
    const data = await response.json()

    if (!response.ok) {
        console.error(data.error)
    }

    // mensagem temporaria de api salva e depois redireciona para buscar estado atual no dom
    if (data.message) {
        let api_message = (document.getElementById("api-message") as HTMLParagraphElement)
        api_message.textContent = data.message
        api_message.hidden = false

        // temporizador da mensagem de sucesso e depois redireconar pra buscar estado atual
        setTimeout(() => {api_message.hidden = true; api_message.textContent = ""}, 2000);
    }
})







// botão para ligar a automação, clica em ligar e a página é atualizada buscando o estado da automação atual
document.getElementById("enable_automation")?.addEventListener("click", async () => {

    const status_botao = document.getElementById("enable_automation") as HTMLButtonElement;
    
    const endpoint = status_botao.dataset.enabled == "true"
        ? "/api/v1/automation/disable"
        : "/api/v1/automation/enable";

    const payload = {exchange: "lnmarkets"};
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;

    const response = await fetch(endpoint, {method: "POST", credentials: "include", headers: {"content-type": "application/json", "x-csrftoken": csrf.value}, body: JSON.stringify(payload)});
    const data = await response.json();


    if (!response.ok) {
        console.error(data.error);
        return;
    }

    window.location.href = "/automacao/";
});
