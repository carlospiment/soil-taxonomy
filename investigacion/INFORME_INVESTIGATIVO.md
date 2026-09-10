# Desarrollo de una plataforma para la descripción y clasificación asistida de suelos

## Informe técnico científico y guía para una investigación publicable

**Proyecto:** Soil Taxonomy — aplicación en Python y Streamlit.  
**Fecha de revisión:** 9 de septiembre de 2026.  
**Versión del documento:** 1.0.  
**Autoría, afiliación, sitios de estudio y revista de destino:** por completar por el investigador.  
**Estado:** prototipo funcional con verificación de software; validación independiente de campo pendiente.

Este informe documenta las funciones integradas en el proyecto, sus fundamentos y las decisiones metodológicas que requieren investigación adicional. Se elaboró a partir del código local, la documentación del proyecto, la información aportada por su responsable y una consulta dirigida de fuentes primarias e institucionales. No es una revisión sistemática ni un artículo con resultados experimentales de campo. Las referencias respaldan los conceptos y antecedentes; no certifican la precisión de esta aplicación.

La conclusión central es que se dispone de una plataforma que organiza evidencias pedológicas, cálculos texturales, estimaciones visuales y revisión humana con recuperación de estudios. El paso pendiente para sustentar afirmaciones de desempeño es evaluarla con muestras nuevas, referencias independientes y un diseño definido antes de analizar los resultados.

## Resumen

Se desarrolló un prototipo de apoyo a la descripción de perfiles de suelo y a la documentación de decisiones taxonómicas. La plataforma integra una ficha por horizontes, controles de consistencia, cálculo de clases texturales, coordenadas y fotografías, claves guiadas para dos grandes grupos, aprendizaje automático con datos tabulares, consulta de un flujo remoto de análisis estructural y estimación orientativa del color Munsell. El módulo cromático combina selección de una región de interés, indicadores de calidad, gestión de color, conversión a espacios colorimétricos y búsqueda discreta en datos de renotación. Incluye una corrección opcional con referencia neutra, cuyo alcance es parcial y experimental. Las propuestas se conservan separadas de los valores revisados; aplicar un color al perfil requiere una acción humana explícita. El almacenamiento en ZIP permite recuperar fotografías, cálculos y revisiones. La revisión local del 9 de septiembre de 2026 registró 86 pruebas automatizadas satisfactorias. No se dispone de una estimación independiente de exactitud taxonómica, cromática o estructural. El responsable declaró cuatro capturas de un libro utilizadas en el entrenamiento de estructura, que no constituyen un conjunto independiente de evaluación. Se propone una investigación posterior con captura mediante iPhone 15 Pro, referencias de campo ciegas y separación de datos por perfil o sitio.

**Palabras clave:** descripción pedológica; Soil Taxonomy; color Munsell; estructura del suelo; fotografía digital; aprendizaje automático; trazabilidad; validación independiente.

## 1 Planteamiento del problema

El desarrollo parte de una necesidad operativa del proyecto: reunir datos de campo, fotografías, mediciones y decisiones en una ficha recuperable. El problema de investigación consiste en determinar si esa integración mejora la documentación y ofrece estimaciones visuales útiles bajo condiciones de captura conocidas. La existencia de una interfaz que produce resultados no permite inferir que esos resultados sean correctos en una población de suelos.

