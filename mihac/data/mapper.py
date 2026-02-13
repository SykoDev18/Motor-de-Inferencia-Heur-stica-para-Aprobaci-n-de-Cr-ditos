# ============================================================
# MIHAC v1.0 — Mapper del German Credit Dataset (UCI)
# data/mapper.py
# ============================================================
# Descarga/lee, decodifica y transforma el German Credit
# Dataset al formato exacto del InferenceEngine de MIHAC.
#
# Fuente: https://archive.ics.uci.edu/dataset/144/
#         statlog+german+credit+data
# Archivo: german.data (1000 registros, 20 atributos + clase)
#
# NOTA SOBRE SESGO:
# La variable A9 (sexo/estado civil) se excluye para evitar
# discriminación por género, en cumplimiento con principios
# de IA ética y normativa de igualdad en servicios financieros.
#
# NOTA SOBRE INGRESOS:
# El dataset NO contiene ingresos directos. Se estiman a
# partir de A8 (tasa de cuota como % del ingreso), A5 (monto)
# y A2 (plazo en meses). Ver docstring de _estimar_ingreso().
# ============================================================

import sys
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _DATA_DIR.parent

# ── Nombres de columnas del german.data ─────────────────────

_COLUMN_NAMES: list[str] = [
    "attr_1",  "attr_2",  "attr_3",  "attr_4",  "attr_5",
    "attr_6",  "attr_7",  "attr_8",  "attr_9",  "attr_10",
    "attr_11", "attr_12", "attr_13", "attr_14", "attr_15",
    "attr_16", "attr_17", "attr_18", "attr_19", "attr_20",
    "clase",
]

# ── Tablas de mapeo ─────────────────────────────────────────

# A1 → base del historial crediticio
_MAP_A1: dict[str, int] = {
    "A11": 0,   # < 0 DM
    "A12": 1,   # 0–200 DM
    "A13": 2,   # >= 200 DM
    "A14": 1,   # sin cuenta → neutro
}

# A3 → ajuste al historial crediticio
_MAP_A3: dict[str, int] = {
    "A30": 0,   # sin créditos previos
    "A31": 1,   # todos pagados
    "A32": 1,   # pagados al día
    "A33": -1,  # mora pasada
    "A34": -2,  # mora crítica
}

# A4 → propósito del crédito
_MAP_A4: dict[str, str] = {
    "A40":  "Consumo",       # auto nuevo
    "A41":  "Consumo",       # auto usado
    "A42":  "Consumo",       # muebles/equipo
    "A43":  "Consumo",       # radio/televisión
    "A44":  "Consumo",       # electrodomésticos
    "A45":  "Emergencia",    # reparaciones
    "A46":  "Educacion",     # educación
    "A47":  "Vacaciones",    # vacaciones
    "A48":  "Educacion",     # reentrenamiento
    "A49":  "Negocio",       # negocios
    "A410": "Consumo",       # otros
}

# A6 → factor de deuda estimado sobre ingreso
_MAP_A6: dict[str, float] = {
    "A61": 0.35,   # < 100 DM (ahorro bajo → deuda alta)
    "A62": 0.20,   # 100–500 DM
    "A63": 0.10,   # 500–1000 DM
    "A64": 0.05,   # >= 1000 DM (buen ahorro → deuda baja)
    "A65": 0.25,   # desconocido → moderado
}

# A7 → antigüedad laboral en años
_MAP_A7: dict[str, int] = {
    "A71": 0,   # desempleado
    "A72": 0,   # < 1 año
    "A73": 2,   # 1–4 años (punto medio)
    "A74": 5,   # 4–7 años
    "A75": 8,   # >= 7 años
}

# A8 → tasa de cuota como % del ingreso
_MAP_A8: dict[int, float] = {
    1: 4.0,
    2: 12.0,
    3: 18.0,
    4: 25.0,
}

