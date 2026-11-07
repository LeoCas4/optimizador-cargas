#!/usr/bin/env python3
"""
Interfaz web del Optimizador de Cargas.

Uso:
    py app_web.py                      (Windows)
    python3 app_web.py                 (Mac / Linux)
    py app_web.py ruta\\Tarifas.xlsx    (otro archivo de tarifas)

Abre el navegador en http://localhost:8000
No necesita librerías extra además de openpyxl.
"""

import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import optimizador_cargas as oc

BASE = os.path.dirname(os.path.abspath(__file__))
_ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
EXCEL = _ARGS[0] if _ARGS else os.path.join(BASE, "Tarifas.xlsx")
PORT = int(os.environ.get("PORT", "8000"))
INDEX = os.path.join(BASE, "web", "index.html")
ESTATICOS = {"logo.png": "image/png"}  # archivos de la carpeta web que se pueden servir


def construir_datos():
    """Lee el Excel (en cada llamada, así los cambios se ven al recargar)."""
    tarifas, calificaciones, nombres = oc.leer_tarifas(EXCEL)
    plazas = {}
    for plaza, lineas in tarifas.items():
        con_tarifa = {l: r for l, r in lineas.items() if r}
        calif = {l: (oc.calificacion_de(l, plaza, calificaciones) or 0.0) for l in con_tarifa}
        rutas = sorted({r for t in con_tarifa.values() for r in t})
        info_rutas = {}
        for ruta in rutas:
            hazmat = any(t.get(ruta) and t[ruta]["ACC_IMPO"]
                         and "HAZMAT" in oc.norm(t[ruta]["ACC_IMPO"])
                         for t in con_tarifa.values())
            cot = {}
            for tipo in oc.TIPOS.values():
                for h in ([False, True] if hazmat else [False]):
                    lista = []
                    for l, t in con_tarifa.items():
                        if ruta in t:
                            costo, notas = oc.costo_carga(t[ruta], tipo, h)
                            if costo is not None:
                                lista.append({"linea": l, "costo": costo,
                                              "calif": calif[l], "notas": notas})
                    cot[f"{tipo}|{int(h)}"] = lista
            info_rutas[ruta] = {"nombre": nombres.get(ruta, ruta),
                                "hazmat": hazmat, "cotizaciones": cot}
        plazas[plaza] = {
            "lineas": sorted(({"nombre": l, "calif": c} for l, c in calif.items()),
                             key=lambda x: -x["calif"]),
            "rutas": info_rutas,
        }
    return {"plazas": plazas, "peso_costo": oc.PESO_COSTO,
            "archivo": os.path.basename(EXCEL)}


def optimizar(payload):
    datos = construir_datos()
    plaza = datos["plazas"].get(payload.get("plaza"))
    if not plaza:
        raise ValueError("Plaza no válida.")
    peso = float(payload.get("peso_costo", oc.PESO_COSTO))
    peso = min(max(peso, 0.0), 1.0)

    resultados, costo_total, suma_calif, asignadas, sin_asignar = [], 0.0, 0.0, 0, 0
    for i, c in enumerate(payload.get("cargas", []), 1):
        ruta = plaza["rutas"].get(c.get("ruta"))
        if not ruta:
            raise ValueError(f"Carga {i}: elige una ruta.")
        tipo = c.get("tipo")
        if tipo not in oc.TIPOS.values():
            raise ValueError(f"Carga {i}: tipo no válido.")
        cantidad = int(c.get("cantidad") or 0)
        if cantidad < 1:
            raise ValueError(f"Carga {i}: la cantidad debe ser al menos 1.")
        hazmat = bool(c.get("hazmat")) and ruta["hazmat"]
        cot = {o["linea"]: o for o in ruta["cotizaciones"][f"{tipo}|{int(hazmat)}"]}
        elegidas = c.get("lineas") or {}
        opciones = {}
        for linea, cap in elegidas.items():
            if linea in cot:
                cap = None if cap in (None, "") else max(0, int(cap))
                opciones[linea] = dict(cot[linea], capacidad=cap)
        if not opciones:
            raise ValueError(f"Carga {i}: selecciona al menos una línea transportista.")

        oc.calcular_eficiencia(opciones, peso)
        carga = {"cantidad": cantidad, "opciones": opciones}
        orden, asignacion, pendientes = oc.asignar(carga)

        asig = []
        for linea, q in asignacion:
            o = opciones[linea]
            asig.append({"linea": linea, "cantidad": q, "costo_unit": o["costo"],
                         "costo_total": q * o["costo"], "calif": o["calif"]})
            costo_total += q * o["costo"]
            suma_calif += q * o["calif"]
            asignadas += q
        sin_asignar += pendientes
        resultados.append({
            "ruta": ruta["nombre"], "tipo": tipo, "cantidad": cantidad, "hazmat": hazmat,
            "comparativo": [{"linea": l, "costo": o["costo"], "calif": o["calif"],
                             "eficiencia": o["eficiencia"], "notas": o["notas"],
                             "capacidad": o["capacidad"]} for l, o in orden],
            "asignacion": asig, "pendientes": pendientes,
        })

    if not resultados:
        raise ValueError("Agrega al menos una carga.")
    return {"cargas": resultados, "costo_total": costo_total, "asignadas": asignadas,
            "sin_asignar": sin_asignar,
            "calif_promedio": (suma_calif / asignadas) if asignadas else None,
            "peso_costo": peso}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        try:
            if path in ("/", "/index.html"):
                with open(INDEX, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            elif path == "/api/datos":
                self._send(200, construir_datos())
            elif path.lstrip("/") in ESTATICOS:
                nombre = path.lstrip("/")
                with open(os.path.join(BASE, "web", nombre), "rb") as f:
                    self._send(200, f.read(), ESTATICOS[nombre])
            else:
                self._send(404, {"error": "No encontrado"})
        except Exception as e:  # noqa: BLE001
            self._send(500, {"error": f"No se pudo leer {os.path.basename(EXCEL)}: {e}"})

    def do_POST(self):
        if self.path != "/api/optimizar":
            return self._send(404, {"error": "No encontrado"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
            self._send(200, optimizar(payload))
        except ValueError as e:
            self._send(400, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            self._send(500, {"error": f"Error interno: {e}"})

    def log_message(self, *args):
        pass  # silencia el log de cada petición


def main():
    if not os.path.exists(EXCEL):
        sys.exit(f"No se encontró el archivo de tarifas: {EXCEL}")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print("=" * 60)
    print("  Optimizador de Cargas - interfaz web")
    print(f"  Abre en tu navegador:  {url}")
    print("  Para detener: Ctrl + C")
    print("=" * 60)
    if "--no-browser" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")


if __name__ == "__main__":
    main()
