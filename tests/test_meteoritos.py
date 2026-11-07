
import csv

from scripts.validar_datos import (
    COLUMNAS,
    validar_archivo,
    obtener_anio
)
from scripts.analizar_datos import calcular_indicadores


def fila_valida(identificador="1", **cambios):
    fila = {
        "id": identificador,
        "name": "Meteorito de prueba",
        "recclass": "L6",
        "mass (g)": "100",
        "fall": "Fell",
        "year": "2000-01-01T00:00:00.000",
        "reclat": "-17.4",
        "reclong": "-66.2"
    }
    fila.update(cambios)
    return fila


def crear_csv(tmp_path, filas):
    ruta = tmp_path / "prueba.csv"

    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS)
        escritor.writeheader()
        escritor.writerows(filas)

    return ruta


def contiene_error(errores, campo):
    return any(campo in error for error in errores)


# 1. Registro válido
def test_registro_valido(tmp_path):
    ruta = crear_csv(tmp_path, [fila_valida()])
    total, errores = validar_archivo(ruta)

    assert total == 1
    assert errores == []


# 2. Indicadores con valores conocidos
def test_calculo_indicadores():
    registros = [
        fila_valida("1", **{"mass (g)": "100"}),
        fila_valida("2", fall="Found",
                    **{"mass (g)": "300"}),
        fila_valida("3", **{"mass (g)": ""})
    ]

    resultado = calcular_indicadores(registros)

    assert resultado["total"] == 3
    assert resultado["fell"] == 2
    assert resultado["found"] == 1
    assert resultado["masa_media"] == 200
    assert resultado["sin_masa"] == 1


# 3. Faltantes opcionales y coordenadas cero
def test_campos_faltantes(tmp_path):
    fila = fila_valida(
        **{
            "mass (g)": "",
            "year": "",
            "reclat": "0",
            "reclong": "0"
        }
    )
    ruta = crear_csv(tmp_path, [fila])

    _, errores = validar_archivo(ruta)
    assert errores == []


# 4. Masa negativa
def test_masa_negativa(tmp_path):
    fila = fila_valida(**{"mass (g)": "-500"})
    ruta = crear_csv(tmp_path, [fila])

    _, errores = validar_archivo(ruta)
    assert contiene_error(errores, "mass (g)")


# 5. Latitud fuera de rango
def test_latitud_invalida(tmp_path):
    ruta = crear_csv(
        tmp_path,
        [fila_valida(reclat="95")]
    )
    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "reclat")


# 6. Longitud fuera de rango
def test_longitud_invalida(tmp_path):
    ruta = crear_csv(
        tmp_path,
        [fila_valida(reclong="-200")]
    )
    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "reclong")


# 7. Identificador duplicado
def test_id_duplicado(tmp_path):
    ruta = crear_csv(
        tmp_path,
        [fila_valida("1"), fila_valida("1")]
    )
    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "duplicado")


# 8. Nombre vacío
def test_nombre_vacio(tmp_path):
    ruta = crear_csv(
        tmp_path,
        [fila_valida(name="   ")]
    )
    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "name")


# 9. Clasificación vacía
def test_clasificacion_vacia(tmp_path):
    ruta = crear_csv(
        tmp_path,
        [fila_valida(recclass="")]
    )
    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "recclass")


# 10. Valor Fell/Found incorrecto
def test_fall_invalido(tmp_path):
    ruta = crear_csv(
        tmp_path,
        [fila_valida(fall="Unknown")]
    )
    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "fall")


# 11. Fecha completa válida
def test_fecha_completa():
    anio = obtener_anio("1880-01-01T00:00:00.000")
    assert anio == 1880


# 12. Año fuera de rango
def test_anio_invalido(tmp_path):
    ruta = crear_csv(
        tmp_path,
        [fila_valida(year="2027-01-01")]
    )
    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "year")


# 13. Número incorrecto de campos
def test_estructura_invalida(tmp_path):
    ruta = tmp_path / "estructura.csv"

    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(COLUMNAS)
        escritor.writerow(
            ["1", "Prueba", "L6", "100", "Fell",
             "2000", "0", "0", "CAMPO_EXTRA"]
        )

    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "estructura")


# 14. Registro incorrecto añadido al final
def test_validacion_ultima_fila(tmp_path):
    filas = [
        fila_valida("1"),
        fila_valida("2"),
        fila_valida("3", **{"mass (g)": "-10"})
    ]
    ruta = crear_csv(tmp_path, filas)

    total, errores = validar_archivo(ruta)

    assert total == 3
    assert any(
        "Fila 4" in error and "mass (g)" in error
        for error in errores
    )


# 15. Masa no finita
def test_masa_nan(tmp_path):
    ruta = crear_csv(
        tmp_path,
        [fila_valida(**{"mass (g)": "NaN"})]
    )
    _, errores = validar_archivo(ruta)

    assert contiene_error(errores, "no es finito")


from scripts.generar_sitio import crear_html


# 16. El HTML contiene indicadores calculados y commit.
def test_generacion_html():
    registros = [
        fila_valida("1", name="Meteorito de ejemplo"),
        fila_valida("2", fall="Found")
    ]

    indicadores = calcular_indicadores(registros)
    html = crear_html(indicadores, "abc123")

    assert "Meteorite Observatory" in html
    assert "Meteorito de ejemplo" in html
    assert "abc123" in html
    assert "Masa media" in html


# 17. El contenido del CSV no debe ejecutar HTML.
def test_html_escapa_contenido():
    registro = fila_valida(
        "1",
        name="<script>alert(1)</script>"
    )

    indicadores = calcular_indicadores([registro])
    html = crear_html(indicadores)

    assert "&lt;script&gt;" in html
    assert "<script>alert(1)</script>" not in html