La clasificación asistida se apoya en las *Keys to Soil Taxonomy*, decimotercera edición. La publicación organiza criterios y claves para la clasificación de suelos; en el proyecto se utiliza una edición declarada para evitar mezclar reglas de versiones diferentes. La aplicación organiza el recorrido y la evidencia introducida por el usuario, pero no implementa la totalidad del sistema como un clasificador autónomo. [Soil Survey Staff, 2022](https://www.nrcs.usda.gov/sites/default/files/2022-09/Keys-to-Soil-Taxonomy.pdf).

Para la descripción morfológica, el *Soil Survey Manual* proporciona procedimientos de observación y registro. Es una referencia apropiada para definir cómo se obtendrán los datos de campo que luego se introduzcan en el programa. La comparación experimental debe especificar la propiedad observada, su método de referencia y las condiciones de medición. [Soil Science Division Staff, 2017](https://www.nrcs.usda.gov/resources/guides-and-instructions/soil-survey-manual).

## 2 Objetivos del desarrollo y preguntas de investigación

**Objetivo del desarrollo:** implementar un entorno trazable para registrar perfiles, documentar decisiones taxonómicas e integrar herramientas exploratorias de análisis de datos e imágenes, conservando la intervención del especialista.

Los objetivos específicos implementados son organizar las observaciones por horizonte; comprobar consistencia y precedencia de decisiones; calcular textura a partir de fracciones granulométricas; consultar un modelo externo de estructura; estimar color de una región seleccionada; conservar revisiones; y guardar y recuperar estudios completos.

**Preguntas propuestas para la investigación posterior:**

1. ¿Qué concordancia presenta el color propuesto con referencias independientes, por humedad, dispositivo y condición de iluminación?
2. ¿En qué condiciones la corrección con referencia neutra reduce el error respecto al modo sin corrección?
3. ¿Qué clases estructurales distingue el modelo en fotografías nuevas y cuáles confunde o no detecta?
4. ¿Qué proporción de capturas produce una estimación utilizable y cuáles son las causas de abstención?
5. ¿La ficha asistida mejora la integridad documental y la recuperación de evidencias frente al procedimiento de trabajo previo?

Estas preguntas no tienen respuesta empírica todavía. Si se evalúa la quinta, deberá medirse mediante una comparación específica de tareas, omisiones, tiempo y recuperación; las pruebas unitarias no la resuelven.

## 3 Antecedentes científicos

### 3.1 Fotografía y determinación del color del suelo

Gómez-Robledo y colaboradores estudiaron el uso de un teléfono como sensor de color bajo iluminación controlada, con conversión de imágenes a coordenadas colorimétricas y comparación instrumental. Su trabajo constituye un antecedente de viabilidad, pero utiliza un dispositivo y un procedimiento distintos. No permite asignar sus errores al presente prototipo. [Gómez-Robledo et al., 2013](https://doi.org/10.1016/j.compag.2013.10.002).

Otro estudio comparó cámaras de teléfonos y cartas Munsell utilizando una referencia espectrofotométrica e identificó efectos de la iluminación natural sobre la exactitud. Este antecedente justifica registrar y analizar las condiciones de captura en lugar de agrupar todas las fotografías como si fueran equivalentes. [Fan et al., 2017](https://doi.org/10.2136/sssaj2017.01.0009).

Un estudio publicado en *Sensors* examinó teléfonos y funciones de distancia para asignar colores Munsell, con una referencia instrumental. Sirve como antecedente de búsqueda de colores próximos y de dependencia del dispositivo. Su evaluación de fichas de color no debe confundirse con una validación del presente algoritmo sobre superficies naturales heterogéneas. [Determination of Munsell Soil Colour Using Smartphones, 2023](https://doi.org/10.3390/s23063181).

La investigación sobre placas de referencia junto al objeto fotografiado también ofrece una comparación pertinente para futuras mejoras. Una placa multicolor y un parche neutro único no constituyen el mismo procedimiento; los resultados de ese trabajo no validan automáticamente la corrección diagonal implementada aquí. [Using a Reference Color Plate…, 2025](https://doi.org/10.3390/soilsystems9030093).

### 3.2 Aprendizaje automático y evaluación independiente

Random Forest combina múltiples árboles para producir una predicción. Es el método seleccionado para la pestaña tabular, con parámetros concretos descritos más adelante. La referencia fundacional sustenta la familia algorítmica, no la calidad de los datos que cargue cada usuario. [Breiman, 2001](https://www.stat.berkeley.edu/users/breiman/randomforest2001.pdf).

Los datos ambientales pueden presentar dependencia espacial o jerárquica. Roberts y colaboradores analizan estrategias de validación para esa situación. Aplicado a este proyecto, ello motiva una evaluación por sitios o perfiles, evitando que fotografías relacionadas aparezcan a ambos lados de una partición de entrenamiento y prueba. Esta es una propuesta de diseño; no está implementada en la partición tabular actual. [Roberts et al., 2017](https://doi.org/10.1111/ecog.02881).

## 4 Materiales y arquitectura del prototipo

La evidencia de implementación procede de los archivos del proyecto local. `app.py` organiza cuatro áreas: perfil y subgrupo; predicciones con datos tabulares; estructura; y color. El guardado y la apertura de estudios son funciones transversales. Aunque una pestaña se denomina predicciones geográficas, actualmente procesa una tabla de variables y clases: no implementa por sí sola cartografía predictiva, interpolación espacial ni validación geográfica.

| Componente | Archivos principales | Función y alcance |
|---|---|---|
| Ficha y taxonomía | `profile_ui.py`, `soil_profile.py`, `subgroup_guide.py`, `subgroup_keys.json` | Registro de evidencia y recorrido asistido |
| Textura | `texture.py`, `horizon_editor.py` | Fracción faltante, clase y triángulo |
| Ubicación e imágenes | `field_media.py`, `image_io.py` | Coordenadas, lectura y exportación de originales |
| Aprendizaje tabular | `app.py` | Entrenamiento exploratorio con datos del usuario |
| Estructura | `structure_ui.py`, `soil_structure/` | Inferencia remota y conservación de respuestas |
| Color | `color_ui.py`, `soil_color/` | Región, calidad, colorimetría y corrección neutra |
| Revisión y trazabilidad | `visual_observations.py`, `color_review_ui.py` | Propuestas, revisiones y aplicación explícita |
| Almacenamiento | `study_storage.py`, `storage_ui.py` | ZIP versionado y recuperación |
| Evaluación de campo | `field_validation.py`, `validacion_campo/` | Protocolo, plantillas y métricas descriptivas |

El entorno local observado utilizó Python 3.12.14, Streamlit 1.63.0, NumPy 2.2.6, pandas 3.0.5, scikit-learn 1.9.0, Colour 0.4.6, Pillow 12.3.0, pyproj 3.8.0 e inference-sdk 1.5.2. Estas versiones describen la instalación local, no garantizan equivalencia con el servidor publicado. `requirements.txt` contiene rangos para varias dependencias; una publicación reproducible debe acompañarse de una versión identificable del código y un registro exacto del entorno utilizado.

## 5 Funciones integradas y fundamento metodológico

### 5.1 Ficha pedológica y determinación asistida

La ficha registra identificación, responsable, fecha, profundidad observada, origen de profundidades, contactos, regímenes, horizontes, diagnósticos, condiciones de saturación y reducción, grietas, medidas adicionales y ruta taxonómica. Mantiene datos desconocidos como valores vacíos y diferencia un diagnóstico no evaluado de uno ausente. Conserva las unidades y métodos de las mediciones registradas.

La ruta manual contiene orden, suborden, gran grupo y subgrupo, con evidencia y exclusión de entradas anteriores. Las claves guiadas cubren Hapludults y Dystrudepts, con 15 y 26 salidas respectivamente según el archivo local. Una decisión no evaluada bloquea la continuación concluyente; la salida residual exige documentar las exclusiones. Los cambios en la evidencia invalidan decisiones previas de la guía mediante una huella del contenido.

Las fuentes taxonómicas implementadas corresponden a la edición de 2022; la documentación local identifica las secciones de Hapludults y Dystrudepts. La existencia de una ruta registrada no demuestra que el usuario interpretó correctamente todos los requisitos diagnósticos. Esa diferencia debe mantenerse al presentar el sistema a revisores. [Keys to Soil Taxonomy](https://www.nrcs.usda.gov/resources/guides-and-instructions/keys-to-soil-taxonomy).

### 5.2 Textura y visualización

Si existen dos fracciones válidas, se calcula la tercera como `100 − arena − limo`, o su expresión equivalente. Se conserva cuál fue derivada; editar una medida puede recalcularla, mientras editar directamente la derivada convierte el conjunto en datos manuales. Las sumas inválidas no se normalizan silenciosamente.

Se representan las doce clases texturales y el horizonte seleccionado en un triángulo interactivo. El gráfico caracteriza la distribución granulométrica registrada; no determina por sí solo el subgrupo ni las clases de familia. El fundamento descriptivo está documentado en el capítulo 3 del manual, incluida su figura de clases texturales. [Soil Survey Manual, capítulo 3](https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf).

### 5.3 Coordenadas y fotografías

Se admiten coordenadas geográficas y UTM con zona, hemisferio y datum. La conversión automática de WGS 84/UTM utiliza pyproj; otros datums se conservan sin convertirlos automáticamente. La precisión horizontal declarada se almacena por separado de los decimales mostrados.

Las imágenes se validan por contenido, tamaño y dimensiones. El procesamiento contempla orientación EXIF y conserva hashes de los originales. Los límites de archivos son decisiones operativas para la aplicación, no criterios de calidad científica de una muestra. La fotografía no sustituye las mediciones de laboratorio ni asegura que todos los rasgos relevantes estén visibles.

### 5.4 Predicción con datos tabulares

El usuario carga CSV o Excel, selecciona predictores y una variable objetivo. El programa excluye filas sin etiqueta, impide utilizar el objetivo como predictor y rechaza predictores completamente vacíos. Exige al menos dos clases y dos registros por clase como mínimo operativo, que no constituye un tamaño científicamente suficiente.

El clasificador usa `RandomForestClassifier(n_estimators=100, random_state=42)`. El conjunto de prueba es estratificado, con tamaño `max(número de clases, ceil(0.2 × número de filas))`. La imputación numérica por mediana, la imputación categórica y la codificación de categorías se ajustan dentro de un pipeline sobre entrenamiento. Esta organización sigue el principio de evitar que el preprocesamiento aprenda del conjunto reservado. [Documentación de scikit-learn sobre errores frecuentes](https://scikit-learn.org/stable/common_pitfalls.html).

La interfaz muestra `accuracy`: proporción de etiquetas acertadas en esa partición. En el manuscrito conviene denominarla exactitud global y distinguirla de la precisión por clase. La partición no agrupa automáticamente por sitio, perfil o fecha y no hay ajuste sistemático de hiperparámetros. Las probabilidades mostradas no han sido evaluadas como probabilidades calibradas. La predicción de una etiqueta taxonómica tampoco equivale a resolver una clave diagnóstica.

### 5.5 Análisis experimental de estructura

El módulo envía una imagen a un workflow de Roboflow mediante HTTP, conserva la respuesta y resume detecciones reconocidas con clase y confianza. Distingue resultados vacíos, ausencia de detecciones y formatos no interpretados. La configuración admite una versión de workflow opcional y un umbral de confianza inicial de 0.4. Este valor es una decisión operativa, no un umbral optimizado en un estudio independiente. La API permite ejecutar workflows definidos en el servicio. [Documentación oficial de Roboflow](https://docs.roboflow.com/deploy/serverless-hosted-api-v2/use-with-the-rest-api).

El procesamiento prepara una imagen RGB orientada y la codifica a JPEG para el envío; se conserva el original junto con metadatos del procedimiento. Las detecciones no se convierten automáticamente en tipo, tamaño y grado completos ni se aplican como determinación taxonómica. La respuesta del modelo y la descripción pedológica son objetos que necesitan una correspondencia documentada.

**Procedencia declarada por el responsable:** cuatro imágenes de estructura disponibles en Roboflow son capturas de un libro de edafología, fueron etiquetadas manualmente conforme a las indicaciones del libro y se utilizaron para entrenar. No se ha inspeccionado el dataset privado ni se ha confirmado que esas cuatro imágenes constituyan todo el entrenamiento. Se desconocen aquí el libro, sus páginas, arquitectura exacta, tamaño total del dataset, particiones y configuración completa del entrenamiento.

Esas imágenes pueden servir para demostrar ejecución técnica. No deben presentarse como evaluación externa. Una futura investigación deberá describir su procedencia bibliográfica y documentar las condiciones de uso y reproducción de las figuras. Además, conviene evaluar por separado el paso de imágenes editoriales a fotografías de suelo capturadas en campo; es una posible fuente de cambio de distribución que este proyecto aún no ha cuantificado.

### 5.6 Región de interés e indicadores de calidad del color

El usuario selecciona una región del suelo y exclusiones manuales. El algoritmo no identifica automáticamente piedras, raíces o rasgos redox. Calcula indicadores sobre una muestra de hasta 512 píxeles por lado y obtiene la mediana por canal RGB de los píxeles útiles, en lugar de usar el promedio de toda la fotografía.

Los parámetros iniciales incluyen 1024 píxeles útiles, lado mínimo de 16 píxeles, umbrales de canal 10 y 245, fracciones límite de oscuridad y recorte de 0.20, varianza laplaciana mínima de 15 y desviación RGB máxima de 40. Son umbrales exploratorios del código. Una región oscura puede corresponder a un suelo realmente oscuro; poco detalle puede describir una superficie uniforme. Por ello, las alertas requieren interpretación y no equivalen a un dictamen de calidad científica.

### 5.7 Conversión colorimétrica y propuesta Munsell

La estimación transforma perfiles ICC admitidos a sRGB; cuando no hay perfil y el formato es compatible, declara la suposición sRGB. A partir de la mediana RGB codificada, calcula RGB lineal y XYZ bajo D65. Después aplica adaptación Bradford de D65 a C y obtiene Lab con blanco C y observador de 2 grados. La conversión utiliza Colour 0.4.6. [Documentación de conversión sRGB a XYZ](https://colour.readthedocs.io/en/v0.4.6/generated/colour.sRGB_to_XYZ.html).

El catálogo se construye con `colour.MUNSELL_COLOURS['real']`, complementado con neutros N1 a N9. Se calcula la distancia CIEDE2000 desde el Lab estimado a las entradas y se presentan la más próxima y cuatro alternativas. Se conserva una huella del catálogo. Es una búsqueda discreta, no una interpolación exhaustiva ni una reproducción del inventario de una carta comercial concreta. [Datos Munsell de Colour](https://colour.readthedocs.io/en/v0.4.6/generated/colour.MUNSELL_COLOURS.html); [recursos de renotación del RIT](https://www.rit.edu/science/munsell-color-science-lab-educational-resources).

CIEDE2000 dispone de una formulación y datos de prueba publicados que permiten comprobar implementaciones numéricas. La distancia empleada por el buscador no equivale al error experimental frente al suelo real: para medir ese error haría falta una referencia independiente expresada en condiciones colorimétricas compatibles. [Sharma, Wu y Dalal, 2005](https://doi.org/10.1002/col.20070).

### 5.8 Corrección con referencia neutra

El usuario registra un parche neutro de reflectancia conocida en la misma fotografía. Para cada canal se calcula una ganancia como reflectancia declarada dividida entre la mediana lineal de la referencia; se multiplica el color lineal del suelo por las ganancias y se vuelve a codificar. El código limita reflectancia a 0.02–0.90 y ganancias a 0.25–4. Rechaza referencias inadecuadas y resultados fuera del rango lineal admisible, sin recortarlos silenciosamente.

El alcance es un ajuste diagonal experimental de balance y exposición. No caracteriza la sensibilidad espectral de la cámara, no mide reflectancia del suelo y no sustituye una calibración multicolor. La adaptación Bradford y esta corrección son operaciones diferentes. Su eficacia debe comprobarse comparando, para las mismas muestras independientes, el modo con y sin referencia frente a un patrón externo.

### 5.9 Revisión humana y trazabilidad

Cada observación conserva identidad de perfil y horizonte, hash de imagen, método, versión, contexto, calidad, propuesta y revisiones. Aceptar, corregir o rechazar genera eventos sin sobrescribir la propuesta original. Aplicar un color exige confirmación y modifica únicamente el campo seco o húmedo del horizonte correspondiente.

La aplicación comprueba conflictos de identidad, eliminación del horizonte, cambios en el valor anterior y doble aplicación. Los eventos conservan responsable y fecha, pero el responsable es declarado: no existe firma digital ni acreditación automática. La revisión de color está integrada; la estructura mantiene resultados históricos separados y no debe presentarse como si dispusiera del mismo flujo completo de aplicación.

### 5.10 Almacenamiento y recuperación

El esquema 1 del estudio utiliza ZIP con `estudio.json`, originales por SHA-256 y un manifiesto de integridad. Permite recuperar la ficha, tablas, UUID, fracciones calculadas, cálculos cromáticos guardados, observaciones y resultados de estructura. Las visualizaciones se regeneran al abrir; el ZIP no incluye los experimentos y modelos de la pestaña tabular.

Se valida el contenido antes de reemplazar la sesión. Se rechazan esquemas incompatibles, rutas peligrosas, duplicados, determinadas entradas no admitidas y estudios sin originales requeridos. Existe migración de ZIP anteriores completos. El almacenamiento depende de descargar el archivo y conservar respaldos; no hay autoguardado permanente del servidor, cifrado propio ni autenticación multiusuario. Un hash detecta modificaciones respecto al manifiesto, pero no acredita autoría si ambos se alteran.

La identificación y la procedencia documentada favorecen la reutilización. Sin embargo, un ZIP local no basta para afirmar cumplimiento integral de FAIR: aún se necesitarían decisiones de licencia, publicación, metadatos y acceso persistente. [Wilkinson et al., 2016](https://doi.org/10.1038/sdata.2016.18).

## 6 Evolución documentada por fases

| Fase | Integración | Estado a la fecha del informe |
|---|---|---|
| 1 | Contrato de observaciones y trazabilidad | Implementado |
| 2 | Estructura remota y tratamiento de imágenes | Implementado; desempeño externo no medido |
| 3 | Región y control exploratorio de calidad cromática | Implementado; umbrales no validados en campo |
| 4 | Conversión colorimétrica y búsqueda Munsell | Implementado como estimación orientativa |
| 5 | Referencia neutra y corrección parcial | Implementado; eficacia experimental pendiente |
| 6 | Revisión y aplicación explícita de color | Implementado |
| 7 | Recuperación, almacenamiento y evaluación de campo | Software implementado; estudio independiente pendiente |

La ficha, textura, ubicación y análisis tabular forman parte del conjunto integrado y se describen en este informe, aunque su desarrollo no se limita a esa secuencia de fases visuales.

## 7 Evidencia disponible y resultados verificables

El comando `.\.venv\Scripts\python.exe -m unittest discover -q`, ejecutado sobre la copia local revisada, finalizó con **86 pruebas satisfactorias** el 9 de septiembre de 2026. Las pruebas cubren componentes de interfaz, controles de datos, cálculos y operaciones de recuperación. Incluyen pruebas sintéticas y sustitución de llamadas externas; no equivalen a 86 muestras de campo ni a inferencias reales sobre 86 suelos.

| Afirmación | Evidencia disponible | Qué falta para ampliarla |
|---|---|---|
| El código ejecuta los flujos examinados | Pruebas automatizadas satisfactorias | Uso observado en campo y pruebas del despliegue de la publicación |
| Un estudio puede guardarse y recuperarse | Pruebas de ida y vuelta e interfaz | Comprobar respaldos y entorno operativo de cada instalación |
| Se conservan propuestas y revisiones de color | Esquema y pruebas de historial | Evaluación de utilidad y errores humanos en uso real |
| La conversión produce una propuesta Munsell | Implementación y pruebas numéricas | Referencias independientes sobre muestras reales |
| El cliente consulta estructura | Código y pruebas con respuestas simuladas | Modelo documentado y evaluación externa |
| El sistema clasifica correctamente los suelos de una población | No demostrado | Pedones de referencia y revisión taxonómica independiente |

No se reportan porcentajes de acierto de campo porque no existen datos disponibles para calcularlos. El iPhone 15 Pro fue indicado como dispositivo de la próxima captura; no se presenta como equipo ya calibrado ni evaluado en este proyecto.

## 8 Diseño propuesto para la investigación de campo

### 8.1 Población y selección

Definir los sitios de procedencia, tipos de suelo, intervalos de profundidad y condiciones de uso a los que se pretende generalizar. Registrar número de sitios, perfiles, horizontes y fotografías por condición. Justificar el tamaño mediante precisión requerida y variabilidad del ensayo preliminar; no adoptar un número de fotos como garantía universal.

Separar un ensayo operativo del conjunto final. Ninguna de las cuatro capturas ya usadas para entrenar debe contarse como caso externo. Las nuevas imágenes reservadas para evaluación no deben usarse para decidir parámetros, etiquetas o umbrales del modelo. Las variantes de una misma fotografía y las muestras vinculadas deben permanecer en el grupo asignado a su perfil o sitio.

### 8.2 Referencias y captura

Dos evaluadores deben registrar sus observaciones antes de ver las propuestas automáticas; los desacuerdos se resuelven mediante un procedimiento documentado. Para color se necesita una referencia Munsell de campo y, si se pretende estudiar error colorimétrico, una referencia instrumental adecuada. Para estructura se debe describir directamente la muestra y establecer cómo se relaciona esa descripción con las etiquetas efectivamente disponibles en el modelo.

Con el iPhone 15 Pro se registrarán unidad, aplicación, versión de iOS, lente o zoom, flash, iluminación, superficie, humedad y cualquier conversión de archivo. Se conservará el original y se identificará el archivo realmente analizado. Las muestras destinadas a estudiar la corrección neutra deben incluir la referencia y su procedencia documentada. No se ha establecido un protocolo de captura validado para ese teléfono.

### 8.3 Comparaciones y métricas

Para color comparar las propuestas originales sin corrección y con referencia neutra sobre las mismas muestras, manteniendo seca y húmeda como condiciones separadas. Reportar cobertura, abstenciones y concordancia exacta. La corrección humana posterior se debe evaluar como etapa distinta para evitar que se compare la referencia contra un valor que ya fue corregido con ella.

`field_validation.py` calcula: cobertura como `n_predichas / n_referencias`; concordancia entre predicciones emitidas; y concordancia sobre todos los pares, de modo que no desaparezcan los fallos sin predicción. Para estructura genera matriz de confusión y, por clase, precisión `TP / n_predichas_de_la_clase`, sensibilidad `TP / n_referencias_de_la_clase` y F1 `2TP / (n_referencias_de_la_clase + n_predichas_de_la_clase)`. Los denominadores vacíos de precisión o sensibilidad producen `null`.

El script evalúa etiquetas por registro. Si el objetivo científico es evaluar detección de objetos con cajas o máscaras, se necesitarán anotaciones espaciales y métricas de detección adicionales; ese análisis no está implementado. Tampoco calcula intervalos de confianza, comparación estadística pareada ni error perceptual instrumental. Para estos resultados se propone un análisis posterior que respete la agrupación por perfil y sitio y explicite sus supuestos.

### 8.4 Criterios de aceptación

Antes de analizar el conjunto final se deben acordar clases prioritarias, niveles de concordancia, cobertura mínima, incertidumbre tolerable y condiciones en que se permitirá usar el sistema. Los umbrales no deben fijarse después de ver los resultados. Si no se alcanzan, el informe debe identificar las condiciones de fallo y limitar las conclusiones; una modificación posterior requiere nueva evaluación independiente.

## 9 Limitaciones y cuestiones para los revisores

La limitación principal es la ausencia de datos de validación externa. Se añaden la procedencia editorial de las imágenes de entrenamiento declaradas, el desconocimiento del conjunto completo y de la arquitectura del modelo remoto, los umbrales exploratorios de calidad y la falta de caracterización colorimétrica del dispositivo. Tampoco se han medido concordancia entre observadores, desempeño por grupos de suelo, robustez frente a distintos teléfonos ni tiempos y errores de uso.

La falta de una referencia no debe codificarse como fallo del modelo ni eliminarse sin explicación: corresponde registrar el caso y el motivo por el cual no puede compararse. Igualmente, una medición asistida no autoriza una conclusión taxonómica si faltan diagnósticos, métodos o exclusión de entradas anteriores.

El posible aporte científico es una integración documentada y evaluable de funciones, cuya utilidad y desempeño deberán contrastarse. No se afirma novedad mundial del enfoque, superioridad frente a especialistas ni sustitución de la carta Munsell. Esas afirmaciones requerirían una búsqueda de antecedentes más amplia y experimentos comparativos específicos.

## 10 Guía para convertir el informe en manuscrito

Como título provisional puede utilizarse **Desarrollo y evaluación de una plataforma para descripción pedológica y análisis asistido de imágenes de suelo**. Mientras no exista evaluación de campo, conviene sustituir “evaluación” por “verificación funcional” y presentar el alcance de forma explícita.

La introducción deberá plantear una brecha concreta respaldada por literatura; métodos debe describir población, referencias, modelo, versiones y análisis; resultados debe separar verificación informática de desempeño experimental; discusión debe contrastar resultados propios con los antecedentes sin trasladar sus porcentajes. La conclusión responderá solo a los objetivos realmente evaluados.

Antes de preparar el envío se necesita completar autoría y contribuciones reales, financiación, conflictos, disponibilidad de datos y código, identificación del libro de origen y condiciones de reutilización de imágenes. También se debe declarar la asistencia de IA en programación o redacción según las instrucciones de la revista elegida, con revisión humana de las afirmaciones y referencias. No se ha seleccionado revista ni verificado una política editorial particular.

**Redacción utilizable en la etapa actual:** “Se implementó una plataforma de descripción pedológica y análisis visual exploratorio con recuperación de estudios y revisión humana. La verificación funcional local comprendió 86 pruebas automatizadas satisfactorias. La exactitud de las estimaciones visuales y de las determinaciones asistidas deberá establecerse mediante un estudio independiente”.

**Afirmaciones que todavía no están sustentadas:** que el sistema identifica correctamente cualquier suelo; que presenta un porcentaje determinado de precisión en campo; que la corrección neutra constituye calibración instrumental completa; o que las capturas empleadas para entrenar demuestran generalización.

## 11 Conclusiones

El proyecto ha integrado una ficha pedológica, controles de consistencia, herramientas texturales, predicción tabular, análisis estructural remoto, estimación cromática y recuperación de evidencias. Su arquitectura permite conservar propuestas y revisiones y diferencia la estimación automática de la aplicación humana de un dato.

La verificación informática disponible sustenta la descripción de un prototipo funcional. La contribución experimental sigue abierta: requiere fotografías nuevas, referencias independientes, un modelo documentado y métricas definidas previamente. Este informe y los documentos de campo constituyen una base para organizar esa investigación, no un sustituto de sus resultados.

## Referencias científicas e institucionales

Los enlaces fueron consultados el 9 de septiembre de 2026. La consulta fue dirigida, no sistemática. En los artículos con acceso parcial se utilizaron los resúmenes o fragmentos disponibles; no se atribuyen a ellos procedimientos no comprobados. Adaptar el formato bibliográfico al estilo de la revista seleccionada.

1. Soil Survey Staff. (2022). *Keys to Soil Taxonomy*. 13.ª edición. USDA NRCS. [PDF oficial](https://www.nrcs.usda.gov/sites/default/files/2022-09/Keys-to-Soil-Taxonomy.pdf).
2. Soil Science Division Staff. (2017). *Soil Survey Manual*. C. Ditzler, K. Scheffe y H. C. Monger, eds. USDA Handbook 18. [Publicación oficial](https://www.nrcs.usda.gov/resources/guides-and-instructions/soil-survey-manual); [capítulo 3](https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf).
3. Gómez-Robledo, L., López-Ruiz, N., Melgosa, M., Palma, A. J., Capitán-Vallvey, L. F., y Sánchez-Marañón, M. (2013). Using the mobile phone as Munsell soil-colour sensor: An experiment under controlled illumination conditions. *Computers and Electronics in Agriculture, 99*, 200–208. [DOI](https://doi.org/10.1016/j.compag.2013.10.002).
4. Fan, Z., Herrick, J. E., Saltzman, R., Matteis, C., Yudina, A., Nocella, N., Crawford, E., Parker, R., y Van Zee, J. (2017). Measurement of Soil Color: A Comparison Between Smartphone Camera and the Munsell Color Charts. *Soil Science Society of America Journal, 81*, 1139–1146. [DOI](https://doi.org/10.2136/sssaj2017.01.0009).
5. Nodi, S. S., Paul, M., Robinson, N., Wang, L., y Rehman, S. U. (2023). Determination of Munsell Soil Colour Using Smartphones. *Sensors, 23*(6), 3181. [Artículo](https://doi.org/10.3390/s23063181).
6. Li, S., Zheng, F., Koiter, A. J., Kupriyanovich, Y., Lobb, D. A., y Goharrokhi, M. (2025). Using a Reference Color Plate to Correct Smartphone-Derived Soil Color Measurements with Different Smartphones Under Different Lighting Conditions. *Soil Systems, 9*(3), 93. [Artículo](https://doi.org/10.3390/soilsystems9030093).
7. Sharma, G., Wu, W., y Dalal, E. N. (2005). The CIEDE2000 color-difference formula: Implementation notes, supplementary test data, and mathematical observations. *Color Research & Application*. [DOI](https://doi.org/10.1002/col.20070).
8. Breiman, L. (2001). Random Forests. [Texto del autor alojado en UC Berkeley](https://www.stat.berkeley.edu/users/breiman/randomforest2001.pdf).
9. Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*, 913–929. [DOI](https://doi.org/10.1111/ecog.02881); [texto consultado](https://www.wsl.ch/lud/biodiversity_events/papers/Roberts_et_al-2017-Ecography.pdf).
10. Wilkinson, M. D., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data, 3*, 160018. [DOI](https://doi.org/10.1038/sdata.2016.18).

## Documentación técnica consultada

Estas fuentes documentan implementaciones y servicios; no son estudios de desempeño de la aplicación.

11. Colour Developers. *Colour 0.4.6*. [sRGB a XYZ](https://colour.readthedocs.io/en/v0.4.6/generated/colour.sRGB_to_XYZ.html); [datos Munsell](https://colour.readthedocs.io/en/v0.4.6/generated/colour.MUNSELL_COLOURS.html).
12. Rochester Institute of Technology. *Munsell Color Science Lab Educational Resources*. [Recursos de renotación](https://www.rit.edu/science/munsell-color-science-lab-educational-resources).
13. scikit-learn Developers. *Common pitfalls and recommended practices*. [Preprocesamiento y fuga de información](https://scikit-learn.org/stable/common_pitfalls.html).
14. Roboflow. *Use with the REST API*. [Protocolo de workflows](https://docs.roboflow.com/deploy/serverless-hosted-api-v2/use-with-the-rest-api).

## Documentos y evidencia interna del proyecto

- [Documentación general de implementación](../TAXONOMIA.md).
- [Protocolo de validación independiente](../validacion_campo/PROTOCOLO.md).
- [Plan operativo de campo](../validacion_campo/PLAN_DE_CAMPO.md).
- [Plantilla del conjunto de evaluación](../validacion_campo/plantilla.json).
- [Plantilla por determinación](../validacion_campo/registro_plantilla.json).
- [Script de evaluación descriptiva](../field_validation.py).

Estos archivos son evidencia interna del desarrollo. La información sobre las cuatro capturas y el iPhone 15 Pro procede de lo declarado por el responsable en la conversación de trabajo; no se ha verificado en una inspección del dataset ni en un ensayo del dispositivo.
