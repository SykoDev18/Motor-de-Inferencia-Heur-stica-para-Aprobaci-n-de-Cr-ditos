// ============================================================
// MIHAC v1.0 — formulario.js
// Validación client-side y DTI preview en tiempo real
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    // ── Elementos del formulario ────────────────────────────
    const ingresoInput  = document.getElementById("ingreso");
    const deudaInput    = document.getElementById("deuda");
    const dtiBar        = document.getElementById("dtiBar");
    const dtiBadge      = document.getElementById("dtiBadge");
    const form          = document.getElementById("formEvaluacion");

    // ── DTI Preview en tiempo real ──────────────────────────
    function actualizarDTI() {
        const ingreso = parseFloat(ingresoInput?.value) || 0;
        const deuda   = parseFloat(deudaInput?.value) || 0;

        if (ingreso <= 0) {
            if (dtiBar)   dtiBar.style.width = "0%";
            if (dtiBadge) {
                dtiBadge.textContent = "0.0%";
                dtiBadge.className = "badge bg-secondary";
            }
            return;
        }

        const dti = (deuda / ingreso) * 100;
        const dtiCapped = Math.min(dti, 100);

        // Actualizar barra
        if (dtiBar) {
            dtiBar.style.width = dtiCapped + "%";
            // Color según nivel
            dtiBar.classList.remove("score-bajo", "score-medio", "score-alto");
            if (dti < 25) {
                dtiBar.classList.add("score-alto");   // Verde = bueno
            } else if (dti < 40) {
                dtiBar.classList.add("score-medio");  // Ámbar = moderado
            } else {
                dtiBar.classList.add("score-bajo");   // Rojo = crítico
            }
        }

        // Actualizar badge
        if (dtiBadge) {
            dtiBadge.textContent = dti.toFixed(1) + "%";
            if (dti < 25) {
                dtiBadge.className = "badge bg-success";
            } else if (dti < 40) {
                dtiBadge.className = "badge bg-warning text-dark";
            } else {
                dtiBadge.className = "badge bg-danger";
            }
        }
    }

    // Escuchar cambios en ingreso y deuda
    if (ingresoInput) ingresoInput.addEventListener("input", actualizarDTI);
    if (deudaInput)   deudaInput.addEventListener("input", actualizarDTI);

    // Calcular al cargar (por si hay valores prellenados)
    actualizarDTI();

    // ── Validación client-side (Bootstrap 5) ────────────────
    if (form) {
        form.addEventListener("submit", (event) => {
            // Marcar campos inválidos con clases Bootstrap
            const campos = form.querySelectorAll(
                "input[required], select[required], .form-control, .form-select"
            );

            let hayErrores = false;

            campos.forEach((campo) => {
                // Limpiar estado previo
                campo.classList.remove("is-valid", "is-invalid");

                if (!campo.checkValidity()) {
                    campo.classList.add("is-invalid");
                    hayErrores = true;
                } else if (campo.value.trim() !== "") {
                    campo.classList.add("is-valid");
                }
            });

            // Si hay errores HTML5, prevenir envío
            if (hayErrores) {
                event.preventDefault();
                event.stopPropagation();

                // Scroll al primer error
                const primerError = form.querySelector(".is-invalid");
                if (primerError) {
                    primerError.scrollIntoView({
                        behavior: "smooth",
                        block: "center",
                    });
                    primerError.focus();
                }
            }
        });
    }

    // ── Formatear montos al perder foco ─────────────────────
    const camposMoneda = [ingresoInput, deudaInput,
                          document.getElementById("monto")];

    camposMoneda.forEach((campo) => {
        if (!campo) return;
        campo.addEventListener("blur", () => {
            const val = parseFloat(campo.value);
            if (!isNaN(val) && val >= 0) {
                // Redondear a 2 decimales
                campo.value = val.toFixed(2);
            }
        });
    });
});
