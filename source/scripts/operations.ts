interface OperationsProtocol {
    today_operations: number
    today_profit: number
    month_operations: number
    month_profit: number
    all_time_operations: number
    all_time_profit: number
    total_balance: number
    total_balance_available: number
    total_balance_exposed: number
}

class Operations {

    constructor() { this.get_all_period_data(); this.start_listening(); }

    start_listening() {}

    async get_all_period_data() {

        const response = await fetch(`/api/v1/operations`, {method: "GET", credentials: "include"});

        if (response.status === 401) {
            window.location.href = "/";
            return;
        }

        const data: OperationsProtocol = await response.json();

        document.getElementById("today_operations")!.textContent = `${data.today_operations} operações`
        document.getElementById("today_profit")!.textContent = `${data.today_profit} BTC`

        document.getElementById("month_operations")!.textContent = `${data.month_operations} operações`
        document.getElementById("month_profit")!.textContent = `${data.month_profit} BTC`

        document.getElementById("all_time_operations")!.textContent = `${data.all_time_operations} operações`
        document.getElementById("all_time_profit")!.textContent = `${data.all_time_profit} BTC`

        document.getElementById("total_balance")!.textContent = `${data.total_balance} BTC`
        document.getElementById("total_balance_available")!.textContent = `${data.total_balance_available} BTC`
        document.getElementById("total_balance_exposed")!.textContent = `${data.total_balance_exposed} BTC`
    }
}
new Operations();

/* ----------------------------------------------------------------
   Calculadora de contrato inverso BTC/USD (margem e P/L em sats).

   Responde DUAS perguntas, que são a MESMA equação resolvida para
   variáveis diferentes:

       total_sats = quantidade_usd × sats_por_usd × operações

   com   sats_por_usd = 100.000.000 × |1/entrada − 1/saída|

   que depende SÓ dos preços, nunca do tamanho da posição.

   Vocabulário (é aqui que a confusão nasce):
     quantidade  = notional em USD (o "Quantidade" da LNMarkets)
     margem_sats = quantidade × SATS / entrada / alavancagem
     margem_usd  = margem_sats / SATS × entrada  ==  quantidade / alavancagem

   Ou seja: margem_USD é SEMPRE quantidade_USD ÷ alavancagem.
   ---------------------------------------------------------------- */

const SATS = 100_000_000;
type Side = "long" | "short";
type Mode = "usd" | "sats";

class Calculator {

    private mode: Mode = "usd";

    constructor() { this.bind(); this.update(); }

