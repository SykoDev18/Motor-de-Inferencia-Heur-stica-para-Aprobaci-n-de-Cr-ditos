# ============================================================
# MIHAC v1.0 — Utilidades y Helpers
# app/utils.py
# ============================================================
# Funciones auxiliares para formateo, conversiones y
# operaciones comunes de la interfaz web.
# ============================================================

from typing import Any


def formato_moneda(valor: float) -> str:
    """Formatea un valor numérico como moneda.

    Args:
        valor: Cantidad a formatear.

    Returns:
        String con formato $XX,XXX.XX
    """
    return f"${valor:,.2f}"


def formato_porcentaje(valor: float) -> str:
    """Formatea un valor como porcentaje.

    Args:
        valor: Valor decimal (0.25 → 25.0%).

    Returns:
        String con formato XX.X%.
    """
    return f"{valor * 100:.1f}%"


def color_dictamen(dictamen: str) -> str:
    """Retorna el color CSS para un dictamen.

    Args:
        dictamen: APROBADO, RECHAZADO, o REVISION_MANUAL.

    Returns:
        Código hexadecimal del color.
    """
    colores = {
        "APROBADO": "#10B981",
        "RECHAZADO": "#EF4444",
        "REVISION_MANUAL": "#F59E0B",
    }
    return colores.get(dictamen, "#64748B")


def clase_badge_dictamen(dictamen: str) -> str:
    """Retorna la clase CSS de Bootstrap para el badge.

    Args:
        dictamen: APROBADO, RECHAZADO, o REVISION_MANUAL.

    Returns:
        Clase CSS (bg-success, bg-danger, bg-warning).
    """
    clases = {
        "APROBADO": "bg-success",
        "RECHAZADO": "bg-danger",
        "REVISION_MANUAL": "bg-warning text-dark",
    }
    return clases.get(dictamen, "bg-secondary")


def texto_historial(codigo: int) -> str:
    """Convierte código de historial a texto legible.

    Args:
        codigo: 0=Malo, 1=Neutro, 2=Bueno.

    Returns:
        Texto descriptivo.
    """
    textos = {0: "Malo", 1: "Neutro", 2: "Bueno"}
    return textos.get(codigo, "Desconocido")


def clasificar_dti(dti: float) -> dict[str, Any]:
    """Clasifica un DTI y retorna info para UI.

    Args:
        dti: Ratio deuda/ingreso (0.0 a 1.0+).

    Returns:
        Dict con clase, color, texto y nivel.
    """
    pct = dti * 100
    if pct < 25:
        return {
            "clase": "bg-success",
            "color": "#10B981",
            "texto": "BAJO",
            "nivel": "bajo",
        }
    elif pct < 40:
        return {
            "clase": "bg-warning text-dark",
            "color": "#F59E0B",
            "texto": "MODERADO",
            "nivel": "moderado",
        }
    elif pct < 60:
        return {
            "clase": "bg-warning",
            "color": "#F59E0B",
            "texto": "ALTO",
            "nivel": "alto",
        }
    else:
        return {
            "clase": "bg-danger",
            "color": "#EF4444",
            "texto": "CRÍTICO",
            "nivel": "critico",
        }
