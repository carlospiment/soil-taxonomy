# Captura normalizada de análisis de suelo

Consulta: 2026-09-09. Revisión de servicios y procedimientos de laboratorios; no es un ranking estadístico mundial de frecuencia.

## Resultados recurrentes

- Núcleo de fertilidad: pH, P, K, Ca, Mg y micronutrientes Zn, Mn, Cu y Fe. B aparece en algunos paquetes.
- Caracterización y paquetes ampliados: materia orgánica, conductividad eléctrica, CIC, saturación de bases, Na, N nítrico y S como sulfato.
- Suelos ácidos tropicales: acidez y Al intercambiables, CICE y relaciones entre bases.
- Según objetivo: carbono orgánico, N total/amoniacal, textura, densidad aparente, carbonatos y yeso. No todos forman parte de un análisis rutinario.

Fuentes primarias:

1. [Virginia Tech: procedimientos de laboratorio](https://www.pubs.ext.vt.edu/452/452-881/452-881.html). Lista de análisis rutinarios y especiales; detalla pH agua 1:1, extracción Mehlich 1 y materia orgánica por pérdida por ignición. Sustenta la necesidad de conservar método, extractante y relación de extracción.
2. [Colorado State University: servicios](https://agsci.colostate.edu/soiltestinglab/soil-services/). Paquete completo con pH, CE, materia orgánica, CIC, bases, N nítrico, P, K, Ca, Mg, Na, sulfato y micronutrientes.
3. [Agroanálisis, Costa Rica: suelos](https://www.agroanalisiscr.com/suelos.html). Rutina con pH, acidez, Ca, Mg, K, P, Cu, Fe, Zn y Mn; aporta contexto regional tropical.
4. [FAO/GLOSOLAN: informe de armonización](https://openknowledge.fao.org/3/cb2557en/cb2557en.pdf). Armonización de métodos y unidades de carbono y bases intercambiables.

## Reglas implementadas

Una fila por determinación, con muestra, horizonte/intervalo, profundidades, laboratorio/informe, fecha, parámetro, resultado original, unidad, base de reporte, método, relación suelo:solución, denominador/fórmula, estado y observaciones. El catálogo incluye todos los parámetros del informe compartido; Ca+Mg se distingue de (Ca+Mg)/K.

Se conservan comas decimales, límites (<, >, <=, >=) y ND. Vacío/ND no se transforma en cero. Solo se normalizan unidades dimensionalmente equivalentes: meq/100 g a cmolc/kg sobre la misma fracción, g/kg a %, µS/cm o mS/cm a dS/m. ppm requiere confirmación explícita de masa de suelo seco para representarlo como mg/kg. Se preservan datos pendientes sin inventar unidades.

No se convierten métodos analíticos, masa/volumen, extracto/suelo, materia orgánica/carbono, CIC de suelo/arcilla ni P extraíble/retención de P. Resultados extraíbles y cationes intercambiables tienen entradas diferenciadas. N-NO3 y S-SO4 se expresan como elemento, no como masa del ion completo.

Las saturaciones y relaciones se capturan como reportadas con denominador/fórmula. K% puede significar K/CIC, K/CICE o K/suma de bases: no se calcula con una suposición. Los estados agronómicos son transcritos; no se derivan umbrales universales ni recomendaciones de fertilización.

La tabla se guarda en JSON y ZIP y se recupera al abrir el estudio. Los estudios antiguos sin laboratorio siguen siendo compatibles. Los valores normalizados se recalculan a partir de originales, sin sustituirlos. No se copian automáticamente al formulario taxonómico; allí deben respetarse los métodos exigidos por la clave.

## Uso con el informe compartido

En Perfil y subgrupo → 2b. Análisis de laboratorio y fertilidad, añade una fila por resultado. Repite el identificador de muestra en sus determinaciones; usa otro identificador para otra muestra. Las filas se pueden pegar desde una hoja de cálculo respetando las columnas del editor.

- pH 5.13: parámetro pH, sin unidad; confirmar extractante y relación suelo:solución.
- Materia orgánica 3.96: %, sin trasladarlo a carbono orgánico.
- P 0.02, Zn 1.54, Mn 66.92, Fe 33.11, Cu 0.7: parámetros extraíbles; ppm; confirmar reporte sobre masa de suelo seco para normalizar a mg/kg.
- K 0.32, Ca 3.47, Mg 0.69 y Al 3.8: entradas intercambiables si el laboratorio confirma esa fracción; meq/100 g suelo cuando esa sea la base declarada.
- Acidez intercambiable 4 y CICE 8.48: unidad No informada hasta confirmar la unidad omitida en la imagen. CICE del suelo y CICE de arcilla son entradas distintas.
- SatBases 52.83 y K% 7.14: saturación de bases y saturación de K; registrar el denominador del laboratorio antes de interpretar.
- Ca/K 10.84, Mg/K 2.16, Ca/Mg 5.03 y (Ca+Mg)/K 13: relaciones sin unidad.
- La fila rotulada Ca+Mg con valor 4.48 debe conservarse con observación: confirmar su definición con el laboratorio. Con los valores visibles, Ca+Mg es 4.16 y Ca+Mg+K es 4.48; no corregir silenciosamente el informe.

La aplicación no precarga estas cifras como mediciones reales: faltan la identificación, profundidades y métodos de la muestra.