    bind() {
        const inputs = ["calc_value", "calc_entry", "calc_exit", "calc_leverage", "calc_direction", "calc_ops", "calc_fee"];
        inputs.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            el.addEventListener("input", () => this.update());
            el.addEventListener("change", () => this.update());
        });

        document.getElementById("calc_mode_usd")!.addEventListener("click", () => this.setMode("usd"));
        document.getElementById("calc_mode_sats")!.addEventListener("click", () => this.setMode("sats"));
    }

    /** Troca de pergunta convertendo o valor atual, sem zerar o cenário. */
    private setMode(next: Mode) {
        if (next === this.mode) return;

        const entry = this.num("calc_entry");
        const exit = this.num("calc_exit");
        const ops = this.ops();
        const satsPerUsd = this.satsPerUsd(entry, exit);
        const value = this.num("calc_value");

        if (satsPerUsd > 0 && value > 0) {
            if (this.mode === "usd") {
                // quantidade USD por ordem -> total de sats do período
                this.setInput("calc_value", String(Math.floor(value * satsPerUsd) * ops));
            } else {
                // total de sats -> quantidade USD por ordem
                this.setInput("calc_value", (value / ops / satsPerUsd).toFixed(2));
            }
        }

        this.mode = next;
        document.getElementById("calc_mode_usd")!.classList.toggle("is-active", next === "usd");
        document.getElementById("calc_mode_sats")!.classList.toggle("is-active", next === "sats");
        this.setText("calc_value_label", next === "usd"
            ? "Quantidade por ordem (USD)"
            : "Quantos sats você quer no total");
        this.update();
    }

    private num(id: string): number {
        const el = document.getElementById(id) as HTMLInputElement | null;
        return el ? parseFloat(el.value) || 0 : 0;
    }

    private setInput(id: string, value: string) {
        const el = document.getElementById(id) as HTMLInputElement | null;
        if (el) el.value = value;
    }

    private side(): Side {
        return (document.getElementById("calc_direction") as HTMLSelectElement).value === "short" ? "short" : "long";
    }

    private leverage(): number {
        const l = parseInt((document.getElementById("calc_leverage") as HTMLSelectElement).value);
        return l > 0 ? l : 1;
    }

    private ops(): number {
        const n = Math.floor(this.num("calc_ops"));
        return n > 0 ? n : 100;
    }

    private setText(id: string, text: string) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    private fmt(value: number, decimals: number = 0): string {
        return value.toLocaleString("pt-BR", {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        });
    }

    /** Sats por 1 USD de quantidade. Depende só dos preços. */
    private satsPerUsd(entry: number, exit: number): number {
        if (entry <= 0 || exit <= 0) return 0;
        return SATS * Math.abs(1 / entry - 1 / exit);
    }

    /** Tamanho da posição em sats: quantidade × SATS / preço */
    private positionSats(quantity: number, price: number): number {
        return (quantity * SATS) / price;
    }

    /** P/L bruto em sats. Long ganha quando o preço sobe. */
    private grossPnlSats(side: Side, quantity: number, entry: number, exit: number): number {
        const diff = quantity * SATS * (1 / entry - 1 / exit);
        return side === "long" ? diff : -diff;
    }

    /** Taxas (abertura + fechamento) com floor por lado — igual à LNMarkets. */
    private feeSats(quantity: number, entry: number, exit: number, feeRate: number): number {
        const open = Math.floor(this.positionSats(quantity, entry) * feeRate);
        const close = Math.floor(this.positionSats(quantity, exit) * feeRate);
        return open + close;
    }

    /** Preço de liquidação "puro". null quando não existe. */
    private liquidationPrice(side: Side, quantity: number, entry: number, marginSats: number): number | null {
        if (quantity <= 0) return null;
        const m = marginSats / SATS; // margem em BTC
        const inv = side === "long" ? 1 / entry + m / quantity : 1 / entry - m / quantity;
        return inv > 0 ? 1 / inv : null;
    }

    update() {
        const entry = this.num("calc_entry");
        const exit = this.num("calc_exit");
        const value = this.num("calc_value");
        const leverage = this.leverage();
        const side = this.side();
        const feeRate = this.num("calc_fee") / 100;
        const ops = this.ops();

        if (entry <= 0 || exit <= 0 || value <= 0) return;

        const satsPerUsd = this.satsPerUsd(entry, exit);
        if (satsPerUsd <= 0) {
            this.setText("calc_answer", "Preço de entrada e de saída iguais — não há lucro nesse cenário.");
            return;
        }

        // As duas perguntas, uma equação só.
        let quantity: number;   // USD de quantidade por ordem
        let totalSats: number;  // sats brutos no período

        if (this.mode === "usd") {
            quantity = value;
            totalSats = Math.floor(quantity * satsPerUsd) * ops;
        } else {
            totalSats = value;
            const perOrder = totalSats / ops;
            quantity = Math.ceil((perOrder / satsPerUsd) * 100) / 100;
        }

        const perOrder = Math.floor(this.grossPnlSats(side, quantity, entry, exit));
        const positionSats = this.positionSats(quantity, entry);
        const marginSats = Math.floor(positionSats / leverage);
        const marginUsd = marginSats / SATS * entry;      // == quantity / leverage
        const fees = this.feeSats(quantity, entry, exit, feeRate);
        const net = perOrder - fees;
        const liq = this.liquidationPrice(side, quantity, entry, marginSats);

        this.setText("calc_answer", this.mode === "usd"
            ? `Com ${this.fmt(quantity, 2)} USD de quantidade por ordem você faz ${this.fmt(perOrder)} sats brutos por ordem — ${this.fmt(totalSats)} sats em ${this.fmt(ops)} operações.`
            : `Para fazer ${this.fmt(totalSats)} sats brutos em ${this.fmt(ops)} operações você precisa de ${this.fmt(quantity, 2)} USD de quantidade por ordem (${this.fmt(marginUsd, 2)} USD de margem).` +
              (perOrder * ops !== totalSats
                  ? ` Com esse arredondamento a meta real fica em ${this.fmt(perOrder * ops)} sats.`
                  : ""));

        this.setText("calc_ans_quantity", `$${this.fmt(quantity, 2)}`);
        this.setText("calc_ans_margin_sats", `${this.fmt(marginSats)} sats`);
        this.setText("calc_ans_margin_usd", `$${this.fmt(marginUsd, 2)}`);
        this.setText("calc_ans_pnl_order", `${this.fmt(perOrder)} sats`);
        this.setText("calc_ans_net_order", `${this.fmt(net)} sats`);
        this.setText("calc_ans_liquidation", liq !== null ? `$${this.fmt(liq, 1)}` : "—");

        // Cenário exposto no dataset — usado pelos testes de paridade.
        const root = document.getElementById("calc_answer");
        if (root) {
            root.dataset.quantity = String(quantity);
            root.dataset.totalSats = String(totalSats);
            root.dataset.marginSats = String(marginSats);
            root.dataset.marginUsd = String(marginUsd);
            root.dataset.pnlPerOrder = String(perOrder);
            root.dataset.fees = String(fees);
            root.dataset.netPerOrder = String(net);
        }
    }
}

new Calculator();
