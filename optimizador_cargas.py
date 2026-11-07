#!/usr/bin/env python3
"""
Optimizador de asignación de cargas a líneas transportistas.

Lee las tarifas y calificaciones desde Tarifas.xlsx y, con base en las cargas
que captura el usuario (ruta, tipo IMPO / EXPO / TOURING y cantidad) y las
unidades disponibles de cada línea, recomienda la asignación que minimiza el
costo y maximiza la calificación de la línea transportista.

Uso:
    python optimizador_cargas.py                 # usa Tarifas.xlsx junto al script
    python optimizador_cargas.py ruta/Tarifas.xlsx

Requiere: openpyxl  (pip install openpyxl)
"""

import os
import re
import sys
import unicodedata

try:
    import openpyxl
except ImportError:
    sys.exit("Falta la librería openpyxl. Instálala con:  pip install openpyxl")


TIPOS = {"1": "IMPO", "2": "EXPO", "3": "TOURING"}
# Peso del costo en la eficiencia (0.5 = 50% costo, 50% calificación)
PESO_COSTO = 0.5
PLAZA_CLAVE_CALIF = {"SAN LUIS POTOSI": "SLP", "MONTERREY": "SAVI"}  # Max trucking SLP / SAVI


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
def sin_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def norm(texto):
    """Normaliza nombres: mayúsculas, sin acentos, sin espacios alrededor de '-'."""
    t = sin_acentos(str(texto)).upper().strip()
    t = re.sub(r"\s*-\s*", "-", t)
    return re.sub(r"\s+", " ", t)


def a_numero(valor):
    if isinstance(valor, (int, float)):
        return float(valor)
    return None  # "NA", vacío, texto


def numero_en_texto(texto):
    m = re.search(r"\d+(?:\.\d+)?", str(texto))
    return float(m.group()) if m else None


def money(x):
    return f"${x:,.2f}"


# --------------------------------------------------------------------------- #
# Lectura del Excel
# --------------------------------------------------------------------------- #
def leer_tarifas(ruta_excel):
    """
    Devuelve:
      tarifas: {plaza: {linea: {ruta_norm: {...}}}}
      calificaciones: {nombre_norm: calificacion}
      nombres_ruta: {ruta_norm: nombre como aparece en el Excel}
    """
    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    ws = wb.worksheets[0]
    filas = [list(r) for r in ws.iter_rows(values_only=True)]

    # --- Calificaciones: cualquier celda con formato "NOMBRE - número" ---
    calificaciones = {}
    for fila in filas:
        for celda in fila:
            if isinstance(celda, str):
                m = re.match(r"^\s*(.+?)\s*-\s*(\d+(?:\.\d+)?)\s*$", celda)
                if m and not re.search(r"\d", m.group(1)):
                    calificaciones[norm(m.group(1))] = float(m.group(2))

    # --- Tarifas por plaza / línea ---
    tarifas, nombres_ruta = {}, {}
    plaza = None
    lineas = []          # líneas a las que aplica la tabla actual
    hubo_filas = True    # si ya se leyeron tarifas desde el último encabezado
    plazas_conocidas = {"SAN LUIS POTOSI", "MONTERREY"}

    for i, fila in enumerate(filas):
        a = fila[0] if fila else None
        if a is None or not isinstance(a, str):
            continue
        a_n = norm(a)
        resto_vacio = all(v is None for v in fila[1:6])

        if a_n.startswith("TARIFAS"):
            continue
        if a_n in plazas_conocidas and resto_vacio:
            plaza = a_n
            lineas, hubo_filas = [], True
            tarifas.setdefault(plaza, {})
            continue
        if a_n == "CLIENTE":
            continue
        if resto_vacio:  # encabezado de línea transportista
            # Encabezados seguidos sin tarifas entre ellos comparten la misma tabla
            # (p. ej. MAX TRUCKING / SMART LOGISTICS / LEADS en Monterrey).
            lineas = [a_n] if hubo_filas else lineas + [a_n]
            hubo_filas = False
            tarifas.setdefault(plaza, {}).setdefault(a_n, {})
            continue

        # Fila de tarifa
        impo, expo, completa = (a_numero(v) for v in fila[1:4])
        acc_expo = fila[4] if len(fila) > 4 else None
        acc_impo = fila[5] if len(fila) > 5 else None
        ruta = a_n
        nombres_ruta.setdefault(ruta, ruta)
        hubo_filas = True
        for linea in lineas:
            tarifas[plaza][linea][ruta] = {
                "IMPO": impo, "EXPO": expo, "COMPLETA": completa,
                "ACC_EXPO": str(acc_expo).strip() if acc_expo else None,
                "ACC_IMPO": str(acc_impo).strip() if acc_impo else None,
            }

    return tarifas, calificaciones, nombres_ruta


def calificacion_de(linea, plaza, calificaciones):
    if linea in calificaciones:
        return calificaciones[linea]
    clave = PLAZA_CLAVE_CALIF.get(plaza, "")
    candidatos = [k for k in calificaciones if k.startswith(linea)]
    for k in candidatos:
        if clave and clave in k:
            return calificaciones[k]
    return calificaciones[candidatos[0]] if candidatos else None


