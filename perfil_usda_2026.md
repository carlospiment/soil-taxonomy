# Perfil USDA: alcance, validación y resultados

Actualización: 2026-09-10. Referencia fija: Soil Survey Staff, *Keys to Soil
Taxonomy*, 13th edition, 2022. No se mezclan criterios de ediciones distintas.

## Alcance y referencias

- [Publicación oficial USDA–NRCS](https://www.nrcs.usda.gov/resources/guides-and-instructions/keys-to-soil-taxonomy).
- [PDF USDA](https://www.nrcs.usda.gov/sites/default/files/2022-09/Keys-to-Soil-Taxonomy.pdf).
- [Copia gubernamental utilizada para el cotejo](https://www.govinfo.gov/content/pkg/GOVPUB-A57-PURL-gpo224020/pdf/GOVPUB-A57-PURL-gpo224020.pdf).

El objetivo es registrar evidencias, recorrer las claves y documentar un subgrupo.
La captura general no es un clasificador automático para todos los órdenes.
Hapludults y Dystrudepts tienen guías; las demás rutas requieren consultar la clave
oficial y transcribir la determinación. No se ofrecen recomendaciones de fertilización.

`taxonomy_scope.py` contiene la correspondencia de los 36 campos de horizontes,
los 13 parámetros adicionales y el catálogo de laboratorio con funciones y
referencias USDA. La misma correspondencia se muestra en la interfaz y sus ayudas.
Las referencias son usos posibles: no hacen obligatoria toda medición para todo perfil.

| Información | Función y referencia |
| --- | --- |
| Identificador, responsable, fecha, ubicación y fotos | Trazabilidad del pedón y las observaciones; no determinan un taxón. |
| Designación y profundidades | Caps. 4 y 18; conservar el origen exigido por la entrada. |
| Textura, color, estructura y películas | Evidencia para diagnósticos y rasgos diferenciales, cap. 3. La designación Bt o Bw no confirma un diagnóstico. |
| Química y propiedades físicas | Métodos, fracción y sección exigidos por cap. 3 y la clave elegida; no convertir métodos entre sí. |
| Humedad, temperatura, reducción y saturación | Cap. 3; separar regímenes, condiciones ácuicas y duración observada. |
| Medidas adicionales | Criterios de subgrupos: grietas, extensibilidad, propiedades frágicas, saturación, pendiente, materiales transportados y orgánicos. |
| Ruta manual y guía | Cap. 4 y clave del orden: primera alternativa aplicable, exclusión documentada de anteriores. |

Los nombres oficiales de los taxones permanecen en inglés. La tabla de equivalencias
aclara los términos españoles y la tabla editable muestra los términos USDA.
«Propiedades vérticas» es una agrupación de rasgos;
«Petroplintita», conservado como identificador histórico, debe documentarse como
cementación por hierro y contrastarse con la definición USDA pertinente. No se
equipara automáticamente a un contacto petroférrico.

## Laboratorio taxonómico

La captura excluye categorías agronómicas (bajo/medio/alto), pH tampón, nutrientes
extraíbles para fertilidad y relaciones como Ca/K. Conserva carbono orgánico,
textura, carbonatos, yeso, intercambio, saturación de bases/sodio, conductividad,
densidad y determinaciones ándicas/espódicas pertinentes.

Cada resultado necesita muestra, intervalo, informe, método, unidad, base de reporte
y criterio USDA/página. pH requiere relación suelo:solución; intercambio y saturación
necesitan denominador o fórmula cuando corresponda. La aplicación detecta faltantes
y compatibilidad numérica; la adecuación científica del método debe revisarse contra
la definición completa. No inventa relaciones entre tablas ni copia automáticamente
una medición del laboratorio a un horizonte.

Los registros antiguos fuera del catálogo y las filas originales con interpretación
agronómica se conservan en `laboratorio_historico_no_taxonomico`. No intervienen en
la determinación. Se incluyen en los respaldos y tienen descarga propia fuera de la
primera pestaña. Una medición taxonómica de una fila antigua puede conservarse en la
captura, mientras la fila original con su interpretación permanece en el histórico.

## Validación y decisiones

- Errores de laboratorio, intervalos y medidas adicionales llegan al informe y
  bloquean la adopción del subgrupo. ND o unidad/base sin resolver quedan pendientes.
- Volúmenes/fracciones adicionales: 0–100 %. Pendiente del terreno puede superar
  100 % porque expresa desnivel/distancia horizontal. Días: enteros 0–366.
- Se revisan techo + espesor, profundidad observada y días consecutivos/acumulados.
- Un horizonte sin identificar produce un pendiente. La ausencia declarada de un
  diagnóstico requiere evidencia. Los diagnósticos no evaluados no se consideran ausentes.
- Los faltantes administrativos se muestran como documentación incompleta; no son
  criterios taxonómicos ni borran decisiones.
- Cambiar responsable, fecha, identificador, ubicación o descripción de fotos no
  invalida las evaluaciones. Cambiar mediciones o evidencias taxonómicas conserva
  los textos y exige confirmar su revisión. La guía revisa conservadoramente todo
  el recorrido: todavía no calcula dependencias individuales de cada requisito.
- También se conserva y marca para revisión la ruta manual con propuesta existente.
- Un desacuerdo entre subgrupo manual y asistido deja el subgrupo adoptado pendiente.
  Debe corregirse la ruta o la guía con evidencia; no basta elegir uno y ocultar el otro.

## Cotejo de las guías

Se cotejaron los 15 códigos HCGA–HCGO (Hapludults, pp. 330–331) y los 26 códigos
KFGA–KFGZ (Dystrudepts, pp. 224–227) contra el PDF gubernamental. Los 41 textos,
códigos y nombres coinciden tras normalizar espacios y saltos de línea; se inspeccionaron
las seis páginas renderizadas. Se conserva la nota de HCGA, y las entradas que
continúan en la página siguiente conservan su texto completo. Cada entrada enlaza
su página inicial. Se mantienen los AND/OR, las excepciones, el orden y Typic como
salida residual tras excluir las anteriores.

Este cotejo verifica la transcripción, no valida diagnósticos de pedones reales ni
implementa automáticamente todas las definiciones citadas por las claves.

## Presentación y archivos

La tabla de horizontes ofrece vistas de campo, textura y mediciones, conservando
los datos ocultos. Las fotos recuperadas admiten descripción y exclusión reversible.
El resumen inicial y la conclusión usan el mismo informe: estado, pendientes,
contradicciones, último nivel documentado y subgrupos manual/asistido/adoptado.

- JSON: ficha y evidencias, sin bytes de imágenes originales.
- ZIP de ficha: añade fotos del perfil.
- ZIP de estudio completo: respaldo editable con originales e historial de análisis.

Los borradores con resultados de laboratorio inválidos pueden guardarse y reabrirse
sin perder valores originales. La validación de estructura del archivo sigue activa;
al abrir, la interfaz vuelve a evaluar las evidencias y mantiene el bloqueo científico.
La condición de revisión pendiente y los textos de las decisiones se conservan en ZIP.

## Pruebas

`test_taxonomy_scope.py` cubre catálogo, referencias, validación, discrepancias,
conservación de decisiones, cambios administrativos, revisión tras modificar
mediciones, alternancia de guías, históricos agronómicos, borradores, fotos y vistas.
`test_soil_profile.py` comprueba además la precedencia y la exclusión de alternativas.
Los casos son sintéticos; no equivalen a validación taxonómica independiente.

En este equipo se utiliza el entorno funcional:

```powershell
.\tmp\lab-check-env\Scripts\python.exe -m unittest discover -p 'test_*.py' -q
```

Resultado de esta actualización: 59 pruebas de perfil, laboratorio, almacenamiento,
textura/fotos, alcance USDA y dashboard pasaron después del último cambio.
La ejecución ampliada anterior pasó 100 de 101 pruebas; la restante,
`test_wire_payload_matches_installed_sdk`, no pudo ejecutarse por ausencia de
`inference_sdk` en el entorno de pruebas (pestaña de estructura, fuera de este cambio).
