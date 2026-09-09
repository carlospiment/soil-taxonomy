# Validación independiente de color y estructura

Estado: **pendiente de datos de campo y ejecución por un equipo independiente**.
Este documento es un protocolo propuesto, no un estudio concluido. Las pruebas
automatizadas usan imágenes sintéticas y no estiman el desempeño en suelos reales.

## Preparación y referencia

1. Identificar equipo evaluador, responsabilidades, conflictos y relación con el
   desarrollo/entrenamiento. Registrar protocolo y umbrales de aceptación antes
   de observar resultados. Conservar versión del código y del modelo remoto;
   si no se conoce el modelo interno, declarar esa limitación de reproducibilidad.
2. Definir población de uso, sitios, dispositivos, iluminación, humedad y clases
   esperadas. Justificar el número de perfiles y la representación de cada clase
   con un diseño estadístico. Separar por perfil/sitio entrenamiento, ajuste y
   evaluación; las fotos repetidas no deben cruzar esos conjuntos.
3. Obtener referencias sin mostrar las predicciones a los especialistas. Registrar
   dos lecturas independientes y documentar discrepancias y resolución; conservar
   ambas lecturas además de la referencia consensuada.
4. Para color registrar Munsell, humedad y preparación de la superficie; mantener
   separadas determinaciones secas y húmedas. La descripción debe considerar la
   superficie evaluada y la condición de humedad, según el
   [Soil Survey Manual, capítulo 3](https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf).
   Para estructura describir tipo, tamaño y grado con el manual y documentar una
   correspondencia explícita entre las etiquetas reales del modelo y la referencia.
   La app no predice necesariamente los tres atributos.
5. Conservar originales, SHA-256, UUID del perfil/horizonte, fecha, dispositivo,
   iluminación, ROI, referencia neutra y su reflectancia documentada, versiones,
   propuesta original, revisión y motivo. Comparar el resultado automático previo
   a la corrección humana con la referencia; no evaluar el dato ya corregido.

## Registro y resumen reproducible

Copiar `plantilla.json` a un archivo de trabajo y completar sus metadatos.
Cada elemento de `records` debe contener:

| Campo | Contenido |
|---|---|
| sample_id, profile_id, horizon_id | Identificadores de muestra, perfil y horizonte |
| image_sha256 | Hash hexadecimal del original |
| kind | `color` o `structure` |
| moisture | `dry` o `moist`; estructura admite `unknown` |
| reference_reviewer, reference_evidence | Responsable y documento de la referencia ciega |
| reference | Munsell o etiqueta estructural de referencia |
| predicted | Propuesta automática original; `null` si no emitió resultado |
| abstention_reason | Obligatorio si no hay predicción |

Se pueden añadir campos de dispositivo, sitio, réplicas y lecturas originales.
Usar identificadores diferentes para réplicas y conservar su vínculo con el perfil.
No seleccionar únicamente fotografías aceptadas: registrar también rechazos,
abstenciones, errores remotos y exclusiones con sus motivos.

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe field_validation.py validacion_campo\datos.json validacion_campo\resultados.json
```

El comando exige datos y metadatos, rechaza pares duplicados y no sobrescribe
resultados existentes. Calcula cobertura, abstenciones y concordancia exacta tanto
sobre resultados emitidos como sobre todos los pares. Separa color seco, húmedo y
estructura y muestra matrices de confusión. No certifica independencia ni aplica
un umbral inventado. Una etiqueta sin correspondencia con el modelo no debe
considerarse una evaluación estructural válida.

## Informe independiente requerido para aceptación

Publicar diseño, fechas, muestra, exclusiones, trazabilidad de referencias,
resultados por dispositivo/iluminación/humedad/clase y condiciones de fallo.
Añadir intervalos de incertidumbre con el perfil/sitio como unidad de agrupación;
las métricas descriptivas del script no los calculan. Para estructura informar
también precisión y sensibilidad por clase conforme al diseño acordado.
Si se mide error perceptual de color, documentar instrumento, iluminante,
observador y transformación compatibles antes de calcular diferencias Lab;
concordancia Munsell exacta no equivale a error perceptual.

El equipo debe comparar los resultados con los umbrales preregistrados y emitir
una conclusión con límites de uso, responsables y referencias al conjunto de
evidencias. Adjuntar ese informe y los datos de evaluación al respaldo del proyecto.
Hasta entonces, **la aceptación científica de la Fase 7 sigue pendiente**.
