"""USDA 2022 evidence scope and cross-table checks; no inferred diagnoses."""
import hashlib
import json
import math

REFERENCE = 'Keys to Soil Taxonomy, 13th ed. (2022)'
URL = 'https://www.nrcs.usda.gov/sites/default/files/2022-09/Keys-to-Soil-Taxonomy.pdf'

# References describe possible uses, never universal measurement requirements.
LAB_USES = {
    'pH': 'Sulfuric horizon; documentar agua y relación suelo:solución (cap. 3).',
    'Carbono orgánico': 'Epipedons; organic soil materials; distribución de C en subgrupos fluventic (cap. 3; KFGL/KFGS/KFGT).',
    'Carbonato de calcio equivalente': 'Calcic/petrocalcic horizons (cap. 3).',
    'Yeso': 'Gypsic/petrogypsic horizons (cap. 3).',
    'Arena': 'Textura de tierra fina; salidas arenic/psammentic (HCGE/HCGJ/HCGK/HCGL; KFGR y claves de familia).',
    'Limo': 'Textura y granulometría; documentar fracción y sección de control (caps. 3 y 17).',
    'Arcilla': 'Argillic/kandic/oxic horizons y granulometría (caps. 3 y 17; KFGV).',
    'Potasio intercambiable (K)': 'Componente de saturación de bases; método requerido por la clave (cap. 3).',
    'Calcio intercambiable (Ca)': 'Componente de saturación de bases; método requerido por la clave (cap. 3).',
    'Magnesio intercambiable (Mg)': 'Componente de saturación de bases; método requerido por la clave (cap. 3).',
    'Sodio intercambiable (Na)': 'Natric horizon y saturación de bases; documentar método (cap. 3).',
    'Aluminio intercambiable (Al)': 'Suma de cationes; documentar extractante y denominador (cap. 3).',
    'Acidez intercambiable (Al + H)': 'Cálculo documentado de intercambio y saturación; no sustituye métodos (cap. 3).',
    'CIC del suelo': 'Saturación de bases y actividad de arcilla; método y correcciones (cap. 3; KFGV).',
    'CICE del suelo': 'Evidencia de intercambio efectivo; documentar criterio y cálculo (cap. 3).',
    'Suma de bases': 'Saturación de bases; conservar cationes y denominador (cap. 3).',
    'CIC de la arcilla': 'Kandic/oxic horizons; Oxic Dystrudepts KFGV (cap. 3).',
    'CICE de la arcilla': 'Kandic/oxic horizons; método y correcciones (cap. 3).',
    'Conductividad eléctrica': 'Salic horizon: extracto de pasta saturada (cap. 3).',
    'Saturación de bases': 'Mollic/umbric epipedons; separación de taxones; especificar método (cap. 3; KFGW).',
    'Saturación de Na': 'Natric horizon; porcentaje de sodio intercambiable y método (cap. 3).',
    'Relación de adsorción de sodio (SAR)': 'Natric horizon y criterios sódicos cuando la clave lo admita. Registrar extracto, unidades de Na/Ca/Mg y fórmula; no equivale al porcentaje de Na intercambiable (Keys 2022, cap. 3).',
    'Densidad aparente': 'Andic soil properties; condición de retención 33 kPa cuando se exige (cap. 3; KFGF–KFGH).',
    'Retención de P': 'Andic soil properties; método de retención, no P extraíble (cap. 3).',
    'Al oxalato': 'Andic soil properties/spodic materials; oxalato de amonio (cap. 3; KFGF–KFGI/KFGU).',
    'Fe oxalato': 'Andic soil properties/spodic materials; oxalato de amonio (cap. 3; KFGF–KFGI/KFGU).',
    'Vidrio volcánico': 'Andic soil properties y subgrupos vitrandic; fracción 0,02–2 mm cuando se exige (cap. 3; KFGF/KFGI).',
    'Retención agua 1500 kPa': 'Oxic Dystrudepts KFGV; registrar base y método.',
    'ODOE': 'Spodic materials; densidad óptica del extracto de oxalato (cap. 3; KFGU).',
    'COLE': 'Extensibilidad; no equivale a extensibilidad lineal integrada en cm (cap. 3; HCGC/KFGC).',
}

