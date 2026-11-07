# Optimizador de Cargas

Programa que recomienda **qué línea transportista conviene para cada carga**, buscando el **menor costo** y la **mejor calificación** de la línea.

Lee las tarifas y calificaciones del archivo `Tarifas.xlsx` y se usa desde el navegador, en tu propia computadora (`http://localhost:8000`).

![Captura del programa](docs/captura.png)

---

## Contenido

1. [Instalar Python (desde cero)](#1-instalar-python-desde-cero)
2. [Descargar el programa](#2-descargar-el-programa)
3. [Abrir el programa](#3-abrir-el-programa)
4. [Cómo usarlo](#4-cómo-usarlo)
5. [Actualizar tarifas y calificaciones](#5-actualizar-tarifas-y-calificaciones)
6. [Cómo se calcula la recomendación](#6-cómo-se-calcula-la-recomendación)
7. [Solución de problemas](#7-solución-de-problemas)
8. [Archivos del proyecto](#8-archivos-del-proyecto)

---

## 1. Instalar Python (desde cero)

El programa necesita **Python 3.9 o más reciente**. Solo se instala una vez.

### Windows

1. Entra a **https://www.python.org/downloads/** y haz clic en el botón amarillo **Download Python 3.x**.
2. Abre el archivo descargado (`python-3.x.x-amd64.exe`).
3. **MUY IMPORTANTE:** en la primera pantalla del instalador marca la casilla
   **☑ Add python.exe to PATH** (está abajo).
4. Haz clic en **Install Now** y espera a que termine. Al final haz clic en **Close**.
5. Comprueba la instalación:
   - Presiona la tecla **Windows**, escribe `cmd` y presiona **Enter**.
   - En la ventana negra escribe lo siguiente y presiona Enter:
     ```
     py --version
     ```
   - Debe aparecer algo como `Python 3.13.1`. ✅

> **Si ves el mensaje "no se encontró Python; ejecutar sin argumentos para instalar desde el Microsoft Store…"**
> usa `py` en lugar de `python` en todos los comandos. Ese aviso sale porque Windows tiene un acceso directo a la Microsoft Store.
> Si quieres desactivarlo: **Configuración → Aplicaciones → Configuración avanzada de aplicaciones → Alias de ejecución de aplicaciones** y apaga **python.exe** y **python3.exe**.

### Mac

1. Entra a **https://www.python.org/downloads/** y descarga **Python 3.x para macOS**.
2. Abre el archivo `.pkg` y sigue el instalador (Continuar → Aceptar → Instalar).
3. Comprueba la instalación: abre **Terminal** (Cmd + Espacio, escribe "Terminal") y escribe:
   ```
   python3 --version
   ```
   Debe aparecer algo como `Python 3.13.1`. ✅

---

## 2. Descargar el programa

**Opción fácil (sin Git):**

1. En esta página de GitHub haz clic en el botón verde **`<> Code`** → **Download ZIP**.
2. Busca el archivo en tu carpeta **Descargas**, haz clic derecho → **Extraer todo…** → **Extraer**.
3. Te quedará una carpeta llamada `optimizador-cargas-main`. Puedes moverla a donde quieras (por ejemplo, al Escritorio).

**Opción con Git** (si ya lo tienes instalado):
```bash
git clone https://github.com/LeoCas4/optimizador-cargas.git
```

---

## 3. Abrir el programa

### Windows: doble clic (recomendado)

1. Entra a la carpeta del programa.
2. Haz **doble clic** en **`Abrir Optimizador.bat`**.
3. La primera vez instalará automáticamente lo que necesita (tarda unos segundos).
4. Se abrirá el navegador con el programa. Si no se abre solo, entra a **http://localhost:8000**.
5. **No cierres la ventana negra** mientras uses el programa. Para salir, ciérrala (o presiona `Ctrl + C`).

> Si Windows muestra "Windows protegió su PC", haz clic en **Más información → Ejecutar de todas formas**.

### Windows: con comandos (alternativa)

1. Abre la carpeta del programa en el Explorador de archivos.
2. Haz clic en la barra de direcciones (arriba), escribe `cmd` y presiona **Enter**. Se abre una ventana negra ya ubicada en la carpeta.
3. **Solo la primera vez**, instala la librería para leer Excel:
   ```
   py -m pip install -r requirements.txt
   ```
4. Abre el programa:
   ```
   py app_web.py
   ```

### Mac

1. Abre **Terminal**.
2. Escribe `cd ` (con un espacio al final), **arrastra la carpeta del programa** a la Terminal y presiona **Enter**.
3. **Solo la primera vez**:
   ```
   python3 -m pip install -r requirements.txt
   ```
4. Abre el programa:
   ```
   python3 app_web.py
   ```
5. Se abre el navegador en **http://localhost:8000**. Para salir, presiona `Ctrl + C` en la Terminal.

### Versión de consola (sin navegador)

También existe una versión que funciona solo con preguntas en la ventana negra:
```
py optimizador_cargas.py
```
(en Mac: `python3 optimizador_cargas.py`)

---

## 4. Cómo usarlo

**Paso 1: Plaza y prioridad**
- Elige la plaza: **San Luis Potosí** o **Monterrey**. Verás las líneas de esa plaza con su calificación.
- Con la barra puedes dar más peso al **costo** (izquierda) o a la **calificación** (derecha). Por defecto es 50 % / 50 %.

**Paso 2: Cargas disponibles**
- **Ruta / cliente:** por ejemplo, HONDA-HONDA.
- **Tipo:** IMPO, EXPO o Ambos (Touring).
- **Cargas:** cuántas cargas tienes de esa ruta.
- **Líneas transportistas disponibles:** marca solo las líneas que tienes disponibles. Cada tarjeta muestra el costo por carga con los accesoriales incluidos.
- Si una línea solo puede llevar algunas cargas, escribe cuántas en **¿Cuántas cargas puede llevar?**. Si lo dejas vacío, se considera que puede llevar todas.
- **HAZMAT:** la casilla solo aparece en las rutas que tienen tarifa especial HAZMAT.
- Con **+ Agregar carga** capturas otra ruta.

**Paso 3: Recomendación**
- Presiona **Calcular recomendación**.
- Verás el **costo total**, las **cargas asignadas**, la **calificación promedio**, la tabla con la **línea recomendada** para cada carga y un comparativo de eficiencia de todas las líneas.
- Con **Imprimir / PDF** puedes guardar o compartir el resultado.

---

## 5. Actualizar tarifas y calificaciones

Todo se lee de **`Tarifas.xlsx`**, así que **no necesitas modificar el código** para cambiar precios.

- Edita el Excel y guárdalo (con el mismo nombre y en la misma carpeta).
- En el programa, haz clic en **Recargar** (arriba a la derecha).

Reglas del formato del Excel:
- Cada plaza va en una fila con su nombre (`SAN LUIS POTOSÍ`, `MONTERREY`).
- Cada línea transportista va en una fila con su nombre, seguida de la fila de encabezados `CLIENTE | IMPO | EXPO | TARIFA COMPLETA | ACCESORIAL EXPO | ACCESORIAL IMPO` y de sus rutas.
- Si varias líneas aparecen seguidas sin tabla entre ellas (como `MAX TRUCKING`, `SMART LOGISTICS` y `LEADS` en Monterrey), **comparten la tabla que viene debajo**.
- `NA` significa que esa línea solo cotiza la tarifa completa.
- Las calificaciones se escriben como `NOMBRE- 4.5` (por ejemplo, `XPRESS- 4`). Para Max Trucking se usan `Max trucking SLP` y `Max trucking SAVI` (Monterrey).

Para usar otro archivo de Excel:
```
py app_web.py "C:\ruta\a\OtroArchivo.xlsx"
```

---

## 6. Cómo se calcula la recomendación

**Costo por carga**
| Tipo | Tarifa usada |
|---|---|
| IMPO | columna IMPO + accesorial IMPO |
| EXPO | columna EXPO + accesorial EXPO (p. ej. MSS 50) |
| Ambos (Touring) | TARIFA COMPLETA + accesoriales EXPO e IMPO |

- Los accesoriales se suman siempre que la ruta los tenga.
- **HAZMAT:** si la carga es HAZMAT, se usa la tarifa HAZMAT en lugar de la tarifa normal (p. ej. Ford en Monterrey con ALASA: $754 en vez de $580).

**Eficiencia (0 a 100 %)**, solo entre las líneas que marcaste como disponibles:

```
Eficiencia = %costo × (costo más bajo ÷ costo de la línea) + %calificación × (calificación ÷ 5)
```

Las cargas se asignan primero a la línea más eficiente. Si esa línea no puede llevarlas todas, el resto pasa a la siguiente mejor.

---

## 7. Solución de problemas

| Problema | Solución |
|---|---|
| `no se encontró Python…` o `python no se reconoce…` | Usa `py` en lugar de `python`. Si `py` tampoco funciona, reinstala Python marcando **Add python.exe to PATH**. |
| `No module named openpyxl` o `Falta la librería openpyxl` | Ejecuta `py -m pip install -r requirements.txt` dentro de la carpeta del programa. |
| `No se encontró el archivo de tarifas` | Revisa que `Tarifas.xlsx` esté en la misma carpeta que `app_web.py`. |
| La página dice "No hay conexión con el programa" | La ventana negra se cerró. Vuelve a abrir el programa. |
| `Address already in use` / el puerto 8000 está ocupado | El programa ya está abierto en otra ventana. Ciérrala, o abre otro puerto: en `cmd`, `set PORT=8001` y luego `py app_web.py`. |
| No aparece el logo | Revisa que exista `web/logo.png`. |
| El Excel no se actualiza | Guarda y **cierra** el Excel, luego presiona **Recargar** en la página. |

---

## 8. Archivos del proyecto

```
optimizador-cargas/
├── Abrir Optimizador.bat   ← doble clic para abrir (Windows)
├── app_web.py              ← servidor de la interfaz web (localhost:8000)
├── optimizador_cargas.py   ← lógica de cálculo + versión de consola
├── Tarifas.xlsx            ← tarifas y calificaciones
├── requirements.txt        ← librerías necesarias (openpyxl)
├── web/
│   ├── index.html          ← interfaz
│   └── logo.png
└── docs/
    └── captura.png
```
