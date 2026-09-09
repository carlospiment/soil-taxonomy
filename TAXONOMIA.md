# Perfil y subgrupo

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
   evidencia invalidan las respuestas de la guía al volver a evaluarla. El JSON
   es una exportación; esta versión no incluye su importación.

## Fotos, coordenadas y textura

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

Textura: [Soil Survey Manual (2017), capítulo 3, figura 3-7](https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf).
Coordenadas: [NGA Coordinate Systems](https://earth-info.nga.mil/?action=coordsys&dir=coordsys).
