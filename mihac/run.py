# ============================================================
# MIHAC v1.0 — Punto de Entrada Web
# Motor de Inferencia Heurística para Aprobación de Créditos
# ============================================================
# Ejecutar con:  python run.py
# Abrir en:      http://localhost:5000
# ============================================================

import os
import sys
from pathlib import Path

# Asegurar que mihac/ esté en sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app import create_app

# Leer entorno (development | testing | production)
config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)


if __name__ == "__main__":
    print("=" * 60)
    print("  MIHAC v1.0 — Interfaz Web")
    print(f"  Entorno : {config_name}")
    print(f"  URL     : http://localhost:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))