DIAGNOSTIC_ENGLISH = dict(zip([
    'Epipedón mólico', 'Epipedón úmbrico', 'Epipedón ócrico', 'Epipedón hístico',
    'Epipedón fólico', 'Epipedón melánico', 'Epipedón antrópico', 'Epipedón plaggen',
    'Horizonte argílico', 'Horizonte kándico', 'Horizonte nátrico', 'Horizonte cámbico',
    'Horizonte óxico', 'Horizonte espódico', 'Horizonte cálcico', 'Horizonte petrocálcico',
    'Horizonte gípsico', 'Horizonte petrogypsic', 'Horizonte sálico', 'Horizonte sulfúrico',
    'Fragipán', 'Duripán', 'Horizonte plácico', 'Horizonte sómbrico (sombric)',
    'Horizonte glósico', 'Horizonte ágrico', 'Propiedades frágicas', 'Propiedades ándicas',
    'Materiales espódicos', 'Materiales álbicos', 'Plintita', 'Petroplintita',
    'Propiedades vérticas', 'Condiciones ácuicas', 'Permafrost', 'Crioturbación',
], ['Mollic epipedon', 'Umbric epipedon', 'Ochric epipedon', 'Histic epipedon',
    'Folistic epipedon', 'Melanic epipedon', 'Anthropic epipedon', 'Plaggen epipedon',
    'Argillic horizon', 'Kandic horizon', 'Natric horizon', 'Cambic horizon',
    'Oxic horizon', 'Spodic horizon', 'Calcic horizon', 'Petrocalcic horizon',
    'Gypsic horizon', 'Petrogypsic horizon', 'Salic horizon', 'Sulfuric horizon',
    'Fragipan', 'Duripan', 'Placic horizon', 'Sombric horizon', 'Glossic horizon',
    'Agric horizon', 'Fragic soil properties', 'Andic soil properties',
    'Spodic materials', 'Albic materials', 'Plinthite', 'Ironstone: documentar cementación; no equivale automáticamente a petroferric contact',
    'Vertic subgroup criteria: cracks, slickensides, linear extensibility',
    'Aquic conditions', 'Permafrost', 'Cryoturbation']))

HORIZON_USES = {}
for names, use in [
    (['Horizonte', 'Techo (cm)', 'Base (cm)', 'Métodos / muestra / observaciones'], 'Designaciones y trazabilidad de intervalos: caps. 4 y 18; profundidad de referencia según cada clave.'),
    (['Arena (%)', 'Limo (%)', 'Arcilla (%)', 'Clase textural USDA', 'Fragmentos (%)'], 'Textura/partículas: caps. 3 y 17; HCGE/HCGJ–HCGL, KFGF/KFGI/KFGR. Las subclases de arena y la granulometría de familia requieren mediciones adicionales.'),
    (['Color húmedo (Munsell)', 'Color seco (Munsell)'], 'Epipedons y rasgos redox, cap. 3; HCGD–HCGF/HCGN, KFGA/KFGM/KFGY. Evaluar preparación y humedad requeridas.'),
    (['Estructura', 'Películas de arcilla'], 'Argillic/cambic/natric horizons, cap. 3; no se deduce el diagnóstico solo de la designación Bt/Bw.'),
    (['Rasgos redox'], 'Aquic conditions, cap. 3; HCGD–HCGF, KFGF/KFGJ/KFGL–KFGN.'),
    (['Carbono orgánico (%)'], LAB_USES['Carbono orgánico']),
    (['pH H2O', 'pH KCl'], 'Reacción del suelo y método exigido por la definición: cap. 3. No convertir pH KCl en pH H2O.'),
    (['SB suma cationes (%)', 'SB NH4OAc pH 7 (%)'], LAB_USES['Saturación de bases']),
    (['CIC NH4OAc (cmolc/kg suelo)', 'CIC (cmolc/kg arcilla)', 'CICE (cmolc/kg arcilla)'], 'Kandic/oxic horizons y saturación: cap. 3; KFGV. Conservar base, extractante y correcciones.'),
    (['Densidad aparente (g/cm³)', 'Retención de P (%)', 'Al oxalato (%)', 'Fe oxalato (%)', 'Vidrio volcánico (%)'], 'Andic soil properties/spodic materials, cap. 3; KFGF–KFGI/KFGU. Métodos y fracción según entrada.'),
    (['CaCO3 equivalente (%)', 'Yeso (%)', 'CE extracto saturado (dS/m)', 'Na intercambiable (%)'], 'Calcic/gypsic/salic/natric horizons, cap. 3; una concentración aislada no confirma el diagnóstico.'),
    (['COLE', 'Slickensides (%)'], 'Rasgos vérticos: cap. 3; HCGC/KFGC. Medir también grietas, espesor y extensibilidad integrada.'),
    (['Nódulos / plintita (%)'], 'Plinthite, cap. 3: distinguir plintita de otros nódulos; documentar abundancia y comportamiento.'),
    (['Retención agua 1500 kPa (%)'], LAB_USES['Retención agua 1500 kPa']),
    (['ODOE'], LAB_USES['ODOE']),
]:
    HORIZON_USES.update(dict.fromkeys(names, use))

