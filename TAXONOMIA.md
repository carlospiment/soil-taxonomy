# Perfil y subgrupo

## Actualización USDA exclusiva — 10 de septiembre de 2026

La primera pestaña se limita a evidencias y documentación para **Keys to Soil
Taxonomy, 13th edition (2022)**, hasta subgrupo. La guía de esta actualización es
[Perfil USDA: alcance, validación y resultados](investigacion/perfil_usda_2026.md).
Esta sección y esa guía sustituyen las indicaciones históricas de fertilidad y
borrado de decisiones descritas más abajo. El PDF del manual anterior todavía
describe la interfaz previa; para estos cambios utiliza la guía enlazada.

El módulo sustituye las reglas que asignaban un orden usando únicamente pH,
materia orgánica o arcilla. Permite registrar evidencias por horizonte y una
ruta taxonómica manual. No confirma diagnósticos a partir de esos valores aislados.

## Uso

1. Describe el perfil y el origen de las profundidades. Deja vacías las mediciones
   desconocidas; no uses cero para representarlas.
2. Registra por horizonte la textura, colores Munsell, morfología, resultados y
   métodos de laboratorio. Las dos medidas de saturación de bases y las unidades
   de CIC no son intercambiables.
3. Evalúa los horizontes y propiedades diagnósticos con sus definiciones completas.
   Presente requiere evidencia; No evaluado no significa Ausente.
4. Documenta orden, suborden y gran grupo con código/página y exclusión de las
   entradas anteriores. La ficha general sirve para cualquier orden.
5. Para Hapludults o Dystrudepts, usa la clave guiada en su orden original. Lee
   todos los requisitos, incluidos AND/OR, espesor, profundidad y notas. Registra
   evidencia tanto para Cumple como para No cumple. Se toma la primera entrada
   que cumple; una entrada desconocida bloquea las posteriores. Typic exige
   excluir y documentar todas las anteriores.
6. Descarga el JSON para conservar la ficha y las decisiones, o el ZIP para incluir
   las fotos originales aceptadas. Los cambios de
   evidencia conservan las respuestas y exigen revisar su vigencia. El JSON
   conserva referencias; para recuperar un estudio completo usa el ZIP de Fase 7.

## Fotos, coordenadas y textura

En el bloque 2, los encabezados de horizontes usan indicadores de color:
🟩 observaciones de campo, 🟦 resultados de laboratorio, 🟪 cálculos automáticos
y ⬜ métodos/procedencia. La leyenda y las ayudas explican su significado.
Un asterisco distingue identificación, techo y base como datos básicos de cada
horizonte. Los demás requisitos dependen de la clave y del estudio; el color
no impone obligatoriedad universal. Las fracciones texturales se identifican
como laboratorio, con ayuda que aclara el cálculo de la tercera fracción.
Los indicadores solo cambian la presentación, no los nombres exportados ni
los archivos de estudios anteriores. Los campos químicos siguen siendo entradas
manuales hasta disponer de datos de origen y métodos para automatizarlos.

- El responsable y la fecha se registran por separado. Se admiten coordenadas
  geográficas decimales o UTM con zona, hemisferio y datum. WGS 84 / UTM se
  transforma a latitud/longitud mediante pyproj; otros datums se conservan sin
  transformación automática.
- Fotos JPG, PNG y WEBP: máximo 10, 20 MB por foto, 60 MB en conjunto y 40 MP
  por imagen. El JSON guarda referencias; el ZIP incluye las imágenes originales.
- En la tabla de horizontes, dos fracciones válidas completan la tercera hasta
  100 %. Se conserva cuál fue calculada; editar una medida recalcula la derivada.
  Editar directamente la derivada convierte las tres en manuales.
- El triángulo dinámico muestra las 12 clases texturales USDA y el horizonte
  seleccionado. Las sumas incorrectas no se normalizan. No se infieren clases
  granulométricas de familia ni subgrupos a partir de la textura.
