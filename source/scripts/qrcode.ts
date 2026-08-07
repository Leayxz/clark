document.getElementById("gerar_invoice")?.addEventListener("click", async () => {

    const response = await fetch("/api/v1/payment/create/sats", {method: "POST", "credentials": "include"})
    const data = await response.json()

    if (!response.ok) {
        console.error(data.error)
        alert("Erro ao gerar invoice.")
        return
    }

    let qrcode = document.getElementById("qrcode_img") as HTMLImageElement
    qrcode.src = "data:image/png;base64," + data.qrcode
    
    let modal = document.getElementById("modal-invoice") as HTMLDivElement
    modal.style.display = "flex"

    let deposit_id = document.getElementById("deposit-id") as HTMLParagraphElement
    deposit_id.textContent = "Deposit ID: " + data.deposit_id

    let payment_request = document.getElementById("payment-request") as HTMLParagraphElement
    payment_request.textContent = data.payment_request

    // REDIRECIONA PÓS 2 MINUTOS
    setTimeout(() => {window.location.href = "/dashboard/"}, 2 * 60 * 1000)

})


document.getElementById("btn-pagamento")?.addEventListener("click", () => {
    window.location.href = "/dashboard/"

});
