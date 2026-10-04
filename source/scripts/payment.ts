declare const QRCode: {toCanvas( canvas: HTMLCanvasElement, text: string, options?: object): void};

class Cupom {

    constructor() { this.start_listening(); }

    start_listening() {
        document.getElementById("coupon_button")?.addEventListener("click", async () => { this.validacao_cupom(); })
        document.getElementById("confirmar_assinatura")?.addEventListener("click", async (event) => { event.preventDefault(); this.gerar_invoice(); });

        const cpfInput = document.getElementById("cpf_input") as HTMLInputElement | null;
        if (cpfInput) {
            cpfInput.addEventListener("input", () => {
                cpfInput.value = cpfInput.value.replace(/[^0-9]/g, '');
            });
        }

        const copyBtn = document.getElementById("pm-copy") as HTMLButtonElement | null;
        if (copyBtn) {
            copyBtn.addEventListener("click", async () => {
                const code = document.getElementById("pm-code-val")?.textContent || "";
                const copyText = document.getElementById("pm-copy-text");

                try {
                    await navigator.clipboard.writeText(code);
                    if (copyText) {
                        copyText.textContent = "Copiado!";
                        setTimeout(() => {
                            copyText.textContent = "Copiar código PIX";
                        }, 2000);
                    }
                } catch (err) {
                    console.error("Falha ao copiar:", err);
                }
            });
        }
    }


    async validacao_cupom() {

        // Reset do estado para permitir múltiplas tentativas
        const hint = document.getElementById("coupon_hint")!;
        const hintText = document.getElementById("coupon_hint_text")!;

        hint.classList.remove("coupon__hint--visible", "coupon__hint--hidden", "error");
        hint.classList.add("coupon__hint--hidden");
        hint.removeAttribute("hidden");

        const discountRow = document.getElementById("os-discount-row") as HTMLElement | null;
        if (discountRow) {
            discountRow.classList.add("is-hidden");
        }

        const totalFull = document.getElementById("os-total-full") as HTMLElement | null;
        if (totalFull) {
            totalFull.textContent = "R$150,00";
        }

        const coupon_code = (document.getElementById("coupon_input") as HTMLInputElement)!.value.trim();
        const csrftoken = (document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement)!.value;
        const response = await fetch('/api/v1/coupon/validate', {method: 'POST', credentials: "include", headers: {'Content-Type': 'application/json', "x-csrftoken": csrftoken},  body: JSON.stringify({ coupon_code: coupon_code })});

        if (!response.ok) {
            hintText.textContent = "Cupom Inválido — Desconto Não Aplicado";
            hint.className = "coupon__hint coupon__hint--visible coupon__hint--error";
            return;
        }

        const data = await response.json();
        hintText.innerHTML = `<strong>${data.coupon_code}</strong> aplicado — 10% OFF`;
        hint.className = "coupon__hint coupon__hint--visible coupon__hint--success";

        if (discountRow) {
            const couponName = discountRow.querySelector("#os-coupon-name") as HTMLElement | null;
            if (couponName) couponName.textContent = data.coupon_code;
            const discountVal = discountRow.querySelector(".order-summary__val--down") as HTMLElement | null;
            if (discountVal) discountVal.textContent = '10% OFF';
            discountRow.classList.remove("is-hidden");
        }

        if (totalFull) {
            totalFull.textContent = `R$135,00`;
        }
    }