- Las ayudas están en los iconos junto a los campos y en los encabezados de las
  tablas. El manual completo está en `Manual_usuario/Manual_de_usuario_Soil_Taxonomy.pdf`.

## Alcance y límites

- Claves guiadas: 15 subgrupos de Hapludults y 26 de Dystrudepts. Se conserva el
  texto original inglés; la nota de HCGA se muestra junto al criterio.
- La interpretación de criterios y la determinación de los niveles superiores
  corresponden al usuario. El programa valida documentación y precedencia,
  no certifica la interpretación pedológica ni verifica todas las relaciones
  entre mediciones y diagnósticos.
- Para otros grandes grupos, la ruta es manual: se registra el taxón propuesto,
  no se genera un nombre concatenando rasgos ni se valida su existencia.
- La lista de mediciones no sustituye las definiciones completas. Algunas claves
  requieren observaciones adicionales, secciones de control o métodos específicos.
- La pestaña de aprendizaje automático predice las etiquetas del dataset,
  incluso Subgrupo_USDA si existe esa columna. Esa predicción no equivale a una
  determinación por las claves taxonómicas.

## Fuentes consultadas

Soil Survey Staff (2022). *Keys to Soil Taxonomy*, 13th edition. USDA–NRCS.

- [Página oficial](https://www.nrcs.usda.gov/resources/guides-and-instructions/keys-to-soil-taxonomy).
- [PDF oficial](https://www.nrcs.usda.gov/sites/default/files/2022-09/Keys-to-Soil-Taxonomy.pdf).
- [Copia gubernamental consultada en GovInfo](https://www.govinfo.gov/content/pkg/GOVPUB-A57-PURL-gpo224020/pdf/GOVPUB-A57-PURL-gpo224020.pdf).

Secciones: diagnósticos (capítulo 3); uso secuencial, profundidades y códigos
(capítulo 4, pp. 65–69; especialmente pp. 66–67); Dystrudepts (pp. 224–227;
páginas 232–235 del PDF); Hapludults (pp. 330–331; páginas 338–339 del PDF).
Los criterios de subgrupo de `subgroup_keys.json` proceden de esas páginas del
documento gubernamental y conservan su secuencia. No se mezclan ediciones.

## Verificación

### Recuperación, almacenamiento y validación de campo: Fase 7

Se eligió almacenamiento en archivos ZIP portátiles controlados por el usuario,
sin base de datos ni servicio compartido. Al final de la página, `Guardar estudio
completo (ZIP)` conserva ficha editable, UUID, tablas, fracciones calculadas,
observaciones de color con cálculos/ROI/calibración/revisiones/aplicaciones,
fotografías originales y resultados de estructura acumulados. No guarda claves
API, credenciales ni modelos/datasets de la pestaña de aprendizaje automático.
Esa pestaña es un experimento separado del estudio pedológico.

Abre el archivo desde `Abrir estudio guardado` al inicio. El botón exige marcar
el reemplazo explícito del estudio actual. La validación ocurre antes de cambiar
la sesión: un fallo conserva el estudio abierto. Tras recuperar puedes editar
tablas y campos y revisar observaciones; los gráficos y controles se regeneran.
Los originales de análisis están disponibles al final para visualizar, descargar
y volver a cargar si necesitas otra evaluación. No se ejecuta inferencia remota
al abrir. Los resultados estructurales históricos se muestran por separado.

`study_storage.py` define el esquema 1: `estudio.json`, imágenes por SHA-256 y
`manifest.json` con hashes de todos los contenidos. Se verifica integridad,
identidad y versiones; tablas y entradas de controles; imágenes, historial de
revisión y correspondencia de aplicaciones. Se rechazan rutas peligrosas,
duplicados, enlaces, ZIP cifrados, imágenes ausentes y esquemas desconocidos.
Los archivos se leen en memoria sin extraer ni ejecutar contenido. Límites:
100 MB comprimidos/descomprimidos, 8 MB de JSON y 200 imágenes; las fotos de
perfil mantienen el máximo de 10 y 60 MB, y cada imagen 20 MB/40 MP.
La memoria de trabajo puede superar el tamaño del ZIP durante la validación.

Migración: acepta el ZIP anterior `perfil_taxonomico.json` + fotos originales,
manteniendo UUID y revisiones cuando existen; si carece de trazabilidad, crea
UUID nuevos y un historial vacío, sin inventar evaluaciones. Debe estar completo:
si una observación anterior apunta a una foto no incluida, se rechaza. Adjunta
el original antes de volver a exportar desde la sesión original. El JSON aislado
no permite recuperar imágenes y no se admite como estudio completo. Exportar
de nuevo produce esquema 1; nunca se sobrescribe el archivo original.

Persistencia: la descarga requiere que el usuario guarde el archivo. No hay
autoguardado ni almacenamiento permanente del servidor. Antes de cerrar o
reemplazar un estudio guarda un ZIP con fecha y copia a otra ubicación; prueba
la apertura de esa copia. Mantén varias versiones y restaura la última íntegra
si la más reciente está dañada. No hay reparación automática de datos corruptos.

Acceso: no existe listado compartido de estudios ni autenticación de usuarios.
Los permisos/cifrado del dispositivo y del destino de respaldo protegen los ZIP;
el archivo no está cifrado y el hash no autentica autoría. Quien posea el archivo
puede leerlo. La app no modifica permisos del sistema. En un despliegue multiusuario
se necesita protección de acceso al servicio, además de estas comprobaciones.

Pruebas: `.\.venv\Scripts\python.exe -m unittest discover -v` incluye recuperación
y edición en Streamlit, respaldos, migración anterior, conservación de fotos,
cálculos y revisiones, exclusión de credenciales, rechazo de rutas/archivos
incompatibles y conservación de la sesión ante importación fallida.
Estas pruebas comprueban el límite de acceso de la aplicación, no las ACL de
carpetas elegidas por el usuario ni un sistema de autenticación inexistente.

La validación independiente está **pendiente**. El protocolo y plantilla están
en [validacion_campo/PROTOCOLO.md](validacion_campo/PROTOCOLO.md).
`field_validation.py` resume pares reales con cobertura, abstenciones,
concordancia exacta y matrices de confusión. No contiene resultados de campo
ni declara precisión científica. La aceptación completa requiere que un equipo
independiente ejecute el protocolo y entregue datos e informe de desempeño.

Para distribuir incluye `study_storage.py`, `storage_ui.py`, `field_validation.py`,
`validacion_campo/` y los cambios en `app.py`, `profile_ui.py`, `field_media.py`,
`subgroup_guide.py`, `color_ui.py` y `structure_ui.py`, junto al proyecto existente.
No se añadieron dependencias.

### Revisión humana y aplicación de color: Fase 6

En la pestaña de color abre `Revisar y aplicar observaciones de color`. El historial
está disponible aunque el cargador ya no tenga la foto. Selecciona una observación,
registra responsable y motivo/evidencia, y acepta, corrige o rechaza. Aceptar exige
una propuesta Munsell existente; corregir permite registrar una determinación de
campo incluso si la imagen no produjo color. El formato/rango de notación se
comprueba, pero no la existencia del color en una carta comercial.

Guardar revisión no cambia la ficha. Para ello revisa el horizonte, campo seco o
húmedo y transición valor anterior→confirmado; marca la confirmación y pulsa
`Aplicar color confirmado al perfil`. Solo se actualiza ese campo del horizonte
identificado por UUID. Se rechazan perfiles distintos, horizontes borrados,
propuestas pendientes/rechazadas, valores anteriores distintos y doble aplicación.
La revisión del editor se incrementa para regenerar tabla e informe con el dato.
Esto incorpora una medición confirmada, no una clasificación taxonómica definitiva.

`soil_color/validation.py` devuelve copias sin alterar la predicción. Cada revisión
conserva responsable, motivo y fecha UTC. La aplicación añade `applications` con
identificador, revisión asociada, responsable, fecha, campo, valor anterior y valor
aplicado. Una observación aplicada ya no se revisa ni aplica otra vez: una nueva
determinación puede sustituirla explícitamente. Editar la tabla posteriormente no
se revierte desde este historial; los eventos describen aplicaciones pasadas.
El nombre es declarado, sin autenticación ni firma; no implica acreditación.

`color_review_ui.py` permite descargar el JSON revisado. El JSON/ZIP del perfil y
el ZIP de la foto actualmente seleccionada incluyen revisiones y aplicaciones.
El almacenamiento sigue siendo temporal en sesión. Estructura Roboflow permanece
separada: esta fase aplica exclusivamente colores, no clases estructurales.

Para publicar sube `color_review_ui.py`, `color_ui.py` y toda la carpeta
`soil_color/`, conservando las dependencias y archivos anteriores. No hay nuevas
dependencias. Agrega `test_color_validation` al comando de pruebas de Fase 5;
incluye inmutabilidad de propuesta, rechazo, identidad, conflictos, aplicación
única y flujo Streamlit con revisión sin cambio y aplicación exportada.

### Referencia neutra: Fase 5, calibración parcial

En el modo de estimación activa `Corregir con referencia neutra en esta foto`.
Fotografía una referencia neutra junto al suelo, en el mismo plano y bajo la
misma iluminación uniforme, evitando reflejos. Registra dispositivo, iluminación
y preparación. Selecciona el interior del parche con los controles; no debe
solaparse con píxeles útiles del suelo. Introduce su identificación y la fuente
de su reflectancia, y el porcentaje documentado por fabricante o medición.
No se presupone 18 % ni se admite una hoja blanca como referencia conocida.

`soil_color/calibration.py` implementa un modelo diagonal experimental: cada
ganancia es reflectancia / mediana del canal de referencia decodificado a RGB
lineal. Multiplica el RGB lineal representativo del suelo por las ganancias y
vuelve a codificar sRGB antes del pipeline XYZ/Lab/Munsell. Es un ajuste de balance
y exposición, no una caracterización espectral ni una matriz multicolor de cámara.
La adaptación Bradford D65→C de Fase 4 sigue siendo una operación separada.

Se rechazan referencias con región insuficiente, oscuridad, saturación o alta
variación, canales medianos fuera de (10,245), reflectancia fuera de [2,90] % o
ganancias fuera de [0.25,4]. Estos límites son operativos, no criterios científicos
validados. Poco detalle es compatible con un parche uniforme. Un RGB corregido
fuera de [0,1] lineal impide estimar Munsell: no se recorta silenciosamente ni se
sustituye por una estimación sin corrección.

La exportación conserva foto/hash, rectángulo y calidad de referencia, reflectancia
declarada, identificación, ganancias, versión `neutral-linear-gains-v1`, RGB
observado/corregido y espacios antes/después. `calibrated=true` significa solamente
que esta corrección parcial se aplicó; `scientifically_validated=false` permanece.
No existe todavía modo científico validado, caracterización multicolor, detección
automática de carta ni comprobación independiente de la reflectancia declarada.
El ajuste usa el propio parche; no se presenta su error de ajuste como validación.
La respuesta espectral, procesamiento del teléfono, iluminación no uniforme y
metamerismo pueden mantener errores aunque el neutro quede corregido.

Cambiar referencia, reflectancia, región o modo invalida el resultado visible.
Los registros siguen pendientes y no alteran la taxonomía. No hay dependencias
nuevas. Para publicar sube `color_ui.py` y toda la carpeta `soil_color/` conservando
los archivos anteriores. Pruebas: añade `test_calibration` al comando de Fase 4;
comprueba recuperación de ganancias sintéticas, bloqueo de entradas/recorte y
flujo de interfaz, exportación y separación del dato confirmado.

### Colorimetría orientativa: Fase 4

Activa `Estimar Munsell orientativo (imagen no calibrada)` en la pestaña de color
y registra la evaluación como en Fase 3. El modo de solo calidad sigue disponible.
La propuesta permanece pendiente; no modifica los colores manuales ni la taxonomía.
Una región rechazada o con alerta de oscuridad/saturación no produce Munsell.
Las demás advertencias permanecen visibles junto a la estimación.

`soil_color/color_spaces.py` interpreta perfiles ICC mediante Pillow/LittleCMS,
con destino sRGB e intención colorimétrica relativa. Sin ICC asume sRGB y lo
registra; rechaza transparencias, ICC inválidos y modos distintos de RGB/gris sin
perfil. Esta gestión de color no calibra la cámara, exposición ni iluminación.

El representante es la mediana por canal del RGB codificado sobre la muestra
enmascarada de Fase 3, de hasta 512 px por lado. No es la media de toda la imagen
ni necesariamente un píxel existente. Se decodifica sRGB, se calcula XYZ D65 y se
adapta mediante Bradford a C; CIELAB utiliza blanco C y observador CIE 1931 de 2°.
XYZ se exporta con Y del blanco igual a 1; Lab usa su escala de referencia habitual.

`soil_color/munsell.py` compara por CIEDE2000 con los 2734 registros de
`colour.MUNSELL_COLOURS['real']`, convirtiendo Y porcentual a escala 0–1, y añade
N1–N9 mediante la función de renotación de la misma biblioteca. No utiliza el
conjunto extrapolado `all` ni inventa una tabla RGB. Devuelve el candidato discreto
más próximo y cuatro alternativas, sin interpolación ni restricción a páginas de
una carta comercial. Un candidato próximo no demuestra exactitud frente al suelo:
ΔE00 es distancia a la referencia, no probabilidad, incertidumbre ni validación.
No hay umbral científico de aceptación ni detección de pertenencia al gamut de
renotación; la búsqueda es orientativa incluso cuando existe un vecino lejano.

La exportación incluye conversiones, estado no calibrado, algoritmo, versión de
Colour, procedencia/tamaño/hash del catálogo y gestión ICC. La caché contiene solo
el catálogo público; las fotos permanecen en sesión. Cambiar de modo invalida la
evaluación visible y conserva el historial. Calibración y validación humana
aplicada siguen pendientes de fases posteriores.

Dependencia nueva: `colour-science==0.4.6` (Python >=3.10), probada en Python 3.12
con NumPy 2.2.6. Instala también imageio; reutiliza SciPy existente. Para publicar,
sube `requirements.txt`, `color_ui.py` y toda la carpeta `soil_color/`, conservando
el resto del proyecto. No se requiere API ni archivos de referencia descargados
en tiempo de ejecución.

Pruebas: agrega `test_colorimetry` al comando completo de Fase 3 (72 pruebas).
Incluyen primario rojo, blanco/negro, transferencia sRGB, un par publicado de
CIEDE2000, un registro real de renotación y neutros, ICC inválido, transparencia,
bloqueo por calidad y flujo Streamlit sin sobrescribir valores manuales.

Referencias metodológicas:
- [Colour 0.4.6: sRGB a XYZ](https://colour.readthedocs.io/en/v0.4.6/generated/colour.sRGB_to_XYZ.html).
- [Colour 0.4.6: datos Munsell](https://colour.readthedocs.io/en/v0.4.6/generated/colour.MUNSELL_COLOURS.html).
- [RIT: procedencia de renotación, iluminante C y observador 2°](https://www.rit.edu/science/munsell-color-science-lab-educational-resources).

### Región y calidad del color: Fase 3

La cuarta pestaña, `Color: región y calidad`, se implementa en `color_ui.py` y
`soil_color/`. No requiere dependencias nuevas ni envía fotos a Roboflow.

1. Crea un horizonte con nombre en la ficha del perfil.
2. Sube una fotografía JPG/PNG o usa la cámara (máximo 20 MiB y 25 MP).
3. Selecciona el horizonte y el estado seco o húmedo. Puedes indicar preparación,
   iluminación, dispositivo y qué material estás observando.
4. Ajusta el rectángulo de interés y hasta tres rectángulos de exclusión mediante
   los controles porcentuales. Las exclusiones son manuales; no hay detección de
   raíces, piedras ni fondo. La vista gris muestra los píxeles excluidos.
5. Pulsa `Evaluar y registrar selección` y descarga el ZIP de la evaluación.

Las coordenadas se guardan en píxeles de la imagen orientada según EXIF, con origen
arriba a la izquierda y límites derecho e inferior exclusivos. Las exclusiones
superpuestas se cuentan una sola vez y se recortan a la región seleccionada.
La foto original no se modifica. Cambiar imagen, selección, horizonte, humedad o
contexto invalida el resultado visible; repetir una evaluación idéntica no duplica
su registro. Seco y húmedo generan observaciones independientes.

El control `roi-qc-v1` es exploratorio y no está validado científicamente para
suelos. Rechaza regiones con menos de 1024 píxeles útiles o un lado menor de 16 px.
Calcula estadísticas sobre una muestra de hasta 512 px por lado: advierte si más
del 20 % tiene todos los canales RGB ≤ 10, si más del 20 % tiene algún canal ≥ 245,
si la desviación estándar de algún canal supera 40 o si la varianza del laplaciano
es menor de 15. Esta última medida indica poco detalle, que también puede deberse
a una superficie uniforme; no demuestra desenfoque. Las métricas, umbrales,
versión y advertencias se exportan. No detectar alertas no certifica la fotografía.

Se registra la mediana RGB observada, sin normalización ICC, calibración,
conversiones XYZ/Lab ni asignación Munsell. Ningún valor modifica los colores
manuales ni la clasificación. Incluso una evaluación rechazada por calidad queda
como observación pendiente, sin valor validado, para conservar su trazabilidad.

El ZIP específico contiene `evaluacion_color.json` e imagen original, vinculados
por SHA-256. El informe del perfil incluye la observación, pero su ZIP solo incluye
esta foto si también se adjunta en la ficha; en caso contrario la trazabilidad
señala la imagen no adjunta. Los registros viven en la sesión, sin base de datos ni
importación: descarga los archivos antes de cerrarla.

Para publicar, añade `color_ui.py`, la carpeta completa `soil_color/` y `app.py`
actualizado, conservando los módulos de las fases anteriores y el resto del
proyecto. Subir solo `app.py` no basta.

Pruebas completas (67): `.\.venv\Scripts\python.exe -B -m unittest test_soil_color test_image_io test_structure_client test_roboflow test_visual_observations test_app test_soil_profile test_field_features -q`.
Incluyen orientación EXIF, máscaras superpuestas, exclusiones en estadísticas,
regiones vacías, exposición y detalle sintéticos, exportación del original y flujo
Streamlit con registros seco/húmedo sin llamadas al proveedor ni cambios manuales.

### Estructura e imágenes: Fase 2

`app.py` delega la tercera pestaña en `structure_ui.py`. La lectura compartida
está en `image_io.py`; `field_media.validate_photo` mantiene su interfaz anterior.
Se comprueba el formato decodificado, integridad, límite de bytes y píxeles y que
sea una foto estática. Perfiles conservan JPG/PNG/WEBP y 40 MP; estructura,
JPG/PNG y 25 MP; ambos mantienen 20 MB por archivo. El ZIP conserva los originales.
Para inferencia se orienta según EXIF y se convierte a RGB. Esto no calibra ni
convierte un perfil ICC a sRGB; la futura colorimetría deberá gestionar ese paso.

`soil_structure/roboflow_client.py` usa HTTP directo al mismo endpoint que el SDK
1.5.2, con la misma codificación JPEG, autorización Bearer, `confidence=0.4` y
`use_cache=True`. Una prueba compara la solicitud con la del SDK instalado.
Se conserva `inference-sdk` en las dependencias como referencia de compatibilidad;
`requests`, ya instalado mediante el SDK, se declara ahora como dependencia directa.
Este transporte evita modificar el SDK o alterar clientes globales para aplicar
timeouts. Se fijan 10 s para conexión y 60 s de inactividad de lectura: no son
un plazo máximo total de ejecución del servidor. No hay reintentos automáticos de
POST, porque una solicitud que agota la espera puede haberse procesado y consumido
cuota. Las redirecciones se rechazan. Los errores públicos no muestran el cuerpo
ni las excepciones originales del proveedor.

Workspace y workflow continúan siendo `carlos-pimentel/usda-soil-structure`.
La clave se busca en entorno, secretos de Streamlit y, como alternativa, el campo
de contraseña. Opcionalmente `ROBOFLOW_WORKFLOW_VERSION_ID` permite fijar una
versión en entorno o secretos. Si no se configura, se conserva la selección
remota del workflow; no se conoce ni se inventa la versión del modelo interno.
No se alteran los pasos remotos de almacenamiento del workflow existente.

`soil_structure/prediction.py` resume únicamente listas reconocidas de detecciones
con `class`/`class_name` y `confidence` entre 0 y 1. Conserva cada detección original,
incluidas sus coordenadas, y diferencia salidas vacías, listas vacías y formatos no
interpretados. No transforma puntuaciones en certeza ni asigna tamaño o grado.
Los ejemplos de prueba son sintéticos; no documentan las clases reales del modelo.

La interfaz conserva la respuesta HTTP completa y permite descargar
`estructura_suelo.json` con hash de imagen, dimensiones, fecha UTC, configuración,
resumen y respuesta original. Este JSON no contiene los bytes de la foto: conserva
el original por separado. Un cambio de imagen, credencial o versión invalida el
resultado visible. Los reruns no provocan nuevas solicitudes; solo el botón Analizar.
El resultado sigue separado de la ficha y de su registro de observaciones: aún no
hay asociación automática a horizonte ni revisión humana en pantalla.

Para publicar esta fase deben incluirse `app.py`, `structure_ui.py`, `image_io.py`,
`field_media.py`, `requirements.txt` y la carpeta completa `soil_structure/`, además
de los módulos de Fase 1 y el resto del proyecto. Subir solo `app.py` no basta.

Pruebas completas: `.\.venv\Scripts\python.exe -m unittest -q test_app test_soil_profile test_field_features test_visual_observations test_roboflow test_structure_client test_image_io`.

Referencia del protocolo HTTP:
[Roboflow Workflows](https://inference.roboflow.com/workflows/modes_of_running/).
No se ha ejecutado inferencia real durante esta fase; falta contrastar la salida
del workflow privado con fotografías de campo.

### Observaciones visuales: contrato de la Fase 1

El JSON y el JSON dentro del ZIP conservan los campos anteriores y agregan
`trazabilidad_visual` (schema_version 1). Contiene el UUID del perfil, referencias
a los horizontes exportados y una lista de observaciones. El UUID del perfil se
mantiene durante la sesión aunque se corrija el código de campo; no identifica
automáticamente un perfil abierto en otra sesión. Las filas conservan UUID
internos al editarse, renombrarse o eliminar filas anteriores. Estos UUID no se
mezclan con las mediciones ni se muestran como columnas editables.

`visual_observations.py` proporciona funciones independientes de Streamlit:

- `create_observation`: registra propuesta, hash de imagen, horizonte, humedad,
  método, versión, contexto, calidad y respuesta original. El contexto admite ROI,
  captura, calibración y modelo; los resultados pueden incluir RGB, XYZ, Lab y
  alternativas. No se inventan valores faltantes ni se realizan conversiones.
- `review_observation`: devuelve una copia con un evento de aceptación, corrección
  o rechazo, responsable, motivo y fecha UTC. Conserva `predicted_value`, separa
  `validated_value` y mantiene las revisiones anteriores.
- `extend_report`: añade el registro sin alterar campos anteriores. Conserva y
  señala observaciones cuyo horizonte fue eliminado o cuya imagen no está adjunta.

Las observaciones de color requieren `dry` o `moist`; estructura también admite
`unknown`. Cada determinación es independiente, incluso para una misma fotografía
o un mismo horizonte. Las fechas incluyen zona horaria; NaN, infinito y objetos no
JSON se rechazan. Los resultados se copian para evitar cambios por referencias
compartidas; no es un registro firmado ni una base de datos inmutable.

La Fase 1 preparó el contrato y la exportación. La Fase 3 añade la interfaz para
registrar evaluaciones de región y calidad; todavía no hay interfaz de revisión
ni se capturan automáticamente resultados de Roboflow. Los colores manuales anteriores
no se convierten en predicciones. Registrar o revisar propuestas no altera la
huella de evidencia ni actualiza los datos taxonómicos. La aplicación de datos
confirmados, las conversiones Munsell, el guardado permanente y la importación
siguen pendientes de sus fases correspondientes.

Pruebas del contrato: `.\.venv\Scripts\python.exe -m unittest -v test_visual_observations`.

Ejecuta `.\.venv\Scripts\python.exe -m unittest -v test_app test_soil_profile test_field_features`.
Las pruebas verifican funcionamiento, coherencia de datos y precedencia. No
constituyen validación científica con pedones de referencia.

### Laboratorio anterior: compatibilidad histórica

La primera pestaña utiliza fichas individuales para horizontes, determinaciones,
diagnósticos y ruta taxonómica. Los datos categóricos se capturan mediante listas
con «No evaluado», sin asignar observaciones por defecto. La descripción de campo
incluye campos condicionados, tamaños de estructura y nitidez de límites asistidos
según el USDA Field Book 4.0. La textura puede completar la tercera fracción a partir
de dos porcentajes válidos. Estas ayudas no confirman automáticamente diagnósticos
ni subgrupos.

Los datos de sitio y descripción se conservan en `descripcion_asistida` del respaldo.
Cambiar de ficha o esconder un campo condicionado conserva lo capturado; eliminar
un horizonte o análisis permite deshacer la última eliminación durante la sesión.
Las pruebas de interacción están en `test_assisted_capture.py`.

La versión anterior incluía **Análisis de laboratorio y fertilidad**. Ahora,
**Perfil y subgrupo → 2b. Determinaciones de laboratorio para la clave USDA** registra
una fila por determinación y muestra, con horizonte, profundidad, resultado
original, unidad, método y datos del informe. Se admiten comas decimales,
límites como `<0,02` y resultados `ND`; los datos ausentes no se convierten en cero.

La vista de resultados normalizados convierte únicamente unidades compatibles.
Para ppm exige confirmar la base de suelo seco por masa. Las saturaciones y
relaciones conservan el denominador o la fórmula informados por el laboratorio.
Los registros agronómicos anteriores y sus categorías se conservan como históricos,
fuera de la evidencia taxonómica; pueden descargarse desde Guardar estudio y respaldo.
Los resultados taxonómicos se incluyen en la ficha JSON y en el respaldo ZIP, se recuperan
al abrir el estudio y no se trasladan automáticamente a los campos taxonómicos.
Los estudios anteriores sin esta tabla se abren con el laboratorio vacío.

Consulta el [catálogo, reglas y ejemplo de captura](investigacion/laboratorio_suelos.md).
Pruebas: `python -m unittest -v test_laboratory test_study_storage`.

Textura: [Soil Survey Manual (2017), capítulo 3, figura 3-7](https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf).
Coordenadas: [NGA Coordinate Systems](https://earth-info.nga.mil/?action=coordsys&dir=coordsys).
