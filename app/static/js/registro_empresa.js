document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".form-register");
    const mensajeArea = document.querySelector(".mensajes");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        mensajeArea.innerHTML = ""; // limpiar mensajes

        const correo = form.email.value.trim();
        const password = form.password.value.trim();
        const confirmar = form.confirmar.value.trim();

        // 🟥 Validar coincidencia de contraseñas
        if (password !== confirmar) {
            mensajeArea.innerHTML = `<p style="color:red;">Las contraseñas no coinciden</p>`;
            return;
        }

        // 🟥 Validar existencia del correo (consulta al servidor)
        const respuesta = await fetch("/verificar_correo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo })
        });

        const data = await respuesta.json();
        if (data.existe) {
            mensajeArea.innerHTML = `<p style="color:red;">El correo ya está registrado</p>`;
            return;
        }

        // ✅ Si todo está bien, envía el formulario al backend
        form.submit();
    });
});
