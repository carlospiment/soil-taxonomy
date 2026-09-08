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

Ejecuta `.\.venv\Scripts\python.exe -m unittest -v test_app test_soil_profile test_field_features`.
Las pruebas verifican funcionamiento, coherencia de datos y precedencia. No
constituyen validación científica con pedones de referencia.

Textura: [Soil Survey Manual (2017), capítulo 3, figura 3-7](https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf).
Coordenadas: [NGA Coordinate Systems](https://earth-info.nga.mil/?action=coordsys&dir=coordsys).
