// script responsável por buscar os dados que precisam ser enviados para a API de cadastro
document.getElementById("register_form")?.addEventListener("submit", async (event) => { event.preventDefault();

    const email = document.getElementById("email") as HTMLInputElement;
    const password = document.getElementById("password") as HTMLInputElement;
    const confirmed_password = document.getElementById("confirmed_password") as HTMLInputElement;
    const errorEl = document.getElementById("register_error_show") as HTMLParagraphElement;

    if (password.value !== confirmed_password.value) {
        errorEl.textContent = "Senhas não coincidem."
        errorEl.style.display = "block";
        return;
    }

    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;
    const PAYLOAD = {"email": email.value, "password": password.value}

    const result = await fetch("/api/v1/register", {"method": "POST", "headers": {"Content-Type": "application/json",
                                                                                   "X-CSRFToken": csrf.value},
                                                                                   "body": JSON.stringify(PAYLOAD)})
    
                                                                                   const data = await result.json()

    if (!result.ok) {
        errorEl.textContent = data.error;
        errorEl.style.display = "block";
        errorEl.style.color = "red";
        console.error(data.error);
        return;
    }

    // Redireciona usuário registrado com sucesso para fazer o login
    window.location.href = "/login/"
})