# A14 → ajuste adicional de deuda
_MAP_A14: dict[str, float] = {
    "A141": 0.10,   # crédito bancario adicional
    "A142": 0.05,   # crédito en tiendas
    "A143": 0.00,   # ninguno
}

# A15 → tipo de vivienda
_MAP_A15: dict[str, str] = {
    "A151": "Rentada",
    "A152": "Propia",
    "A153": "Familiar",
}

# A18 → número de dependientes
_MAP_A18: dict[str, int] = {
    "A181": 0,   # solo el solicitante
    "A182": 2,   # 2+ personas (estimado conservador)
}

# Factor de conversión DM → MXN (aproximación histórica)
_DM_A_MXN: float = 10.5


class GermanCreditMapper:
    """Transforma el German Credit Dataset al formato MIHAC.

    Lee el archivo german.data (20 atributos codificados +
    clase), decodifica los valores alemanes categóricos y
    produce un DataFrame con las 9 variables de entrada del
    InferenceEngine más la etiqueta real para validación.

    Attributes:
        _df_raw: DataFrame crudo sin transformar.

    Ejemplo de uso::

        mapper = GermanCreditMapper()
        df = mapper.load_and_transform("german.data")
        dicts = mapper.to_mihac_dicts(df)
    """

    def __init__(self) -> None:
        """Inicializa el mapper."""
        self._df_raw: pd.DataFrame | None = None

    # ────────────────────────────────────────────────────────
    # CARGA
    # ────────────────────────────────────────────────────────

    def load(self, filepath: str) -> pd.DataFrame:
        """Lee el archivo german.data crudo.

        El archivo no tiene encabezados y está separado por
        espacios. Se asignan nombres attr_1..attr_20, clase.

        Args:
            filepath: Ruta al archivo german.data.

        Returns:
            DataFrame con 1000 filas y 21 columnas crudas.

        Raises:
            FileNotFoundError: Si el archivo no existe.

        Ejemplo::

            df_raw = mapper.load("data/german.data")
            print(df_raw.shape)  # (1000, 21)
        """
        ruta = Path(filepath)
        if not ruta.exists():
            raise FileNotFoundError(
                f"Archivo no encontrado: {ruta.resolve()}\n"
                f"Descargalo de: https://archive.ics.uci.edu/"
                f"dataset/144/statlog+german+credit+data\n"
                f"Coloca 'german.data' en: {_DATA_DIR}"
            )

        try:
            df = pd.read_csv(
                ruta,
                sep=r"\s+",
                header=None,
                names=_COLUMN_NAMES,
                engine="python",
            )
            logger.info(
                "Cargados %d registros de %s",
                len(df), filepath,
            )
            self._df_raw = df
            return df
        except Exception as e:
            logger.error("Error leyendo %s: %s", filepath, e)
            raise

    def load_from_ucimlrepo(self) -> pd.DataFrame:
        """Descarga el dataset directamente desde la API UCI.

        Alternativa a load() cuando no se tiene el archivo
        local. Requiere la librería ucimlrepo instalada.

        Returns:
            DataFrame crudo con 21 columnas.

        Ejemplo::

            df_raw = mapper.load_from_ucimlrepo()
        """
        try:
            from ucimlrepo import fetch_ucirepo
            dataset = fetch_ucirepo(id=144)
            X = dataset.data.features
            y = dataset.data.targets

            df = X.copy()
            df.columns = _COLUMN_NAMES[:-1]
            target_col = y.columns[0]
            df["clase"] = y[target_col].values
            self._df_raw = df
            logger.info(
                "Descargados %d registros desde UCI",
                len(df),
            )
            return df
        except ImportError:
            logger.error(
                "ucimlrepo no instalado. Ejecutar: "
                "pip install ucimlrepo"
            )
            raise
        except Exception as e:
            logger.error(
                "Error descargando de UCI: %s", e
            )
            raise

    # ────────────────────────────────────────────────────────
    # TRANSFORMACIÓN
    # ────────────────────────────────────────────────────────

    def transform(
        self, df_raw: pd.DataFrame
    ) -> pd.DataFrame:
        """Aplica todos los mapeos al DataFrame crudo.

        Transforma las 20 columnas alemanas codificadas a
        las 9 variables MIHAC + etiqueta real.

        Args:
            df_raw: DataFrame crudo de 21 columnas.

        Returns:
            DataFrame con columnas:
            edad, ingreso_mensual, total_deuda_actual,
            historial_crediticio, antiguedad_laboral,
            numero_dependientes, tipo_vivienda,
            proposito_credito, monto_credito,
            etiqueta_real, etiqueta_binaria

        Ejemplo::

            df = mapper.transform(df_raw)
            print(df.columns.tolist())
        """
        df = pd.DataFrame()

        # ── edad (A13: valor numérico directo) ──
        df["edad"] = df_raw["attr_13"].apply(
            self._mapear_edad
        )

        # ── ingreso_mensual (estimado: A5, A2, A8) ──
        df["ingreso_mensual"] = df_raw.apply(
            self._estimar_ingreso, axis=1
        )

        # ── total_deuda_actual (estimado: A6, A14, ingreso) ──
        df["total_deuda_actual"] = df_raw.apply(
            lambda row: self._estimar_deuda(
                row,
                df.loc[row.name, "ingreso_mensual"]
                if row.name in df.index else 10000.0,
            ),
            axis=1,
        )

        # ── historial_crediticio (A1 + A3) ──
        df["historial_crediticio"] = df_raw.apply(
            self._mapear_historial, axis=1
        )

        # ── antiguedad_laboral (A7) ──
        df["antiguedad_laboral"] = (
            df_raw["attr_7"].map(_MAP_A7).fillna(2).astype(int)
        )

        # ── numero_dependientes (A18) ──
        df["numero_dependientes"] = (
            df_raw["attr_18"]
            .map(_MAP_A18)
            .fillna(1)
            .astype(int)
        )

        # ── tipo_vivienda (A15, reforzado por A12) ──
        df["tipo_vivienda"] = df_raw.apply(
            self._mapear_vivienda, axis=1
        )

        # ── proposito_credito (A4) ──
        df["proposito_credito"] = (
            df_raw["attr_4"]
            .map(_MAP_A4)
            .fillna("Consumo")
        )

        # ── monto_credito (A5 convertido a MXN) ──
        df["monto_credito"] = df_raw["attr_5"].apply(
            self._convertir_monto
        )

        # ── etiqueta (clase) ──
        df["etiqueta_real"] = df_raw["clase"].astype(int)
        df["etiqueta_binaria"] = (
            df["etiqueta_real"].apply(
                lambda x: 1 if x == 1 else 0
            )
        )

        logger.info(
            "Transformación completa: %d registros, "
            "%d columnas",
            len(df), len(df.columns),
        )
        return df

    # ────────────────────────────────────────────────────────
    # FUNCIONES DE MAPEO INDIVIDUALES
    # ────────────────────────────────────────────────────────

    @staticmethod
    def _mapear_edad(valor: Any) -> int:
        """Convierte edad a int clampeado 18–99."""
        try:
            edad = int(valor)
            return max(18, min(99, edad))
        except (ValueError, TypeError):
            return 30  # valor por defecto

    @staticmethod
    def _mapear_historial(row: pd.Series) -> int:
        """Combina A1 (estado cuenta) y A3 (historial).

        Fórmula: raw = base_A1 + ajuste_A3
        Clampeo: <=0 → 0 (Malo), ==1 → 1 (Neutro),
                 >=2 → 2 (Bueno)

        Args:
            row: Fila del DataFrame crudo.

        Returns:
            int: 0, 1 o 2.
        """
        base = _MAP_A1.get(str(row["attr_1"]), 1)
        ajuste = _MAP_A3.get(str(row["attr_3"]), 0)
        raw = base + ajuste
        if raw <= 0:
            return 0
        elif raw == 1:
            return 1
        else:
            return 2

    @staticmethod
    def _estimar_ingreso(row: pd.Series) -> float:
        """Estima el ingreso mensual a partir de A5, A2, A8.

        El dataset NO tiene ingresos directos.  Se estima:
          cuota_mensual = monto_DM / plazo_meses
          ingreso_est = cuota_mensual / (tasa_cuota% / 100)
          ingreso_mxn = ingreso_est * factor_DM_MXN

        A8 codifica la tasa de cuota sobre el ingreso
        disponible:  1→4%, 2→12%, 3→18%, 4→25%.

        JUSTIFICACIÓN PARA LA TESIS:
        Esta estimación es una proxy razonable porque la
        relación cuota/ingreso es linealmente inversible.
        El factor DM→MXN ($10.5) aproxima la equivalencia
        de poder adquisitivo histórica.  Los valores se
        clampean a un mínimo de $3,000 MXN para reflejar
        un salario mínimo viable.

        Args:
            row: Fila del DataFrame crudo.

        Returns:
            float: Ingreso mensual estimado en MXN.
        """
        try:
            monto_dm = float(row["attr_5"])
            plazo = max(1, int(row["attr_2"]))
            tasa_idx = int(row["attr_8"])
            tasa = _MAP_A8.get(tasa_idx, 12.0)

            cuota = monto_dm / plazo
            if tasa <= 0:
                tasa = 12.0

            ingreso_dm = cuota / (tasa / 100.0)
            ingreso_mxn = ingreso_dm * _DM_A_MXN

            return round(max(3000.0, ingreso_mxn), 2)
        except (ValueError, TypeError, ZeroDivisionError):
            return 10000.0  # valor por defecto

    @staticmethod
    def _estimar_deuda(
        row: pd.Series, ingreso: float
    ) -> float:
        """Estima deuda total a partir de A6 y A14.

        A6 (cuenta de ahorros) → factor sobre ingreso.
        A14 (otros planes de pago) → ajuste adicional.

        Args:
            row: Fila del DataFrame crudo.
            ingreso: Ingreso estimado del solicitante.

        Returns:
            float: Deuda total estimada en MXN (>= 0).
        """
        try:
            factor_a6 = _MAP_A6.get(
                str(row["attr_6"]), 0.25
            )
            ajuste_a14 = _MAP_A14.get(
                str(row["attr_14"]), 0.0
            )
            deuda = ingreso * (factor_a6 + ajuste_a14)
            return round(max(0.0, deuda), 2)
        except (ValueError, TypeError):
            return round(ingreso * 0.20, 2)

    @staticmethod
    def _mapear_vivienda(row: pd.Series) -> str:
        """Mapea tipo de vivienda combinando A15 y A12.

        A15 es la fuente principal.
        A12 refuerza: si A12=A121 (inmueble real) y
        A15=A152 → confirmar "Propia".

        Args:
            row: Fila del DataFrame crudo.

        Returns:
            str: "Propia" | "Familiar" | "Rentada"
        """
        vivienda = _MAP_A15.get(
            str(row["attr_15"]), "Rentada"
        )
        # A12=A121 (tiene inmueble) refuerza Propia
        if str(row["attr_12"]) == "A121":
            if vivienda == "Familiar":
                vivienda = "Propia"
        return vivienda

    @staticmethod
    def _convertir_monto(valor_dm: Any) -> float:
        """Convierte monto de DM a MXN y clampea.

        Conversión: DM * 10.5 (aprox. equivalencia).
        Clampeo: 500–50,000 (límites de MIHAC).

        Args:
            valor_dm: Monto en Deutsche Mark.

        Returns:
            float: Monto en MXN entre 500 y 50,000.
        """
        try:
            mxn = float(valor_dm) * _DM_A_MXN
            return round(max(500.0, min(50000.0, mxn)), 2)
        except (ValueError, TypeError):
            return 5000.0

    # ────────────────────────────────────────────────────────
    # VALIDACIÓN
    # ────────────────────────────────────────────────────────

    def validate_output(
        self, df: pd.DataFrame
    ) -> tuple[bool, list[str]]:
        """Verifica coherencia del DataFrame transformado.

        Chequeos:
          - Sin valores nulos
          - Edad 18–99
          - Ingresos > 0
          - Historial en {0, 1, 2}
          - Vivienda en {"Propia", "Familiar", "Rentada"}
          - Propósito en los 5 valores válidos

        Args:
            df: DataFrame transformado.

        Returns:
            (True, []) si OK.
            (False, [lista de problemas]) si hay errores.

        Ejemplo::

            ok, problemas = mapper.validate_output(df)
        """
        problemas: list[str] = []

        # Nulos
        nulos = df.isnull().sum()
        cols_nulas = nulos[nulos > 0]
        if len(cols_nulas) > 0:
            for col, cnt in cols_nulas.items():
                problemas.append(
                    f"Columna '{col}' tiene {cnt} nulos"
                )

        # Edad
        fuera = df[
            (df["edad"] < 18) | (df["edad"] > 99)
        ]
        if len(fuera) > 0:
            problemas.append(
                f"{len(fuera)} registros con edad fuera "
                f"de 18–99"
            )

        # Ingreso
        neg = df[df["ingreso_mensual"] <= 0]
        if len(neg) > 0:
            problemas.append(
                f"{len(neg)} registros con ingreso <= 0"
            )

        # Historial
        invalidos = df[
            ~df["historial_crediticio"].isin([0, 1, 2])
        ]
        if len(invalidos) > 0:
            problemas.append(
                f"{len(invalidos)} registros con historial "
                f"inválido"
            )

        # Vivienda
        validas = {"Propia", "Familiar", "Rentada"}
        inv_viv = df[~df["tipo_vivienda"].isin(validas)]
        if len(inv_viv) > 0:
            problemas.append(
                f"{len(inv_viv)} registros con vivienda "
                f"inválida"
            )

        # Propósito
        props = {
            "Negocio", "Educacion", "Consumo",
            "Emergencia", "Vacaciones",
        }
        inv_prop = df[
            ~df["proposito_credito"].isin(props)
        ]
        if len(inv_prop) > 0:
            problemas.append(
                f"{len(inv_prop)} registros con propósito "
                f"inválido"
            )

        ok = len(problemas) == 0
        if ok:
            logger.info("Validación OK: sin problemas")
        else:
            for p in problemas:
                logger.warning("Validación: %s", p)

        return (ok, problemas)

    # ────────────────────────────────────────────────────────
    # MÉTODOS DE CONVENIENCIA
    # ────────────────────────────────────────────────────────

    def load_and_transform(
        self, filepath: str | None = None
    ) -> pd.DataFrame:
        """Carga, transforma y valida en un solo paso.

        Si filepath es None, intenta descargar desde UCI.
        Si la validación falla, imprime advertencias pero
        retorna el DataFrame de todas formas.

        Args:
            filepath: Ruta a german.data (o None para UCI).

        Returns:
            DataFrame transformado al formato MIHAC.

        Ejemplo::

            df = mapper.load_and_transform("german.data")
        """
        if filepath is not None:
            df_raw = self.load(filepath)
        else:
            df_raw = self.load_from_ucimlrepo()

        df = self.transform(df_raw)

        ok, problemas = self.validate_output(df)
        if not ok:
            for p in problemas:
                print(f"  ⚠ {p}")

        return df

    def to_mihac_dicts(
        self, df: pd.DataFrame
    ) -> list[dict]:
        """Convierte DataFrame a lista de dicts para MIHAC.

        Excluye etiqueta_real y etiqueta_binaria — solo las
        9 variables de entrada del InferenceEngine.

        Args:
            df: DataFrame transformado.

        Returns:
            Lista de dicts listos para engine.evaluate().

        Ejemplo::

            dicts = mapper.to_mihac_dicts(df)
            resultado = engine.evaluate(dicts[0])
        """
        cols_mihac = [
            "edad", "ingreso_mensual", "total_deuda_actual",
            "historial_crediticio", "antiguedad_laboral",
            "numero_dependientes", "tipo_vivienda",
            "proposito_credito", "monto_credito",
        ]
        return df[cols_mihac].to_dict(orient="records")

    def split(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Divide en train/test con estratificación.

        Mantiene la proporción de etiquetas (70/30) en
        ambos conjuntos.

        Args:
            df: DataFrame transformado.
            test_size: Proporción para test (default 0.2).
            random_state: Semilla de aleatoriedad.

        Returns:
            (df_train, df_test)

        Ejemplo::

            train, test = mapper.split(df)
            print(len(train), len(test))  # 800, 200
        """
        from sklearn.model_selection import train_test_split
        return train_test_split(
            df,
            test_size=test_size,
            random_state=random_state,
            stratify=df["etiqueta_real"],
        )


# ────────────────────────────────────────────────────────────
# FUNCIÓN AUXILIAR: Resumen del dataset
# ────────────────────────────────────────────────────────────

def get_dataset_summary(df: pd.DataFrame) -> dict:
    """Resumen estadístico del dataset transformado.

    Args:
        df: DataFrame transformado con etiquetas.

    Returns:
        Dict con métricas clave del dataset.

    Ejemplo::

        resumen = get_dataset_summary(df)
        print(resumen["tasa_morosidad_real"])
    """
    total = len(df)
    buenos = int((df["etiqueta_real"] == 1).sum())
    malos = int((df["etiqueta_real"] == 2).sum())

    dti_estimado = (
        df["total_deuda_actual"] / df["ingreso_mensual"]
    )

    return {
        "total_registros": total,
        "buenos_pagadores": buenos,
        "malos_pagadores": malos,
        "tasa_morosidad_real": round(malos / total, 4),
        "edad_promedio": round(
            df["edad"].mean(), 1
        ),
        "ingreso_promedio_estimado": round(
            df["ingreso_mensual"].mean(), 2
        ),
        "dti_promedio_estimado": round(
            dti_estimado.mean(), 4
        ),
        "distribucion_proposito": (
            df["proposito_credito"]
            .value_counts()
            .to_dict()
        ),
        "distribucion_vivienda": (
            df["tipo_vivienda"]
            .value_counts()
            .to_dict()
        ),
        "distribucion_historial": (
            df["historial_crediticio"]
            .value_counts()
            .to_dict()
        ),
    }


# ────────────────────────────────────────────────────────────
# DATOS MOCK (fallback cuando german.data no disponible)
# ────────────────────────────────────────────────────────────

def _generate_mock_raw(n: int = 10) -> pd.DataFrame:
    """Genera datos crudos mock del formato german.data.

    Útil para tests cuando el archivo real no está disponible.

    Args:
        n: Número de filas mock a generar.

    Returns:
        DataFrame con 21 columnas en formato german.data.
    """
    np.random.seed(42)
    mock_data = {
        "attr_1":  np.random.choice(
            ["A11", "A12", "A13", "A14"], n),
        "attr_2":  np.random.randint(6, 48, n),
        "attr_3":  np.random.choice(
            ["A30", "A31", "A32", "A33", "A34"], n),
        "attr_4":  np.random.choice(
            ["A40", "A41", "A42", "A43", "A46",
             "A49"], n),
        "attr_5":  np.random.randint(500, 10000, n),
        "attr_6":  np.random.choice(
            ["A61", "A62", "A63", "A64", "A65"], n),
        "attr_7":  np.random.choice(
            ["A71", "A72", "A73", "A74", "A75"], n),
        "attr_8":  np.random.randint(1, 5, n),
        "attr_9":  np.random.choice(
            ["A91", "A92", "A93", "A94"], n),
        "attr_10": np.random.choice(
            ["A101", "A102", "A103"], n),
        "attr_11": np.random.randint(1, 5, n),
        "attr_12": np.random.choice(
            ["A121", "A122", "A123", "A124"], n),
        "attr_13": np.random.randint(20, 65, n),
        "attr_14": np.random.choice(
            ["A141", "A142", "A143"], n),
        "attr_15": np.random.choice(
            ["A151", "A152", "A153"], n),
        "attr_16": np.random.randint(1, 4, n),
        "attr_17": np.random.choice(
            ["A171", "A172", "A173", "A174"], n),
        "attr_18": np.random.choice(
            ["A181", "A182"], n),
        "attr_19": np.random.choice(
            ["A191", "A192"], n),
        "attr_20": np.random.choice(
            ["A201", "A202"], n),
        "clase":   np.random.choice([1, 2], n,
                                     p=[0.7, 0.3]),
    }
    return pd.DataFrame(mock_data)


# ════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("MIHAC — Tests del German Credit Mapper")
    print("=" * 60)

    mapper = GermanCreditMapper()

    # Test 1: Archivo inexistente
    print("\n── Test 1: Archivo inexistente ──")
    try:
        mapper.load("archivo_que_no_existe.data")
        print("  ✗ FAIL: no lanzó excepción")
    except FileNotFoundError as e:
        print(f"  ✓ PASS: {str(e)[:80]}...")

    # Test 2: Intentar cargar el dataset real
    german_path = _DATA_DIR / "german.data"
    usar_mock = not german_path.exists()

    if usar_mock:
        print("\n── Test 2: Usando datos MOCK (german.data "
              "no disponible) ──")
        df_raw = _generate_mock_raw(20)
        print(f"  Generados {len(df_raw)} registros mock")
    else:
        print("\n── Test 2: Cargando german.data real ──")
        df_raw = mapper.load(str(german_path))
        print(f"  Cargados {len(df_raw)} registros")

    # Test 3: Transformar
    print("\n── Test 3: Transformación ──")
    df = mapper.transform(df_raw)
    print(f"  Shape: {df.shape}")
    print(f"  Columnas: {df.columns.tolist()}")
    print(f"\n  Primeras 3 filas:")
    print(df.head(3).to_string(index=False))

    # Test 4: Validación
    print("\n── Test 4: Validación ──")
    ok, problemas = mapper.validate_output(df)
    print(f"  Válido: {ok}")
    if problemas:
        for p in problemas:
            print(f"  ⚠ {p}")
    else:
        print("  ✓ Sin problemas")

    # Test 5: Resumen
    print("\n── Test 5: Resumen del dataset ──")
    resumen = get_dataset_summary(df)
    for k, v in resumen.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")

    # Test 6: to_mihac_dicts
    print("\n── Test 6: Conversión a dicts MIHAC ──")
    dicts = mapper.to_mihac_dicts(df)
    print(f"  Total dicts: {len(dicts)}")
    print(f"  Primer dict:")
    for k, v in dicts[0].items():
        print(f"    {k}: {v}")

    claves_esperadas = {
        "edad", "ingreso_mensual", "total_deuda_actual",
        "historial_crediticio", "antiguedad_laboral",
        "numero_dependientes", "tipo_vivienda",
        "proposito_credito", "monto_credito",
    }
    assert set(dicts[0].keys()) == claves_esperadas, (
        "FAIL: claves incorrectas"
    )
    print("  ✓ Claves correctas")

    print(f"\n{'='*60}")
    print("TODOS LOS TESTS DEL MAPPER PASARON ✓")
    print(f"{'='*60}")
