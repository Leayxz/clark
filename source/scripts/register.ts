// script responsável por buscar os dados que precisam ser enviados para a API de cadastro
document.getElementById("AuthForm")?.addEventListener("submit", async (event) => { event.preventDefault();

    const email = document.getElementById("email") as HTMLInputElement;
    const password = document.getElementById("password") as HTMLInputElement;

    const errorEl = document.getElementById("error") as HTMLParagraphElement;
    errorEl.style.display = "none";

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
    // deve redirecionar direto pra /home/
    // talvez mostrar mensagem de sucesso, aguardar 1s e depois redirecionar.
    console.log(result);
    console.log(data);
    //window.location.href = "/v1/login/"
})