# --------------------------------------------------------------------------- #
# Cálculo de costo (los accesoriales se incluyen SIEMPRE que la ruta los tenga)
# --------------------------------------------------------------------------- #
def costo_carga(tarifa, tipo, hazmat):
    """Costo de UNA carga y notas aplicadas. None si la línea no cotiza."""
    notas = []
    impo, expo, completa = tarifa["IMPO"], tarifa["EXPO"], tarifa["COMPLETA"]
    base = {"IMPO": impo, "EXPO": expo, "TOURING": completa}[tipo]

    if base is None:
        if completa is None:
            return None, notas
        base = completa
        notas.append("tarifa completa")

    costo = base
    usa_expo = tipo in ("EXPO", "TOURING")
    usa_impo = tipo in ("IMPO", "TOURING")

    acc = tarifa["ACC_EXPO"]
    if acc and usa_expo:
        val = numero_en_texto(acc)
        if val:
            costo += val
            notas.append(f"+{acc}")

    acc = tarifa["ACC_IMPO"]
    if acc:
        val = numero_en_texto(acc)
        if "HAZMAT" in norm(acc):
            if hazmat and val:
                costo = val  # la tarifa HAZMAT sustituye a la tarifa normal
                notas.append("tarifa HAZMAT")
        elif val and usa_impo:
            costo += val
            notas.append(f"+{acc}")

    return costo, notas


# --------------------------------------------------------------------------- #
# Eficiencia (calificación vs. costo)
# --------------------------------------------------------------------------- #
def calcular_eficiencia(opciones, peso_costo=None):
    """
    Índice de eficiencia 0-100 (mayor = mejor) entre las líneas disponibles:
      PESO_COSTO       * (costo más bajo / costo de la línea)
    + (1 - PESO_COSTO) * (calificación de la línea / 5)
    """
    peso = PESO_COSTO if peso_costo is None else peso_costo
    cmin = min(o["costo"] for o in opciones.values())
    for o in opciones.values():
        o["eficiencia"] = 100 * (peso * cmin / o["costo"]
                                 + (1 - peso) * o["calif"] / 5)


def asignar(carga):
    """Reparte las cargas empezando por la línea más eficiente, hasta su capacidad."""
    pendientes, asignacion = carga["cantidad"], []
    orden = sorted(carga["opciones"].items(),
                   key=lambda x: (-x[1]["eficiencia"], x[1]["costo"]))
    for linea, o in orden:
        if pendientes == 0:
            break
        q = pendientes if o["capacidad"] is None else min(o["capacidad"], pendientes)
        if q > 0:
            asignacion.append((linea, q))
            pendientes -= q
    return orden, asignacion, pendientes


# --------------------------------------------------------------------------- #
# Entrada de datos
# --------------------------------------------------------------------------- #
def pedir_opcion(msg, opciones):
    while True:
        r = input(msg).strip()
        if r in opciones:
            return r
        print(f"  Opción no válida. Elige: {', '.join(opciones)}")


_NADA = object()


def pedir_entero(msg, minimo=0, vacio=_NADA):
    while True:
        r = input(msg).strip()
        if r == "" and vacio is not _NADA:
            return vacio
        if r.isdigit() and int(r) >= minimo:
            return int(r)
        print(f"  Escribe un número entero mayor o igual a {minimo}.")


def pedir_varios(msg, n):
    """Lee una lista de números separados por coma, p. ej. '1,3'."""
    while True:
        partes = [x for x in re.split(r"[,\s]+", input(msg).strip()) if x]
        if partes and all(x.isdigit() and 1 <= int(x) <= n for x in partes):
            return sorted({int(x) for x in partes})
        print(f"  Escribe uno o varios números entre 1 y {n}, separados por coma (ej. 1,3).")


