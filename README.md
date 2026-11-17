# Optimizador de Cargas

Programa que recomienda **qué línea transportista conviene para cada carga**, buscando el **menor costo** y la **mejor calificación** de la línea.

Lee las tarifas y calificaciones del archivo `Tarifas.xlsx` y se usa desde el navegador: en tu propia computadora (`http://localhost:8000`) o publicado en internet.

> **Sitio en línea:** **https://cargasop.com/optimizador/**
> Alojado en HostGator México. Los datos del sitio están en la [sección 10](#10-datos-del-sitio-publicado).

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
9. [Publicar en internet (HostGator)](#9-publicar-en-internet-hostgator)
10. [Datos del sitio publicado](#10-datos-del-sitio-publicado)

---

## 1. Instalar Python (desde cero)

El programa necesita **Python 3.9 o más reciente**. Solo se instala una vez.
Sigue los pasos de tu sistema: [Windows](#windows) o [Mac](#mac).

### Windows

1. Entra a **https://www.python.org/downloads/** y haz clic en el botón amarillo **Download Python 3.x**.
2. Abre el archivo descargado (`python-3.x.x-amd64.exe`).
3. **MUY IMPORTANTE:** en la primera pantalla del instalador marca la casilla
   **Add python.exe to PATH** (está abajo).
4. Haz clic en **Install Now** y espera a que termine. Al final haz clic en **Close**.
5. Comprueba la instalación:
   - Presiona la tecla **Windows**, escribe `cmd` y presiona **Enter**.
   - En la ventana negra escribe lo siguiente y presiona Enter:
     ```
     py --version
     ```
   - Debe aparecer algo como `Python 3.13.1`.

> **Si ves el mensaje "no se encontró Python; ejecutar sin argumentos para instalar desde el Microsoft Store…"**
> usa `py` en lugar de `python` en todos los comandos. Ese aviso sale porque Windows tiene un acceso directo a la Microsoft Store.
> Si quieres desactivarlo: **Configuración → Aplicaciones → Configuración avanzada de aplicaciones → Alias de ejecución de aplicaciones** y apaga **python.exe** y **python3.exe**.

### Mac

1. Entra a **https://www.python.org/downloads/** y haz clic en **Download Python 3.x**.
   La página detecta que usas Mac y descarga el instalador `python-3.x.x-macos11.pkg`. Sirve para Mac con chip Intel y con chip Apple (M1, M2, M3, M4).
2. Abre la carpeta **Descargas** y haz doble clic en el archivo `.pkg`.
3. En el instalador haz clic en **Continuar** → **Continuar** → **Aceptar** → **Instalar**.
   Te pedirá la **contraseña de tu Mac** (o Touch ID). Espera a que termine y haz clic en **Cerrar**.
4. Al terminar se abre una carpeta llamada **Python 3.x**. Haz doble clic en **`Install Certificates.command`**.
   Se abre una ventana de Terminal, hace la configuración sola y la puedes cerrar cuando diga `process completed`.
   (Esto permite que Python descargue la librería que usa el programa.)
5. Comprueba la instalación:
   - Presiona **Cmd + Espacio**, escribe `Terminal` y presiona **Enter**.
   - En la Terminal escribe lo siguiente y presiona Enter:
     ```
     python3 --version
     ```
   - Debe aparecer algo como `Python 3.13.1`.

> **En Mac siempre se usa `python3`** (no `python`).
>
> **Si al escribir `python3` aparece una ventana pidiendo instalar las "herramientas de desarrollo de línea de comandos"**,
> significa que todavía no se instaló Python desde python.org. Haz clic en **Cancelar** y repite los pasos 1 a 4.

## 2. Descargar el programa

**Opción fácil (sin Git):**

1. En esta página de GitHub haz clic en el botón verde **`<> Code`** → **Download ZIP**.
2. Descomprime el archivo:
   - **Windows:** en tu carpeta **Descargas**, clic derecho sobre el ZIP → **Extraer todo…** → **Extraer**.
   - **Mac:** en tu carpeta **Descargas**, haz doble clic en el ZIP (Safari a veces lo descomprime solo).
3. Te quedará una carpeta llamada `optimizador-cargas-main`. Puedes moverla a donde quieras (por ejemplo, al Escritorio o a Documentos).

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

### Mac: doble clic (recomendado)

1. Entra a la carpeta del programa.
2. **La primera vez:** haz **clic derecho** (o Control + clic) sobre **`Abrir Optimizador.command`** → **Abrir** → en el aviso vuelve a hacer clic en **Abrir**.
   Esto es necesario porque macOS bloquea los archivos descargados de internet la primera vez.
   Las siguientes veces basta con hacer **doble clic**.
3. Se abre una ventana de Terminal. La primera vez instalará lo que necesita (tarda unos segundos).
4. Se abrirá el navegador con el programa. Si no se abre solo, entra a **http://localhost:8000**.
5. **No cierres la ventana de Terminal** mientras uses el programa. Para salir, presiona `Ctrl + C` en la Terminal y luego ciérrala.

> Si macOS dice **"no se puede abrir porque proviene de un desarrollador no identificado"** y no aparece el botón Abrir:
> ve a **Configuración del Sistema → Privacidad y seguridad**, baja hasta el mensaje de `Abrir Optimizador.command` y haz clic en **Abrir de todas formas**.
>
> Si dice **"no tienes permiso"** o el archivo se abre en un editor de texto, sigue los pasos "con comandos" de abajo.
> Una vez dentro de la carpeta en la Terminal, también puedes repararlo con `chmod +x "Abrir Optimizador.command"`.

### Mac: con comandos (alternativa)

1. Abre **Terminal** (Cmd + Espacio → escribe `Terminal` → Enter).
2. Escribe `cd` seguido de **un espacio**, luego **arrastra la carpeta del programa** desde el Finder hasta la ventana de Terminal y presiona **Enter**.
   Debe verse algo así:
   ```
   cd /Users/tu-usuario/Downloads/optimizador-cargas-main
   ```
   > Otra forma: en el Finder haz clic derecho sobre la carpeta → **Servicios** → **Nuevo Terminal en la carpeta**.
3. **Solo la primera vez**, instala la librería para leer Excel:
   ```
   python3 -m pip install -r requirements.txt
   ```
4. Abre el programa:
   ```
   python3 app_web.py
   ```
5. Se abre el navegador en **http://localhost:8000**. Para salir, presiona `Ctrl + C` en la Terminal.

**Las siguientes veces** solo necesitas los pasos 1, 2 y 4.

### Versión de consola (sin navegador)

También existe una versión que funciona solo con preguntas en la ventana negra:
- Windows:
  ```
  py optimizador_cargas.py
  ```
- Mac:
  ```
  python3 optimizador_cargas.py
  ```

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
- Windows:
  ```
  py app_web.py "C:\ruta\a\OtroArchivo.xlsx"
  ```
- Mac:
  ```
  python3 app_web.py "/Users/tu-usuario/Documents/OtroArchivo.xlsx"
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

### Windows

| Problema | Solución |
|---|---|
| `no se encontró Python…` o `python no se reconoce…` | Usa `py` en lugar de `python`. Si `py` tampoco funciona, reinstala Python marcando **Add python.exe to PATH**. |
| `No module named openpyxl` o `Falta la librería openpyxl` | Ejecuta `py -m pip install -r requirements.txt` dentro de la carpeta del programa. |
| "Windows protegió su PC" al abrir el `.bat` | Clic en **Más información → Ejecutar de todas formas**. |
| El puerto 8000 está ocupado (`Address already in use`) | El programa ya está abierto en otra ventana. Ciérrala, o usa otro puerto: `set PORT=8001` y luego `py app_web.py`. |

### Mac

| Problema | Solución |
|---|---|
| `command not found: python3` o aparece la ventana de "herramientas de desarrollo" | Instala Python desde python.org (sección 1, Mac). |
| `No module named openpyxl` o `Falta la librería openpyxl` | Ejecuta `python3 -m pip install -r requirements.txt` dentro de la carpeta del programa. |
| `SSL: CERTIFICATE_VERIFY_FAILED` al instalar | Abre **Aplicaciones → Python 3.x** y haz doble clic en **`Install Certificates.command`**. Luego repite la instalación. |
| `error: externally-managed-environment` | Tu Python es de Homebrew. Instala Python desde python.org (sección 1, Mac) o usa `python3 -m pip install --user -r requirements.txt`. |
| "No se puede abrir… desarrollador no identificado" | Clic derecho → **Abrir**, o **Configuración del Sistema → Privacidad y seguridad → Abrir de todas formas**. |
| `Abrir Optimizador.command` se abre como texto o dice "permiso denegado" | En la Terminal, dentro de la carpeta: `chmod +x "Abrir Optimizador.command"`. |
| El puerto 8000 está ocupado (`Address already in use`) | El programa ya está abierto en otra Terminal. Ciérrala, o usa otro puerto: `PORT=8001 python3 app_web.py`. |

### Ambos

| Problema | Solución |
|---|---|
| `No se encontró el archivo de tarifas` | Revisa que `Tarifas.xlsx` esté en la misma carpeta que `app_web.py`. |
| La página no carga o dice "No se pudo abrir Tarifas.xlsx" | En tu computadora: la ventana negra (o la Terminal) se cerró; vuelve a abrir el programa. En internet: revisa que `Tarifas.xlsx` esté en la misma carpeta que `index.html` y que se llame exactamente así (con T mayúscula). |
| No aparece el logo | Revisa que `logo.png` esté junto a `index.html` (en tu computadora: `web/logo.png`). |
| Al abrir `index.html` con doble clic no carga nada | La página no funciona abriéndola directo del disco. En tu computadora usa `app_web.py` (sección 3); en internet súbela al hosting (sección 9). |
| El Excel no se actualiza | Guarda y **cierra** el Excel, luego presiona **Recargar** en la página. |

---

## 8. Archivos del proyecto

```
optimizador-cargas/
├── Abrir Optimizador.bat       ← doble clic para abrir (Windows)
├── Abrir Optimizador.command   ← doble clic para abrir (Mac)
├── app_web.py                  ← servidor de la interfaz web (localhost:8000)
├── optimizador_cargas.py       ← lógica de cálculo + versión de consola
├── Tarifas.xlsx                ← tarifas y calificaciones
├── requirements.txt            ← librerías necesarias (openpyxl)
├── README.md                   ← este documento
├── .gitignore
├── web/
│   ├── index.html              ← interfaz
│   ├── motor.js                ← lee el Excel y hace los cálculos en el navegador
│   └── logo.png
├── hosting/
│   └── .htaccess               ← configuración para el hosting (sección 9)
└── docs/
    └── captura.png
```

La página (`web/index.html` + `web/motor.js`) hace todo el cálculo en el navegador leyendo directamente `Tarifas.xlsx`; `app_web.py` solo la sirve en tu computadora. Por eso la misma página funciona en local y en cualquier hosting. `optimizador_cargas.py` contiene la misma lógica en Python para la versión de consola.

---

## 9. Publicar en internet (HostGator)

La página funciona como un **sitio estático**: el hosting no necesita Python ni nada especial, solo hay que subir 5 archivos.

> **Importante: tus tarifas quedarán en internet.** Cualquier persona que conozca la dirección podría ver la página y descargar `Tarifas.xlsx`.
> Sigue el **paso 5** para protegerla con usuario y contraseña. Además, la página indica a Google que no la muestre en sus resultados.

### Paso 1: Juntar los archivos que se suben

Crea en tu computadora una carpeta llamada `optimizador` y copia en ella **estos 5 archivos, todos sueltos (sin subcarpetas)**:

| Archivo | Dónde está en el proyecto |
|---|---|
| `index.html` | carpeta `web` |
| `motor.js` | carpeta `web` |
| `logo.png` | carpeta `web` |
| `Tarifas.xlsx` | carpeta principal |
| `.htaccess` | carpeta `hosting` |

> **`.htaccess` no se ve en Windows o Mac** porque empieza con punto (es un archivo oculto).
> - **Windows:** en el Explorador de archivos, menú **Ver → Mostrar → Elementos ocultos**.
> - **Mac:** en el Finder presiona **Cmd + Shift + .** (punto).
>
> Si no logras copiarlo, no pasa nada: puedes crearlo después directamente en el hosting (ver paso 4).

### Paso 2: Entrar al Administrador de archivos de HostGator

1. Entra a **https://cliente.hostgator.mx** con tu cuenta.
2. En el menú de la izquierda haz clic en **Hospedajes**.
3. En tu plan haz clic en **Administrar** y luego en **cPanel** (se abre en otra pestaña).
4. En cPanel busca la sección **Archivos** y haz clic en **Administrador de archivos**.
5. En la columna de la izquierda haz clic en la carpeta **`public_html`**. Todo lo que está ahí es lo que se ve en internet.

> Si tienes varios dominios en el mismo plan, cada dominio adicional suele tener su propia carpeta (por ejemplo `public_html/otrodominio.com`). Entra a la carpeta del dominio que quieres usar.

### Paso 3: Crear la carpeta y subir los archivos

> **Opción rápida con el .zip:** entra a `public_html`, haz clic en **Cargar**, sube `optimizador-hostgator.zip`, luego clic derecho sobre el .zip → **Extract** → **Extract File(s)**. Se crea la carpeta `optimizador` con todo adentro y después puedes borrar el .zip.
> **Cuidado:** el .zip debe subirse y extraerse **dentro de `public_html`**. Si se extrae en la carpeta inicial (`/home2/usuario`), la carpeta queda fuera de internet y la página no abre; en ese caso selecciónala → **Mover** → escribe `/public_html` → **Move File(s)**.

Opción manual, archivo por archivo:


1. Dentro de `public_html`, haz clic en **+ Carpeta** (arriba a la izquierda), escribe `optimizador` y haz clic en **Create New Folder**.
   Usar una carpeta propia evita que se borre o se reemplace la página que ya tengas en tu sitio.
2. Haz doble clic en la carpeta **`optimizador`** para entrar.
3. Haz clic en **Cargar** (Upload) y arrastra los 5 archivos del paso 1. Espera a que cada uno llegue a 100 % y regresa con el enlace **Go Back to "/home/…/public_html/optimizador"**.
4. Revisa que dentro de `optimizador` estén `index.html`, `motor.js`, `logo.png` y `Tarifas.xlsx` (y `.htaccess`). Para ver `.htaccess` en el Administrador: **Configuración** (arriba a la derecha) → marca **Mostrar archivos ocultos (dotfiles)** → **Save**.

### Paso 4 (solo si no subiste `.htaccess`)

1. Dentro de la carpeta `optimizador`, haz clic en **+ Archivo**, escribe `.htaccess` y haz clic en **Create New File**.
2. Haz clic derecho sobre `.htaccess` → **Edit** → **Edit**.
3. Pega el contenido del archivo `hosting/.htaccess` de este proyecto y haz clic en **Save Changes**.

### Paso 5: Proteger con usuario y contraseña (recomendado)

1. Regresa a la página principal de **cPanel**.
2. En la sección **Archivos** haz clic en **Privacidad de directorios** (Directory Privacy).
3. Entra a `public_html` y haz clic en el nombre de la carpeta **`optimizador`** (o en **Editar**).
4. Marca **Proteger este directorio con contraseña**, escribe un nombre (por ejemplo "Optimizador de Cargas") y haz clic en **Guardar**.
5. En **Crear usuario**, escribe un usuario y una contraseña segura y haz clic en **Guardar**.
   Puedes crear un usuario para cada persona que lo vaya a usar.

### Paso 6: Abrir el programa en internet

Entra desde cualquier navegador a:

```
https://cargasop.com/optimizador/
```

Si hiciste el paso 5, te pedirá el usuario y la contraseña.

> **¿Todavía no tienes dominio?** Necesitas uno conectado a tu plan de hospedaje para tener una dirección como la de arriba.
> Puedes comprarlo en el **Portal del Cliente → Dominios → Nuevo dominio**, o usar uno que ya tengas en otro proveedor apuntando sus DNS a HostGator (en el mismo portal está la guía "¿Cuál es el DNS del hosting?").
>
> **El candado de seguridad (https):** si la dirección con `https://` muestra una advertencia, activa el certificado gratuito en **cPanel → Seguridad → SSL/TLS Status → Run AutoSSL** y espera unos minutos.

### Actualizar las tarifas en internet

1. Edita `Tarifas.xlsx` en tu computadora y guárdalo (mismo nombre).
2. En el **Administrador de archivos**, entra a `public_html/optimizador`, haz clic en **Cargar** y sube el nuevo `Tarifas.xlsx`. Si pregunta, acepta **reemplazar** el archivo.
3. En la página del optimizador haz clic en **Recargar**. Los cambios se ven de inmediato para todos.

### Actualizar el programa

Si en el futuro cambian `index.html`, `motor.js` o `logo.png` en este repositorio, súbelos de nuevo a `public_html/optimizador` reemplazando los anteriores, igual que con las tarifas.

### Problemas comunes en el hosting

| Problema | Solución |
|---|---|
| Sale **Error 500** (Internal Server Error) después de subir `.htaccess` | Edita `.htaccess` en el Administrador de archivos y borra la línea `Options -Indexes`. Si sigue igual, borra las líneas de `<IfModule mod_headers.c>` hasta `</IfModule>`. |
| Sale **Error 404** (Not Found) | Revisa la dirección: debe terminar en `/optimizador/` y la carpeta debe llamarse exactamente `optimizador` (en minúsculas). |
| Se ve la lista de archivos en vez del programa | Falta `index.html` en la carpeta, o tiene otro nombre (por ejemplo `index.html.txt`). |
| La página abre pero dice "No se pudo abrir Tarifas.xlsx" | Sube `Tarifas.xlsx` a la misma carpeta que `index.html`. El nombre distingue mayúsculas: debe ser `Tarifas.xlsx`. |
| Dice "No se pudo descargar Tarifas.xlsx (error 403)" | El archivo no tiene permiso de lectura. En el Administrador de archivos, selecciona `Tarifas.xlsx` → **Permisos** → escribe `644` (o marca **Lectura** en Usuario, Grupo y Mundo) → **Change Permissions**. Recarga la página. |
| Siguen saliendo las tarifas viejas | Revisa que el archivo sí se reemplazó (mira la fecha en el Administrador de archivos) y presiona **Recargar** en la página. |
| La página no pide contraseña | Repite el paso 5 sobre la carpeta `optimizador` y prueba en una ventana de incógnito. |

---

## 10. Datos del sitio publicado

### Dirección

**https://cargasop.com/optimizador/**

### Ficha del sitio

| Dato | Valor |
|---|---|
| Dirección del programa | https://cargasop.com/optimizador/ |
| Dominio | `cargasop.com` (registrado en HostGator México) |
| Proveedor de hosting | HostGator México |
| Plan | Plan Personal (hospedaje compartido con cPanel) |
| Vencimiento del plan | **15/12/2026**: renovar antes de esa fecha para que el sitio no se apague |
| Vencimiento del dominio | Revisar en **Portal del Cliente → Dominios → cargasop.com → Administrar** y renovar antes de que venza |
| Servidores DNS | `ns00004.hostgator.mx` y `ns00005.hostgator.mx` |
| IP del servidor | `69.6.201.55` (compartida) |
| Carpeta del programa en el servidor | `public_html/optimizador` |
| Archivos en esa carpeta | `index.html`, `motor.js`, `logo.png`, `Tarifas.xlsx`, `.htaccess` |
| Permisos de los archivos | `644` (lectura para todos, escritura solo para el dueño) |
| Tipo de sitio | Estático: el cálculo se hace en el navegador; el servidor no necesita Python |

### Cómo entrar a la administración

1. **Portal del Cliente:** https://cliente.hostgator.mx (usuario y contraseña de la cuenta de HostGator).
2. **cPanel:** Portal del Cliente → **Hospedajes** → **cPanel**. El usuario de cPanel aparece en el panel **Información general** de cPanel.
3. **Archivos del programa:** cPanel → **Administrador de archivos** → `public_html` → `optimizador`.

> Las contraseñas **no** se guardan en este repositorio. Guárdalas en un lugar seguro (por ejemplo, un administrador de contraseñas de la empresa).

### Tareas de mantenimiento

| Tarea | Cuándo | Cómo |
|---|---|---|
| Actualizar tarifas o calificaciones | Cada vez que cambien | Sube el nuevo `Tarifas.xlsx` a `public_html/optimizador` (reemplazar) y presiona **Recargar** en la página. Ver sección 9. |
| Renovar el plan de hospedaje | Antes del 15/12/2026 | Portal del Cliente → Hospedajes → Plan Personal → **Modificar Plan / Ciclo** o el aviso de renovación. |
| Renovar el dominio | Antes de su vencimiento | Portal del Cliente → Dominios → cargasop.com → **Administrar**. |
| Revisar el candado de seguridad (SSL) | Si el navegador muestra "No seguro" | cPanel → **SSL/TLS Status** → **Run AutoSSL**. |
| Revisar la contraseña de acceso | Al dar de alta o baja a usuarios | cPanel → **Privacidad de directorios** → `public_html/optimizador`. |
| Respaldo | Antes de cambios grandes | Descarga la carpeta `optimizador` desde el Administrador de archivos (clic derecho → **Comprimir** → descargar el .zip), o usa **Backup** en el Portal del Cliente. |

### Lecciones de la puesta en línea

- **Los archivos deben estar dentro de `public_html`.** Lo que está fuera de esa carpeta no se ve en internet.
- **`Tarifas.xlsx` debe tener permisos `644`.** Si no, la página muestra "No se pudo descargar Tarifas.xlsx (error 403)".
- **Si cPanel no abre (`ERR_CONNECTION_TIMED_OUT`)**, la red puede estar bloqueando cPanel (puerto 2083) o HostGator bloqueó la IP. Prueba con los datos del celular y, si es necesario, pide a **Soporte** que desbloquee tu IP.
- **Un dominio nuevo tarda hasta 24 horas en funcionar.** Se puede revisar en https://dnschecker.org: debe mostrar la IP `69.6.201.55`.