    async gerar_invoice() {

        const coupon_code = (document.getElementById("coupon_input") as HTMLInputElement)!.value.trim();
        const cpf = (document.getElementById("cpf_input") as HTMLInputElement)!.value.trim();

        const cleanCpf = cpf.replace(/[^0-9]/g, '');

        const cpfInput = document.getElementById("cpf_input") as HTMLInputElement | null;
        const cpfError = document.getElementById("cpf_error") as HTMLElement | null;
        const cpfErrorText = document.getElementById("cpf_error_text") as HTMLElement | null;
        const confirmBtn = document.getElementById("confirmar_assinatura") as HTMLButtonElement | null;

        if (cpfError) {
            cpfError.classList.remove("is-visible");
        }

        if (cleanCpf.length < 11) {
            if (cpfInput) {
                cpfInput.classList.remove("field__input--shake");
                void cpfInput.offsetWidth;
                cpfInput.classList.add("field__input--error", "field__input--shake");
            }
            if (cpfError && cpfErrorText) {
                cpfErrorText.textContent = "CPF é obrigatório. Digite pelo menos 11 números.";
                cpfError.classList.add("is-visible");
            }
            return;
        }

        if (cpfError) {
            cpfError.classList.remove("is-visible");
        }

        if (confirmBtn) {
            confirmBtn.disabled = true;
            confirmBtn.textContent = "Carregando...";
        }

        const URL = "/api/v1/payment/create/pix";
        const csrf_token = document.querySelector<HTMLInputElement>("[name=csrfmiddlewaretoken]")!.value;
        const response = await fetch(URL, { method: "POST", credentials: "include", headers: { "content-type": "application/json", "x-csrftoken": csrf_token }, body: JSON.stringify({ coupon_code: coupon_code, payer_tax_number: cleanCpf }) });

        if (!response.ok) {
            const data = await response.json();
            if (response.status === 400) {
                if (cpfError && cpfErrorText) {
                    cpfErrorText.textContent = data.message || "CPF/CNPJ inválido.";
                    cpfError.classList.add("is-visible");
                }
            } else {
                const paymentErrorText = document.getElementById("payment_error_text");
                if (paymentErrorText) {
                    paymentErrorText.textContent = data.message || "Erro ao criar pagamento. Aguarde alguns minutos e tente novamente.";
                }
                const paymentError = document.getElementById("payment_error");
                if (paymentError) {
                    paymentError.classList.add("is-visible");
                }
            }
            if (confirmBtn) {
                confirmBtn.disabled = false;
                confirmBtn.textContent = "Confirmar assinatura";
            }
            return;
        }

        const data = await response.json();

        document.getElementById("titulo_forma_pagamento")!.innerText = `Pagar com Pix`;

        if (confirmBtn) {
            confirmBtn.disabled = false;
            confirmBtn.textContent = "Confirmar assinatura";
        }

        modal!.classList.add("active");
        modal!.setAttribute("aria-hidden", "false");
        modal!.setAttribute("data-state", "criando");

        const feedbackEl = document.getElementById("pm-feedback") as HTMLElement | null;
        const feedbackIcon = document.getElementById("pm-feedback-icon") as SVGSVGElement | null;
        const feedbackText = document.getElementById("pm-feedback-text") as HTMLElement | null;

        if (feedbackEl) {
            feedbackEl.classList.remove("visible", "success", "warning");
            feedbackEl.setAttribute("hidden", "");
        }

        const couponLine = document.getElementById("pm-coupon-line") as HTMLElement | null;
        const totalEl = document.getElementById("pm-total") as HTMLElement | null;

        if (data.coupon) {
            couponLine?.removeAttribute("hidden");
            const couponName = couponLine?.querySelector(".pay-modal__row-label") as HTMLElement | null;
            if (couponName) couponName.textContent = `Cupom ${coupon_code}`;
            const discountVal = couponLine?.querySelector(".pay-modal__row-val--up") as HTMLElement | null;
            if (discountVal) discountVal.textContent = `10% OFF`;
            if (totalEl) totalEl.innerHTML = `R$135,00<span class="per">/mês</span>`;

            if (feedbackEl && feedbackIcon && feedbackText) {
                feedbackEl.classList.add("visible", "success");
                feedbackEl.removeAttribute("hidden");
                feedbackIcon.innerHTML = '<circle cx="12" cy="12" r="10"/><line x1="9" y1="12" x2="12" y2="15"/><line x1="12" y1="15" x2="15" y2="9"/>';
                feedbackText.textContent = "Cupom aplicado — 10% OFF";
            }
        } else {
            couponLine?.setAttribute("hidden", "");
            if (totalEl) totalEl.innerHTML = `R$150<span class="per">/mês</span>`;

            if (feedbackEl && feedbackIcon && feedbackText) {
                feedbackEl.classList.add("visible", "warning");
                feedbackEl.removeAttribute("hidden");
                feedbackIcon.innerHTML = '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>';
                feedbackText.textContent = "Valor cheio — R$150,00";
            }
        }

        const qrcode_container = document.getElementById("qrcode_image");
        if (!qrcode_container) return;
        qrcode_container.innerHTML = "";
        const canvas = document.createElement("canvas");
        qrcode_container.appendChild(canvas);
        QRCode.toCanvas(canvas, data.qr_code, { width: 256 });

        const codeVal = document.getElementById("pm-code-val");
        if (codeVal) codeVal.textContent = data.qr_code;

        modal!.setAttribute("data-state", "aguardando");
    }
}




document.addEventListener("DOMContentLoaded", async () => {
    new Cupom();
});

const modal = document.getElementById("pay-modal");

document.getElementById("pay-modal-close")?.addEventListener("click", () => {
    modal?.classList.remove("active");
    modal?.setAttribute("aria-hidden", "true");
});
