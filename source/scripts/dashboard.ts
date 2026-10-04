interface OverviewProtocol {
    btc_usd_price: number;
    total_patrimony: number;
    total_margin_exposed: number;
    open_orders: number;
    goal_target: number;
    all_time_profit: number;
    last_month_profit: number;
    last_operations: any;
}


interface OverviewPeriodProtocol {
    btc_usd_price: number;
    total_profit: number;
    total_operations: number;
    total_fees: number;
}


class Dashboard {

    constructor() { this.get_data(); this.start_listener(); }

    async get_data() {
        await Promise.all([ this.get_overview_data(), this.get_overview_period("today")])
    }

    start_listener() {
        document.getElementById("info_today")?.addEventListener("click", () => { this.get_overview_period("today"); })
        document.getElementById("info_month")?.addEventListener("click", () => { this.get_overview_period("month"); })
        document.getElementById("info_all_period")?.addEventListener("click", () => { this.get_overview_period("all_period"); })
    }

    async get_overview_period(period: "today" | "month" | "all_period") {

        const response = await fetch(`/api/v1/dashboard/period?period=${period}`, {method: "GET", credentials: "include"});
        if (response.status === 401) { window.location.href = "/"; return; }

        const data: OverviewPeriodProtocol = await response.json();
        const format = new Intl.NumberFormat("en-US", { maximumFractionDigits: 8 });

        //
        document.getElementById("info_today")?.classList.toggle("active", period === "today");
        document.getElementById("info_month")?.classList.toggle("active", period === "month");
        document.getElementById("info_all_period")?.classList.toggle("active", period === "all_period");

        //
        document.getElementById("total_operations")!.textContent = `${data.total_operations}`;
        document.getElementById("total_fees")!.textContent = `丰 ${data.total_fees}`;
        document.getElementById("total_fees_usd")!.textContent = `$${((data.total_fees / 100_000_000) * data.btc_usd_price).toFixed(2)}`;


        //
        document.getElementById("resultado_acumulado_usd")!.textContent = `$${((data.total_profit / 100_000_000) * data.btc_usd_price).toFixed(2)}`

        data.total_profit
            ? document.getElementById("resultado_acumulado")!.textContent = `丰 ${format.format(data.total_profit)} Sats`
            : document.getElementById("resultado_acumulado")!.textContent = `丰 ${data.total_profit.toFixed(5)}`;
    }



    


    async get_overview_data() {

        const response = await fetch(`/api/v1/dashboard`, {method: "GET", credentials: "include"});
        if (response.status === 401) { window.location.href = "/"; return; }

        const data: OverviewProtocol = await response.json();




        // ---------------------------------------------- Main ---------------------------------------------- //





        // ---------------------------------------------- Main ---------------------------------------------- //
        
        document.getElementById("total_patrimony")!.textContent = `丰 ${data.total_patrimony} Sats`
        document.getElementById("usd_patrimony")!.textContent = `$${((data.total_patrimony / 100_000_000) * data.btc_usd_price).toFixed(2)}`
        
        document.getElementById("total_margin_used")!.textContent = `丰 ${data.total_margin_exposed}`;
        document.getElementById("total_margin_used_usd")!.textContent = `$${((data.total_margin_exposed / 100_000_000) * data.btc_usd_price).toFixed(2)}`;

        document.getElementById("open_orders")!.textContent = `${data.open_orders}`;






        // ----------------------------------------- Goal Progress ----------------------------------------- //

        const format = new Intl.NumberFormat("en-US", { maximumFractionDigits: 8 });
        document.getElementById("goal_target")!.textContent = `${format.format(data.goal_target)} Sats`;
        document.getElementById("current_goal_state")!.textContent = `+${data.all_time_profit} Sats`;
        document.getElementById("goal_progress_bar")!.style.width = `${Math.max((data.all_time_profit / data.goal_target) * 100, 0)}%`
        document.getElementById("goal_remaining")!.textContent = `· ${Math.abs(data.all_time_profit - data.goal_target)} sats restantes`;



        // ----------------------------------------- Latest Operations ----------------------------------------- //
        const opsContainer = document.getElementById("last_operations")!;
        const opTpl = document.getElementById("op-template") as HTMLTemplateElement;
        opsContainer.replaceChildren();

        for (const value of data.last_operations) {
            const isBuy = String(value.tipo).toUpperCase().includes("COMPRA");
            const side = isBuy ? "buy" : "sell";
            const profit = value.profit ?? 0;

            const node = opTpl.content.firstElementChild!.cloneNode(true) as HTMLElement;
            const el = {
                icon:   node.querySelector(".clark-op-icon")!,
                type:   node.querySelector(".clark-op-type")!,
                time:   node.querySelector(".clark-op-time")!,
                result: node.querySelector(".clark-op-result")!,
            };

            el.icon.classList.add(side);
            el.type.classList.add(side);

            el.type.textContent   = isBuy ? "Compra" : "Venda";
            el.time.textContent   = value.closed_at ?? "";

            el.result.textContent = profit >= 0 ? `+ ${profit} Sats` : `− ${Math.abs(profit)}`;
            el.result.classList.add(profit >= 0 ? "clark-positive" : "clark-negative");

            opsContainer.appendChild(node);
        }
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


class GoalModal {

    constructor() { this.start_listener(); }

    private open() {
        const modal = document.getElementById("modal-goal") as HTMLDivElement;
        const input = document.getElementById("goal-input") as HTMLInputElement;
        const error = document.getElementById("goal-error") as HTMLParagraphElement;
        error.hidden = true;
        input.value = "";
        modal.classList.add("active");
        input.focus();
    }

    private close() {
        document.getElementById("modal-goal")?.classList.remove("active");
    }

    start_listener() {
        document.getElementById("change-goal")?.addEventListener("click", () => this.open());

        document.getElementById("goal-cancel")?.addEventListener("click", () => this.close());

        document.getElementById("goal-save")?.addEventListener("click", async () => {
            const input = document.getElementById("goal-input") as HTMLInputElement;
            const error = document.getElementById("goal-error") as HTMLParagraphElement;
            const value = Number(input.value);

            if (!Number.isInteger(value) || value < 1) {
                error.textContent = "Informe um valor maior que zero.";
                error.hidden = false;
                return;
            }

            const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement | null;
            if (!csrf) {
                error.textContent = "Não foi possível enviar: token de segurança ausente.";
                error.hidden = false;
                return;
            }

            const response = await fetch("/api/v1/dashboard/goal", { method: "PATCH", credentials: "include", headers: {"content-type": "application/json", "x-csrftoken": csrf.value}, body: JSON.stringify({ goal_target: value }), });

            if (response.status === 401) { window.location.href = "/"; return; }
            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                error.textContent = (data && data.error) ? String(data.error) : "Não foi possível salvar o objetivo.";
                error.hidden = false;
                return;
            }

            this.close();
            new Dashboard().get_overview_data();
        });
    }
}


document.addEventListener("DOMContentLoaded", async () => {
    new Dashboard();
    new LogOut();
    new GoalModal();
});
