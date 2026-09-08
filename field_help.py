"""Ayudas breves para iconos y encabezados de tablas."""
HELP = {
    "profile_id": "Código único del pedón o sitio; úsalo también en las muestras y fotografías.",
    "profile_observer": "Nombre de quien realizó la descripción; la fecha se registra por separado.",
    "profile_date": "Fecha de la descripción o muestreo en campo. Déjala vacía si no está documentada.",
    "profile_depth": "Profundidad máxima realmente observada, no la profundidad estimada del suelo.",
    "profile_reference": "Punto cero desde el que se midieron los intervalos. Todas las tablas deben usar el mismo origen.",
    "profile_contact": "Lítico: roca coherente; paralítico: material rocoso alterado; dénsico: material restrictivo muy denso. Confirma la definición USDA.",
    "profile_contact_depth": "Distancia desde el origen elegido hasta el contacto limitante identificado.",
    "profile_moisture": "Disponibilidad y duración del agua en la sección de control. No equivale a la lluvia anual ni al drenaje.",
    "profile_temperature": "Régimen térmico del suelo verificado a la profundidad y con los criterios de la clave.",
    "profile_mean_temp": "Promedio anual medido o sustentado del suelo, no del aire. Documenta la profundidad.",
    "profile_seasonal_temp": "Diferencia entre temperaturas medias estacionales del suelo; registra el método y período.",
    "profile_climate_evidence": "Anota profundidad, sección de control de humedad, años de observación y fuente de las mediciones.",
    "profile_saturation": "Endosaturación: saturación continua en profundidad; episaturación: agua sobre una capa no saturada. Revisa los criterios completos.",
    "profile_water_depth": "Profundidad donde se comprobó saturación con agua y fecha/período de observación.",
    "profile_water_days": "Días observados durante el año; separa más abajo los consecutivos y los acumulados de años normales.",
    "profile_reduction": "La presencia de agua por sí sola no demuestra reducción. Registra prueba o rasgos diagnósticos.",
    "profile_redox_notes": "Describe colores Munsell, abundancia y localización de depleciones y concentraciones de Fe/Mn.",
    "profile_cracks_width": "Abertura de las grietas en milímetros, indicando las condiciones de humedad.",
    "profile_cracks_depth": "Profundidad hasta la que se observan las grietas; no es el espesor de la capa con grietas.",
    "profile_cracks_days": "Tiempo de apertura de las grietas durante el año; documenta cómo se estimó.",
    "profile_other": "Registra los rasgos exigidos por la clave que no tienen una columna específica, con profundidad y método.",
}
COLUMNS = {
    "Horizonte": "Designación de campo (A, Bt, Bw...) o código del intervalo; no confirma un horizonte diagnóstico.",
    "Techo (cm)": "Profundidad del límite superior respecto al origen seleccionado.",
    "Base (cm)": "Profundidad del límite inferior; debe ser mayor que el techo.",
    "Arena (%)": "Porcentaje en masa de arena (2 a 0,05 mm) en la tierra fina. Con dos fracciones se calcula la tercera.",
    "Limo (%)": "Porcentaje en masa de limo (0,05 a 0,002 mm) en la tierra fina.",
    "Arcilla (%)": "Porcentaje en masa de partículas menores de 0,002 mm. No representa mineralogía de arcillas.",
    "Clase textural USDA": "Resultado automático de arena, limo y arcilla; requiere una suma de 100 %.",
    "Fracción calculada": "Indica cuál porcentaje se obtuvo por diferencia a 100, no mediante medición independiente.",
    "Fragmentos (%)": "Fragmentos mayores de 2 mm; documenta si es porcentaje en volumen o masa. No entra en la suma textural.",
    "Color húmedo (Munsell)": "Notación completa: matiz, valor y croma; por ejemplo 10YR 3/2, en la condición requerida.",
    "Color seco (Munsell)": "Color Munsell en seco; registra la preparación de la muestra (mezclada, triturada, etc.).",
    "Estructura": "Tipo, tamaño y grado de los agregados del suelo.",
    "Películas de arcilla": "Ubicación y abundancia de revestimientos; distingue películas de caras de presión.",
    "Rasgos redox": "Depleciones y concentraciones, colores, abundancia, contraste y localización.",
    "Carbono orgánico (%)": "Carbono orgánico medido; no es el porcentaje de materia orgánica. Documenta el método.",
    "pH H2O": "pH medido en agua; registra la relación suelo:solución.",
    "pH KCl": "pH medido en KCl; no es intercambiable con el pH en agua.",
    "SB suma cationes (%)": "Saturación de bases por suma de cationes. Usa el método y profundidad exigidos por la clave.",
    "SB NH4OAc pH 7 (%)": "Saturación de bases con acetato de amonio a pH 7; no mezclar con el método por suma de cationes.",
    "CIC NH4OAc (cmolc/kg suelo)": "Capacidad de intercambio catiónico por kg de suelo, medida con NH4OAc a pH 7.",
    "CIC (cmolc/kg arcilla)": "CIC expresada por kg de arcilla, aplicando las correcciones del método; no por kg de suelo.",
    "CICE (cmolc/kg arcilla)": "Capacidad de intercambio efectiva por kg de arcilla; documenta método y correcciones.",
    "Densidad aparente (g/cm³)": "Masa seca por volumen. Las claves ándicas pueden exigir medición a 33 kPa; registra la condición.",
    "Retención de P (%)": "Porcentaje de fósforo retenido según el método de laboratorio exigido.",
    "Al oxalato (%)": "Aluminio extraído con oxalato de amonio, sobre la fracción indicada en el método.",
    "Fe oxalato (%)": "Hierro extraído con oxalato de amonio; no es hierro total.",
    "Vidrio volcánico (%)": "Contenido de vidrio; especifica la fracción granulométrica y base del porcentaje.",
    "CaCO3 equivalente (%)": "Carbonatos expresados como equivalente de carbonato de calcio.",
    "Yeso (%)": "Contenido de yeso medido; no basta para confirmar un horizonte gípsico.",
    "CE extracto saturado (dS/m)": "Conductividad eléctrica del extracto de pasta saturada; no de otra dilución.",
    "Na intercambiable (%)": "Porcentaje de sodio intercambiable; documenta el denominador y método.",
    "COLE": "Coeficiente de extensibilidad lineal, adimensional. No equivale a extensibilidad integrada en cm.",
    "Slickensides (%)": "Abundancia de superficies de deslizamiento; documenta base del porcentaje y espesor de la capa.",
    "Nódulos / plintita (%)": "Identifica el material y base del porcentaje. Los nódulos no son automáticamente plintita.",
    "Retención agua 1500 kPa (%)": "Agua retenida a 1500 kPa, según método y base de masa del laboratorio.",
    "ODOE": "Densidad óptica del extracto de oxalato; documenta el procedimiento analítico.",
    "Métodos / muestra / observaciones": "Identificador de muestra, métodos, unidades de referencia y observaciones que sustentan los resultados.",
    "Diagnóstico": "Horizonte o propiedad a verificar con su definición completa en las claves USDA.",
    "Estado": "No evaluado no equivale a ausente. Marca presente solo con evidencia suficiente.",
    "Evidencia / método / criterio": "Cita observaciones, análisis y requisito de la clave que sustenta el diagnóstico.",
    "Nivel": "Posición en la jerarquía: orden, suborden, gran grupo o subgrupo.",
    "Taxón": "Nombre oficial de la clase determinada en ese nivel.",
    "Clave / página": "Código de entrada y página de la edición de 2022 consultada.",
    "Evidencia y exclusión de anteriores": "Explica por qué cumple esta entrada y por qué no cumple las anteriores.",
    "Revisión": "Confirma el cumplimiento solo después de evaluar todas las entradas anteriores de ese nivel.",
    "Parámetro": "Medida adicional necesaria para distinguir criterios de las claves.",
    "Unidad": "Unidad del valor solicitado. No intercambies porcentajes, cm, mm y días.",
    "Valor": "Medida del parámetro de esta fila; deja vacío si no se evaluó.",
    "Intervalo / método / evidencia": "Intervalo de profundidad, período de observación, método y fuente del dato.",
}


def help_for(key):
    return HELP.get(key, "Registra la observación y su evidencia; deja vacío si no se evaluó.")


def column_help(name):
    return COLUMNS.get(name, "Registra la información observada, con sus unidades y método.")


def table_help(names, configs=None):
    configs = configs or {}
    return {name: {**configs.get(name, {}), "help": column_help(name)} for name in names}
