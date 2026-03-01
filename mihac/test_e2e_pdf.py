"""Test E2E: Entregable 1 Semana 9 — Generador de reportes PDF."""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app, db
from app.models import Evaluacion

app = create_app("development")
client = app.test_client()


def submit_eval(overrides=None):
    """Submit an evaluation via POST and return the eval ID."""
    r = client.get("/")
    html = r.data.decode()
    m = re.search(r'name="csrf_token".*?value="(.+?)"', html)
    csrf = m.group(1)
    data = {
        "csrf_token": csrf,
        "edad": "35", "ingreso_mensual": "25000",
        "total_deuda_actual": "3000", "historial_crediticio": "2",
        "antiguedad_laboral": "8", "numero_dependientes": "1",
        "tipo_vivienda": "Propia", "proposito_credito": "Negocio",
        "monto_credito": "15000",
    }
    if overrides:
        data.update(overrides)
    resp = client.post("/", data=data, follow_redirects=False)
    # Extract eval ID from redirect Location header
    loc = resp.headers.get("Location", "")
    m2 = re.search(r"/resultado/(\d+)", loc)
    if m2:
        return int(m2.group(1))
    # If follow_redirects was True, parse from HTML
    return None


# ── Submit 3 profiles: APROBADO, RECHAZADO, REVISION_MANUAL ──
print("1. Submitting 3 profiles...")

id_aprobado = submit_eval()
assert id_aprobado is not None, "Failed to submit APROBADO"
print(f"   APROBADO: eval #{id_aprobado}")

id_rechazado = submit_eval({
    "historial_crediticio": "0",
    "ingreso_mensual": "7000",
    "total_deuda_actual": "5000",
    "antiguedad_laboral": "0",
    "numero_dependientes": "4",
    "tipo_vivienda": "Rentada",
    "proposito_credito": "Vacaciones",
    "monto_credito": "20000",
    "edad": "20",
})
assert id_rechazado is not None, "Failed to submit RECHAZADO"
print(f"   RECHAZADO: eval #{id_rechazado}")

id_revision = submit_eval({
    "historial_crediticio": "1",
    "ingreso_mensual": "15000",
    "total_deuda_actual": "3000",
    "antiguedad_laboral": "2",
    "numero_dependientes": "1",
    "tipo_vivienda": "Familiar",
    "proposito_credito": "Consumo",
    "monto_credito": "10000",
    "edad": "28",
})
assert id_revision is not None, "Failed to submit REVISION"
print(f"   REVISION: eval #{id_revision}")


# ── Test 2: PDF completo APROBADO ──
print("\n2. PDF completo (APROBADO)...")
resp = client.get(f"/resultado/{id_aprobado}/pdf")
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
assert resp.content_type == "application/pdf", f"Got {resp.content_type}"
assert len(resp.data) > 5000, f"PDF too small: {len(resp.data)} bytes"
assert resp.data[:5] == b"%PDF-", "Not a valid PDF"
print(f"   OK: {len(resp.data)} bytes, valid PDF header")

# ── Test 3: PDF completo RECHAZADO ──
print("3. PDF completo (RECHAZADO)...")
resp = client.get(f"/resultado/{id_rechazado}/pdf")
assert resp.status_code == 200
assert resp.data[:5] == b"%PDF-"
print(f"   OK: {len(resp.data)} bytes")

# ── Test 4: PDF cliente REVISION_MANUAL ──
print("4. PDF cliente (REVISION_MANUAL)...")
resp = client.get(f"/resultado/{id_revision}/pdf-cliente")
assert resp.status_code == 200
assert resp.data[:5] == b"%PDF-"
print(f"   OK: {len(resp.data)} bytes")

# ── Test 5: PDF cliente APROBADO ──
print("5. PDF cliente (APROBADO)...")
resp = client.get(f"/resultado/{id_aprobado}/pdf-cliente")
assert resp.status_code == 200
assert resp.data[:5] == b"%PDF-"
print(f"   OK: {len(resp.data)} bytes")

# ── Test 6: PDF completo REVISION_MANUAL ──
print("6. PDF completo (REVISION_MANUAL)...")
resp = client.get(f"/resultado/{id_revision}/pdf")
assert resp.status_code == 200
assert resp.data[:5] == b"%PDF-"
print(f"   OK: {len(resp.data)} bytes")

# ── Test 7: PDF for nonexistent eval → 404 ──
print("7. PDF de evaluacion inexistente → 404...")
resp = client.get("/resultado/99999/pdf")
assert resp.status_code == 404
print("   OK: 404 returned")

# ── Test 8: Verify exports directory has files ──
print("8. Verificar archivos en reports/exports/...")
exports_dir = Path(__file__).resolve().parent / "reports" / "exports"
pdf_files = list(exports_dir.glob("*.pdf"))
assert len(pdf_files) >= 3, f"Expected >=3 PDFs, got {len(pdf_files)}"
print(f"   OK: {len(pdf_files)} PDFs en exports/")
for f in pdf_files:
    size = f.stat().st_size
    print(f"      {f.name}: {size:,} bytes")

# ── Test 9: Download buttons in resultado page ──
print("9. Botones de descarga en resultado.html...")
resp = client.get(f"/resultado/{id_aprobado}")
html = resp.data.decode()
assert "pdf" in html.lower() and "PDF Completo" in html
assert "pdf-cliente" in html and "PDF Cliente" in html
print("   OK: download buttons present")

# ── Test 10: Standalone generator test ──
print("10. Test generador standalone (batch)...")
from reports.pdf_report import PDFReportGenerator
gen = PDFReportGenerator()

with app.app_context():
    evals = Evaluacion.query.order_by(Evaluacion.id.desc()).limit(3).all()
    datos_list = [e.to_dict() for e in evals]

batch_dir = exports_dir / "batch_test"
rutas = gen.batch_generate(datos_list, batch_dir, "cliente")
assert len(rutas) == 3, f"Expected 3, got {len(rutas)}"
print(f"   OK: batch generated {len(rutas)} client PDFs")

# Clean batch test
import shutil
shutil.rmtree(batch_dir, ignore_errors=True)

print("\n" + "=" * 55)
print("  ENTREGABLE 1 E2E: ALL TESTS PASSED")
print("=" * 55)
