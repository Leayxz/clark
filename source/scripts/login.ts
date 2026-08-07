document.getElementById("AuthForm")?.addEventListener("submit", async (event) => { event.preventDefault()

    const email = document.getElementById("email") as HTMLInputElement;
    const password = document.getElementById("password") as HTMLInputElement;

    const errorEl = document.getElementById("error") as HTMLParagraphElement;
    errorEl.style.display = "none";

    const csrf = document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement;
    const PAYLOAD = {"email": email.value, "password": password.value}

    const response = await fetch("/api/v1/login", {"method": "POST", "headers": {"Content-Type": "application/json",
                                                                                  "X-CSRFToken": csrf.value},
                                                                                  "body": JSON.stringify(PAYLOAD)})

    const data = await response.json()

    if (!response.ok) {
        errorEl.textContent = data.error;
        errorEl.style.display = "block";
        errorEl.style.color = "red";
        console.error(data.error);
        return;
    }

    // armazena access, refresh token e redireciona para próxima página
    // deve armazenar em cookie httponly
    console.log("Usuário autenticado com sucesso.")
    window.location.href = "/dashboard/"          
})
