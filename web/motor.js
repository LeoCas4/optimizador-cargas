/*
 * Motor del Optimizador de Cargas (versión JavaScript).
 *
 * Hace en el navegador lo mismo que optimizar_cargas.py / app_web.py:
 *   1. Lee Tarifas.xlsx (lector propio, sin librerías externas).
 *   2. Arma tarifas, calificaciones y cotizaciones por ruta.
 *   3. Calcula la eficiencia y reparte las cargas.
 *
 * Así el programa funciona como sitio estático (por ejemplo en HostGator):
 * basta con subir index.html, motor.js, logo.png y Tarifas.xlsx.
 */
(function (global) {
  'use strict';

  const TIPOS = ['IMPO', 'EXPO', 'TOURING'];
  const PESO_COSTO = 0.5;
  const PLAZA_CLAVE_CALIF = { 'SAN LUIS POTOSI': 'SLP', MONTERREY: 'SAVI' };
  const PLAZAS_CONOCIDAS = new Set(['SAN LUIS POTOSI', 'MONTERREY']);

  /* ===================================================================== */
  /* Lector mínimo de .xlsx (ZIP + XML)                                    */
  /* ===================================================================== */
  async function inflar(bytes) {
    const ds = new DecompressionStream('deflate-raw');
    const stream = new Blob([bytes]).stream().pipeThrough(ds);
    return new Uint8Array(await new Response(stream).arrayBuffer());
  }

  async function leerZip(buffer) {
    const dv = new DataView(buffer);
    const u8 = new Uint8Array(buffer);
    let eocd = -1;
    for (let i = u8.length - 22; i >= Math.max(0, u8.length - 65557); i--) {
      if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
    }
    if (eocd < 0) throw new Error('El archivo de tarifas no es un Excel (.xlsx) válido.');
    const total = dv.getUint16(eocd + 10, true);
    let p = dv.getUint32(eocd + 16, true);
    const dec = new TextDecoder('utf-8');
    const archivos = {};
    for (let n = 0; n < total; n++) {
      if (dv.getUint32(p, true) !== 0x02014b50) break;
      const metodo = dv.getUint16(p + 10, true);
      const tamComp = dv.getUint32(p + 20, true);
      const lenNombre = dv.getUint16(p + 28, true);
      const lenExtra = dv.getUint16(p + 30, true);
      const lenComent = dv.getUint16(p + 32, true);
      const offLocal = dv.getUint32(p + 42, true);
      const nombre = dec.decode(u8.subarray(p + 46, p + 46 + lenNombre));
      archivos[nombre] = { metodo, tamComp, offLocal };
      p += 46 + lenNombre + lenExtra + lenComent;
    }
    return {
      async texto(nombre) {
        const f = archivos[nombre];
        if (!f) return null;
        const o = f.offLocal;
        const ini = o + 30 + dv.getUint16(o + 26, true) + dv.getUint16(o + 28, true);
        const datos = u8.subarray(ini, ini + f.tamComp);
        const raw = f.metodo === 0 ? datos : await inflar(datos);
        return dec.decode(raw);
      },
    };
  }

  function desescapar(s) {
    return s.replace(/&(#x[0-9a-fA-F]+|#\d+|amp|lt|gt|quot|apos);/g, (m, e) => {
      if (e[0] === '#') return String.fromCodePoint(e[1] === 'x' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10));
      return { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" }[e];
    });
  }

  function textoDe(xml) {
    // Concatena todos los <t>…</t> (texto con formato puede venir en varios runs)
    let out = '';
    const re = /<(?:\w+:)?t(?:\s[^>]*)?>([\s\S]*?)<\/(?:\w+:)?t>/g;
    let m;
    while ((m = re.exec(xml))) out += desescapar(m[1]);
    return out;
  }

  function columna(ref) {
    const letras = ref.replace(/\d+/g, '');
    let n = 0;
    for (const ch of letras) n = n * 26 + (ch.charCodeAt(0) - 64);
    return n - 1;
  }

  /** Devuelve las filas de la primera hoja como arreglos (null = celda vacía). */
  async function leerPrimeraHoja(buffer) {
    const zip = await leerZip(buffer);

    // Ruta de la primera hoja según workbook.xml + sus relaciones
    let ruta = 'xl/worksheets/sheet1.xml';
    const wb = await zip.texto('xl/workbook.xml');
    const rels = await zip.texto('xl/_rels/workbook.xml.rels');
    if (wb && rels) {
      const hoja = /<(?:\w+:)?sheet\b[^>]*?\br:id="([^"]+)"/.exec(wb);
      if (hoja) {
        const re = /<Relationship\b[^>]*>/g;
        let m;
        while ((m = re.exec(rels))) {
          const id = /\bId="([^"]+)"/.exec(m[0]);
          const tgt = /\bTarget="([^"]+)"/.exec(m[0]);
          if (id && tgt && id[1] === hoja[1]) {
            const t = tgt[1];
            ruta = t.startsWith('/') ? t.slice(1) : 'xl/' + t.replace(/^\.\//, '');
            break;
          }
        }
      }
    }

    const compartidos = [];
    const ss = await zip.texto('xl/sharedStrings.xml');
    if (ss) {
      const re = /<(?:\w+:)?si>([\s\S]*?)<\/(?:\w+:)?si>/g;
      let m;
      while ((m = re.exec(ss))) compartidos.push(textoDe(m[1]));
    }

    const xml = await zip.texto(ruta);
    if (!xml) throw new Error('No se encontró la hoja de tarifas dentro del Excel.');

    const filas = [];
    let maxCol = 0;
    const reFila = /<(?:\w+:)?row\b([^>]*?)(?:\/>|>([\s\S]*?)<\/(?:\w+:)?row>)/g;
    const reCelda = /<(?:\w+:)?c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/(?:\w+:)?c>)/g;
    let mf, numFila = 0;
    while ((mf = reFila.exec(xml))) {
      const rAttr = /\br="(\d+)"/.exec(mf[1]);
      numFila = rAttr ? parseInt(rAttr[1], 10) : numFila + 1;
      const fila = [];
      let mc, col = -1;
      reCelda.lastIndex = 0;
      const cuerpo = mf[2] || '';
      while ((mc = reCelda.exec(cuerpo))) {
        const attrs = mc[1];
        const ref = /\br="([A-Z]+\d+)"/.exec(attrs);
        col = ref ? columna(ref[1]) : col + 1;
        const tipo = (/\bt="([^"]+)"/.exec(attrs) || [])[1] || 'n';
        const dentro = mc[2] || '';
        const v = /<(?:\w+:)?v>([\s\S]*?)<\/(?:\w+:)?v>/.exec(dentro);
        let valor = null;
        if (tipo === 's') valor = v ? (compartidos[parseInt(v[1], 10)] ?? null) : null;
        else if (tipo === 'inlineStr') valor = textoDe(dentro);
        else if (tipo === 'str') valor = v ? desescapar(v[1]) : null;
        else if (tipo === 'b') valor = v ? v[1] === '1' : null;
        else if (tipo === 'e') valor = v ? desescapar(v[1]) : null;
        else valor = v && v[1] !== '' ? Number(v[1]) : null;
        if (valor === '') valor = null;
        fila[col] = valor;
      }
      filas[numFila - 1] = fila;
      maxCol = Math.max(maxCol, fila.length);
    }
    for (let i = 0; i < filas.length; i++) {
      const f = filas[i] || [];
      const completa = [];
      for (let c = 0; c < maxCol; c++) completa.push(f[c] === undefined ? null : f[c]);
      filas[i] = completa;
    }
    return filas;
  }

  /* ===================================================================== */
  /* Utilidades (equivalentes a las de Python)                             */
  /* ===================================================================== */
  function norm(texto) {
    let t = String(texto).normalize('NFD').replace(/\p{Mn}/gu, '').toUpperCase().trim();
    t = t.replace(/\s*-\s*/g, '-');
    return t.replace(/\s+/g, ' ');
  }

  function aNumero(v) {
    if (typeof v === 'number') return v;
    if (typeof v === 'boolean') return v ? 1 : 0;
    return null;
  }

  function numeroEnTexto(texto) {
    const m = /\d+(?:\.\d+)?/.exec(String(texto));
    return m ? parseFloat(m[0]) : null;
  }

  function texto(v) {
    if (typeof v === 'boolean') return v ? 'True' : 'False';
    return String(v);
  }

  /* ===================================================================== */
  /* Lectura de tarifas                                                    */
  /* ===================================================================== */
  function leerTarifas(filas) {
    const calificaciones = {};
    for (const fila of filas) {
      for (const celda of fila) {
        if (typeof celda === 'string') {
          const m = /^\s*(.+?)\s*-\s*(\d+(?:\.\d+)?)\s*$/.exec(celda);
          if (m && !/\d/.test(m[1])) calificaciones[norm(m[1])] = parseFloat(m[2]);
        }
      }
    }

    const tarifas = {};
    const nombresRuta = {};
    let plaza = null;
    let lineas = [];
    let huboFilas = true;

    for (const fila of filas) {
      const a = fila.length ? fila[0] : null;
      if (a === null || typeof a !== 'string') continue;
      const aN = norm(a);
      const restoVacio = fila.slice(1, 6).every(v => v === null || v === undefined);

      if (aN.startsWith('TARIFAS')) continue;
      if (PLAZAS_CONOCIDAS.has(aN) && restoVacio) {
        plaza = aN;
        tarifas[plaza] = tarifas[plaza] || {};
        lineas = []; huboFilas = true;
        continue;
      }
      if (aN === 'CLIENTE') continue;
      if (restoVacio) {
        lineas = huboFilas ? [aN] : lineas.concat([aN]);
        huboFilas = false;
        tarifas[plaza] = tarifas[plaza] || {};
        tarifas[plaza][aN] = tarifas[plaza][aN] || {};
        continue;
      }

      const [impo, expo, completa] = [fila[1], fila[2], fila[3]].map(aNumero);
      const accExpo = fila.length > 4 ? fila[4] : null;
      const accImpo = fila.length > 5 ? fila[5] : null;
      const ruta = aN;
      if (!(ruta in nombresRuta)) nombresRuta[ruta] = ruta;
      huboFilas = true;
      for (const linea of lineas) {
        tarifas[plaza][linea][ruta] = {
          IMPO: impo, EXPO: expo, COMPLETA: completa,
          ACC_EXPO: accExpo ? texto(accExpo).trim() : null,
          ACC_IMPO: accImpo ? texto(accImpo).trim() : null,
        };
      }
    }
    return { tarifas, calificaciones, nombresRuta };
  }

  function calificacionDe(linea, plaza, calificaciones) {
    if (linea in calificaciones) return calificaciones[linea];
    const clave = PLAZA_CLAVE_CALIF[plaza] || '';
    const candidatos = Object.keys(calificaciones).filter(k => k.startsWith(linea));
    for (const k of candidatos) if (clave && k.includes(clave)) return calificaciones[k];
    return candidatos.length ? calificaciones[candidatos[0]] : null;
  }

  /* ===================================================================== */
  /* Costo de una carga (accesoriales siempre incluidos)                   */
  /* ===================================================================== */
  function costoCarga(tarifa, tipo, hazmat) {
    const notas = [];
    const { IMPO: impo, EXPO: expo, COMPLETA: completa } = tarifa;
    let base = { IMPO: impo, EXPO: expo, TOURING: completa }[tipo];

    if (base === null || base === undefined) {
      if (completa === null || completa === undefined) return [null, notas];
      base = completa;
      notas.push('tarifa completa');
    }

    let costo = base;
    const usaExpo = tipo === 'EXPO' || tipo === 'TOURING';
    const usaImpo = tipo === 'IMPO' || tipo === 'TOURING';

    let acc = tarifa.ACC_EXPO;
    if (acc && usaExpo) {
      const val = numeroEnTexto(acc);
      if (val) { costo += val; notas.push(`+${acc}`); }
    }

    acc = tarifa.ACC_IMPO;
    if (acc) {
      const val = numeroEnTexto(acc);
      if (norm(acc).includes('HAZMAT')) {
        if (hazmat && val) { costo = val; notas.push('tarifa HAZMAT'); }
      } else if (val && usaImpo) {
        costo += val; notas.push(`+${acc}`);
      }
    }
    return [costo, notas];
  }

  /* ===================================================================== */
  /* Datos para la interfaz (mismo formato que /api/datos)                 */
  /* ===================================================================== */
  function construirDatos(filas, archivo) {
    const { tarifas, calificaciones, nombresRuta } = leerTarifas(filas);
    const plazas = {};
    for (const [plaza, lineas] of Object.entries(tarifas)) {
      const conTarifa = {};
      for (const [l, r] of Object.entries(lineas)) if (Object.keys(r).length) conTarifa[l] = r;
      const calif = {};
      for (const l of Object.keys(conTarifa)) calif[l] = calificacionDe(l, plaza, calificaciones) || 0.0;

      const rutasSet = new Set();
      for (const t of Object.values(conTarifa)) for (const r of Object.keys(t)) rutasSet.add(r);
      const rutas = [...rutasSet].sort();

      const infoRutas = {};
      for (const ruta of rutas) {
        const hazmat = Object.values(conTarifa).some(t =>
          t[ruta] && t[ruta].ACC_IMPO && norm(t[ruta].ACC_IMPO).includes('HAZMAT'));
        const cot = {};
        for (const tipo of TIPOS) {
          for (const h of (hazmat ? [false, true] : [false])) {
            const lista = [];
            for (const [l, t] of Object.entries(conTarifa)) {
              if (t[ruta]) {
                const [costo, notas] = costoCarga(t[ruta], tipo, h);
                if (costo !== null) lista.push({ linea: l, costo, calif: calif[l], notas });
              }
            }
            cot[`${tipo}|${h ? 1 : 0}`] = lista;
          }
        }
        infoRutas[ruta] = { nombre: nombresRuta[ruta] || ruta, hazmat, cotizaciones: cot };
      }
      plazas[plaza] = {
        lineas: Object.entries(calif).map(([nombre, c]) => ({ nombre, calif: c }))
          .sort((x, y) => y.calif - x.calif),
        rutas: infoRutas,
      };
    }
    return { plazas, peso_costo: PESO_COSTO, archivo };
  }

  /* ===================================================================== */
  /* Optimización (mismo formato que /api/optimizar)                       */
  /* ===================================================================== */
  function calcularEficiencia(opciones, peso) {
    const cmin = Math.min(...Object.values(opciones).map(o => o.costo));
    for (const o of Object.values(opciones)) {
      o.eficiencia = 100 * (peso * cmin / o.costo + (1 - peso) * o.calif / 5);
    }
  }

  function asignar(cantidad, opciones) {
    let pendientes = cantidad;
    const asignacion = [];
    const orden = Object.entries(opciones)
      .sort((a, b) => (b[1].eficiencia - a[1].eficiencia) || (a[1].costo - b[1].costo));
    for (const [linea, o] of orden) {
      if (pendientes === 0) break;
      const q = o.capacidad === null ? pendientes : Math.min(o.capacidad, pendientes);
      if (q > 0) { asignacion.push([linea, q]); pendientes -= q; }
    }
    return { orden, asignacion, pendientes };
  }

  function optimizar(datos, payload) {
    const plaza = datos.plazas[payload.plaza];
    if (!plaza) throw new Error('Plaza no válida.');
    let peso = payload.peso_costo === undefined ? PESO_COSTO : Number(payload.peso_costo);
    peso = Math.min(Math.max(peso, 0.0), 1.0);

    const resultados = [];
    let costoTotal = 0, sumaCalif = 0, asignadas = 0, sinAsignar = 0;
    (payload.cargas || []).forEach((c, idx) => {
      const i = idx + 1;
      const ruta = plaza.rutas[c.ruta];
      if (!ruta) throw new Error(`Carga ${i}: elige una ruta.`);
      if (!TIPOS.includes(c.tipo)) throw new Error(`Carga ${i}: tipo no válido.`);
      const cantidad = parseInt(c.cantidad, 10) || 0;
      if (cantidad < 1) throw new Error(`Carga ${i}: la cantidad debe ser al menos 1.`);
      const hazmat = Boolean(c.hazmat) && ruta.hazmat;
      const cot = {};
      for (const o of ruta.cotizaciones[`${c.tipo}|${hazmat ? 1 : 0}`]) cot[o.linea] = o;

      const opciones = {};
      for (const [linea, capRaw] of Object.entries(c.lineas || {})) {
        if (linea in cot) {
          const cap = (capRaw === null || capRaw === undefined || capRaw === '')
            ? null : Math.max(0, parseInt(capRaw, 10) || 0);
          opciones[linea] = { ...cot[linea], notas: [...cot[linea].notas], capacidad: cap };
        }
      }
      if (!Object.keys(opciones).length) throw new Error(`Carga ${i}: selecciona al menos una línea transportista.`);

      calcularEficiencia(opciones, peso);
      const { orden, asignacion, pendientes } = asignar(cantidad, opciones);

      const asig = asignacion.map(([linea, q]) => {
        const o = opciones[linea];
        costoTotal += q * o.costo;
        sumaCalif += q * o.calif;
        asignadas += q;
        return { linea, cantidad: q, costo_unit: o.costo, costo_total: q * o.costo, calif: o.calif };
      });
      sinAsignar += pendientes;
      resultados.push({
        ruta: ruta.nombre, tipo: c.tipo, cantidad, hazmat,
        comparativo: orden.map(([l, o]) => ({
          linea: l, costo: o.costo, calif: o.calif, eficiencia: o.eficiencia,
          notas: o.notas, capacidad: o.capacidad,
        })),
        asignacion: asig, pendientes,
      });
    });

    if (!resultados.length) throw new Error('Agrega al menos una carga.');
    return {
      cargas: resultados, costo_total: costoTotal, asignadas, sin_asignar: sinAsignar,
      calif_promedio: asignadas ? sumaCalif / asignadas : null, peso_costo: peso,
    };
  }

  /* ===================================================================== */
  /* API pública                                                           */
  /* ===================================================================== */
  async function cargarTarifas(url) {
    const res = await fetch(url + (url.includes('?') ? '&' : '?') + 't=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) throw new Error(`No se pudo descargar ${url} (error ${res.status}).`);
    const filas = await leerPrimeraHoja(await res.arrayBuffer());
    return construirDatos(filas, decodeURIComponent(url.split('/').pop().split('?')[0]));
  }

  const Motor = { cargarTarifas, optimizar, leerPrimeraHoja, construirDatos, leerTarifas, costoCarga, norm };
  if (typeof module !== 'undefined' && module.exports) module.exports = Motor;
  else global.Motor = Motor;
})(typeof window !== 'undefined' ? window : globalThis);