EXTRA_USES = {
    'Pendiente': 'KFGL/KFGS/KFGT: pendiente del terreno, porcentaje de desnivel/distancia horizontal; puede superar 100 %.',
    'Material transportado por humanos: espesor': 'KFGE/KFGL/KFGS/KFGT: human-transported material; espesor y posición.',
    'Saturación: máximo de días consecutivos en años normales': 'HCGH/KFGG/KFGO: duración en años normales y profundidad.',
    'Saturación: días acumulados en años normales': 'HCGH/KFGG/KFGO: acumulado del mismo período evaluado.',
    'Extensibilidad lineal integrada': 'HCGC/KFGC: extensibilidad en cm integrada en la sección exigida; no COLE.',
    'Capa con grietas: espesor': 'HCGC/KFGC: espesor con grietas del ancho requerido.',
    'Capa con slickensides o cuñas: techo': 'HCGC/KFGC: límite superior respecto a superficie mineral.',
    'Capa con slickensides o cuñas: espesor': 'HCGC/KFGC: espesor de capa; documentar la presencia de slickensides/cuñas.',
    'Propiedades frágicas: volumen': 'HCGD/HCGG/KFGJ/KFGP: volumen con fragic soil properties.',
    'Propiedades frágicas: techo': 'HCGD/HCGG/KFGJ/KFGP: profundidad del límite superior.',
    'Propiedades frágicas: espesor': 'HCGD/HCGG/KFGJ/KFGP: espesor de capa evaluada.',
    'Materiales orgánicos: espesor': 'Caps. 2, 3 y 10: organic soil materials y epipedons; documentar naturaleza y posición.',
    'Fibras después de frotamiento': 'Cap. 10: fibric/hemic/sapric soil materials; método y volumen tras frotamiento.',
}

def evidence_fingerprint(report):
    """Exclude administrative metadata and all computed outcomes."""
    fields = ('referencia', 'profundidad_cm', 'origen_profundidades', 'contacto',
              'profundidad_contacto_cm', 'regimen_humedad', 'regimen_temperatura',
              'temperatura_media_suelo_c', 'diferencia_estacional_c', 'evidencia_regimenes',
              'horizontes', 'diagnosticos', 'saturacion', 'profundidad_saturacion_cm',
              'duracion_saturacion_dias', 'reduccion', 'evidencia_redox',
              'grietas_ancho_mm', 'grietas_profundidad_cm', 'grietas_duracion_dias',
              'otros_rasgos', 'medidas_adicionales', 'laboratorio')
    payload = {key: report.get(key) for key in fields}
    payload['ruta'] = report.get('ruta', [])[:3]
    descriptions = {uid: r for uid, r in report.get('descripcion_asistida', {}).get('horizontes', {}).items() if any(v not in (None, '') for v in r.values())}
    if descriptions:
        payload['descripcion_horizontes'] = descriptions
    site = report.get('descripcion_asistida', {}).get('sitio', {})
    site_evidence = {k: v for k, v in site.items() if k != 'elevacion_m' and v not in (None, '')}
    if site_evidence:
        payload['sitio_evidencia'] = site_evidence
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def validate_extra(rows, depth):
    errors, pending, values = [], [], {}
    for row in rows:
        name, value, unit = row.get('Parámetro', ''), row.get('Valor'), row.get('Unidad')
        if value is None:
            continue
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            errors.append(f'{name}: valor no válido.')
            continue
        values[name] = value
        # Slope percent is rise/run, and may legitimately exceed 100%.
        if unit == '%' and name != 'Pendiente' and value > 100:
            errors.append(f'{name}: debe estar entre 0 y 100 %.')
        if unit == 'días' and (value > 366 or value != int(value)):
            errors.append(f'{name}: debe ser un número entero entre 0 y 366 días.')
        if unit == 'cm' and name != 'Extensibilidad lineal integrada' and depth is not None and value > depth:
            errors.append(f'{name}: supera la profundidad observada.')
        if not str(row.get('Intervalo / método / evidencia') or '').strip():
            pending.append(f'{name}: documentar intervalo, método y criterio USDA.')
    consecutive = values.get('Saturación: máximo de días consecutivos en años normales')
    cumulative = values.get('Saturación: días acumulados en años normales')
    if consecutive is not None and cumulative is not None and consecutive > cumulative:
        errors.append('Saturación: los días consecutivos no pueden superar los acumulados del mismo período.')
    for prefix in ('Capa con slickensides o cuñas', 'Propiedades frágicas'):
        top, thickness = values.get(prefix + ': techo'), values.get(prefix + ': espesor')
        if top is not None and thickness is not None and depth is not None and top + thickness > depth:
            errors.append(f'{prefix}: techo + espesor supera la profundidad observada.')
    return errors, pending

def determination(manual, guide, errors, pending):
    assisted = (guide or {}).get('subgroup')
    conflict = bool(manual and assisted and manual.strip().casefold() != assisted.strip().casefold())
    if conflict:
        status = 'Determinación pendiente: discrepancia entre ruta manual y clave guiada'
    elif errors:
        status = 'Determinación bloqueada por inconsistencias de las evidencias'
    elif pending or (guide or {}).get('requires_review'):
        status = 'Determinación pendiente: completar o revisar evidencias'
    elif assisted:
        status = 'Subgrupo por clave asistida; condicionado a la evidencia declarada'
    elif manual:
        status = 'Subgrupo documentado por el usuario; pendiente de validación taxonómica independiente'
    else:
        status = 'Subgrupo pendiente: completar la ruta taxonómica'
    adopted = None if conflict or errors or pending or (guide or {}).get('requires_review') else assisted or manual
    return {'estado': status, 'subgrupo_manual': manual, 'subgrupo_asistido': assisted,
            'subgrupo_adoptado': adopted, 'discrepancia': conflict,
            'alcance': 'Documentación hasta subgrupo; no certificación taxonómica independiente.'}
