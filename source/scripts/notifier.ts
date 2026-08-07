interface NotifierProtocol {
    telegram_token: string
    telegram_id: string
    error: string
}


document.addEventListener("DOMContentLoaded", async () => {

    const response = await fetch("/api/v1/notifier/telegram", {method: "GET", credentials: "include", headers: {"Content-Type": "application/json"}})
    const data : NotifierProtocol = await response.json()
    console.log(data)
    if (!response.ok) {
        console.error(data.error)
        return
    }

    (document.getElementById("telegram_token") as HTMLInputElement).value = data.telegram_token;
    (document.getElementById("telegram_id") as HTMLInputElement).value = data.telegram_id;
})


document.getElementById("formulario_telegram")?.addEventListener("submit", async (event) => { event.preventDefault()

    const payload = {
        telegram_token: (document.getElementById("telegram_token") as HTMLInputElement).value,
        telegram_id: (document.getElementById("telegram_id") as HTMLInputElement).value
    }



    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;
    const response = await fetch("/api/v1/notifier/telegram", {method: "POST", credentials: "include", headers: {"Content-Type": "application/json", "x-csrftoken": csrf.value}, body: JSON.stringify(payload)})
    const data = await response.json()

    if (!response.ok) {
        console.log(data.error)
    }
});