def si_no(msg):
    return input(msg + " [s/N]: ").strip().lower() in ("s", "si", "sí", "y", "yes")


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    ruta_excel = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "Tarifas.xlsx")
    if not os.path.exists(ruta_excel):
        sys.exit(f"No se encontró el archivo de tarifas: {ruta_excel}")

    tarifas, calificaciones, nombres_ruta = leer_tarifas(ruta_excel)

    print("=" * 72)
    print("   OPTIMIZADOR DE CARGAS - LÍNEAS TRANSPORTISTAS")
    print("=" * 72)

    # 1) Plaza
    plazas = list(tarifas)
    print("\nPlazas disponibles:")
    for i, p in enumerate(plazas, 1):
        print(f"  {i}. {p}")
    plaza = plazas[int(pedir_opcion("Elige la plaza: ",
                                    [str(i) for i in range(1, len(plazas) + 1)])) - 1]

    lineas_plaza = {l: r for l, r in tarifas[plaza].items() if r}
    rutas = sorted({ruta for r in lineas_plaza.values() for ruta in r})
    calif = {}
    for l in lineas_plaza:
        k = calificacion_de(l, plaza, calificaciones)
        if k is None:
            print(f"  Aviso: {l} no tiene calificación en el Excel; se toma 0.")
            k = 0.0
        calif[l] = k

    # 2) Cargas
    n = pedir_entero("\n¿Cuántas cargas (rutas distintas) vas a capturar? ", minimo=1)
    cargas = []
    for k in range(1, n + 1):
        print(f"\n--- Carga {k} de {n} ---")
        for i, r in enumerate(rutas, 1):
            print(f"  {i:>2}. {nombres_ruta[r]}")
        ruta = rutas[int(pedir_opcion("Ruta / cliente: ",
                                      [str(i) for i in range(1, len(rutas) + 1)])) - 1]
        tipo = TIPOS[pedir_opcion("Tipo: 1) IMPO  2) EXPO  3) AMBOS (TOURING): ",
                                  list(TIPOS))]
        cantidad = pedir_entero("¿Cuántas cargas tienes disponibles? ", 1)

        hazmat = False
        if any(t.get(ruta) and t[ruta]["ACC_IMPO"] and "HAZMAT" in norm(t[ruta]["ACC_IMPO"])
               for t in lineas_plaza.values()):
            hazmat = si_no("¿La carga es HAZMAT?")

        # Líneas que cotizan esta ruta y tipo
        cotizan = {}
        for l, rts in lineas_plaza.items():
            if ruta in rts:
                costo, notas = costo_carga(rts[ruta], tipo, hazmat)
                if costo is not None:
                    cotizan[l] = {"costo": costo, "calif": calif[l], "notas": notas}
        if not cotizan:
            print("  Ninguna línea cotiza esta ruta/tipo; se omite.")
            continue

        # ¿De qué líneas tiene disponibles las cargas?
        nombres = list(cotizan)
        print("¿Qué líneas transportistas tienes disponibles para esta carga?")
        for i, l in enumerate(nombres, 1):
            print(f"  {i}. {l}")
        elegidas = [nombres[i - 1] for i in
                    pedir_varios("Escribe los números separados por coma (ej. 1,3): ",
                                 len(nombres))]

        opciones = {}
        for l in elegidas:
            if len(elegidas) == 1:
                cap = None
            else:
                cap = pedir_entero(f"  ¿Cuántas de las {cantidad} cargas puede llevar {l}? "
                                   f"(Enter = todas): ", 0, vacio=None)
            opciones[l] = dict(cotizan[l], capacidad=cap)
        calcular_eficiencia(opciones)
        cargas.append({"ruta": ruta, "tipo": tipo, "cantidad": cantidad,
                       "opciones": opciones})

    if not cargas:
        sys.exit("No hay cargas válidas para evaluar.")

    # 3) Comparativo por carga
    print("\n" + "=" * 72)
    print(f"   COMPARATIVO  (eficiencia: {PESO_COSTO:.0%} costo / "
          f"{1 - PESO_COSTO:.0%} calificación)")
    print("=" * 72)
    resultados = []
    for c in cargas:
        orden, asignacion, pendientes = asignar(c)
        resultados.append((c, asignacion, pendientes))
        print(f"\n{nombres_ruta[c['ruta']]}  |  {c['tipo']}  |  {c['cantidad']} carga(s)")
        print(f"  {'Línea':<18}{'Costo/carga':>13}{'Calif.':>8}{'Eficiencia':>12}  Accesoriales")
        for l, o in orden:
            print(f"  {l:<18}{money(o['costo']):>13}{o['calif']:>8.1f}"
                  f"{o['eficiencia']:>11.1f}%  {', '.join(o['notas'])}")

    # 4) Recomendación final
    print("\n" + "=" * 72)
    print("   RECOMENDACIÓN FINAL (mejor eficiencia calificación / costo)")
    print("=" * 72)
    print(f"{'Ruta':<24}{'Tipo':<9}{'Cargas':>6}  {'Línea':<16}{'Costo total':>13}{'Calif.':>7}")
    costo_total = suma_calif = total_asig = sin_asig = 0
    for c, asignacion, pendientes in resultados:
        for l, q in asignacion:
            o = c["opciones"][l]
            print(f"{nombres_ruta[c['ruta']][:23]:<24}{c['tipo']:<9}{q:>6}  {l:<16}"
                  f"{money(q * o['costo']):>13}{o['calif']:>7.1f}")
            costo_total += q * o["costo"]
            suma_calif += q * o["calif"]
            total_asig += q
        if pendientes:
            print(f"{nombres_ruta[c['ruta']][:23]:<24}{c['tipo']:<9}{pendientes:>6}  "
                  f"SIN LÍNEA DISPONIBLE")
            sin_asig += pendientes
    print("-" * 72)
    print(f"Cargas asignadas:       {total_asig}")
    if sin_asig:
        print(f"Cargas sin asignar:     {sin_asig}  (las líneas elegidas no alcanzan)")
    print(f"Costo total:            {money(costo_total)}")
    if total_asig:
        print(f"Calificación promedio:  {suma_calif / total_asig:.2f}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProceso cancelado.")
