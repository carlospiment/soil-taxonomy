"""Genera el manual de la versión local. Ejecutar con reportlab instalado."""
from pathlib import Path
import sys
import math
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from texture import REGIONS, COLORS, ENGLISH

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Manual_usuario'
OUT.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('UI', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('UIB', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('UI', normal='UI', bold='UIB', italic='UI', boldItalic='UIB')
GREEN=colors.HexColor('#174c3b')
TEAL=colors.HexColor('#32816b')
INK=colors.HexColor('#24342e')
PALE=colors.HexColor('#edf4ef')
GRAY=colors.HexColor('#5d6c65')
W,H=A4
WIDTH=W-88
styles={
 'body':ParagraphStyle('body',fontName='UI',fontSize=10.3,leading=15,textColor=INK,spaceAfter=9),
 'small':ParagraphStyle('small',fontName='UI',fontSize=8.8,leading=12.4,textColor=GRAY,spaceAfter=6),
 'h1':ParagraphStyle('h1',fontName='UIB',fontSize=23,leading=28,textColor=GREEN,spaceAfter=15),
 'h2':ParagraphStyle('h2',fontName='UIB',fontSize=13.2,leading=18,textColor=TEAL,spaceBefore=10,spaceAfter=7),
 'table':ParagraphStyle('table',fontName='UI',fontSize=9.1,leading=12.6,textColor=INK),
 'th':ParagraphStyle('th',fontName='UIB',fontSize=9.1,leading=12.6,textColor=colors.white),
 'code':ParagraphStyle('code',fontName='UI',fontSize=9.3,leading=15,textColor=GREEN,backColor=PALE,borderPadding=9,spaceAfter=12),
}


def p(text,style='body'): return Paragraph(text,styles[style])
def title(n,text): return [p(f'{n:02d} / GUÍA DE USO','small'),p(text,'h1')]
def table(head,rows,widths=None):
 data=[[p(c,'th') for c in head]]+[[p(str(c),'table') for c in row] for row in rows]
 t=Table(data,colWidths=widths or [WIDTH/len(head)]*len(head),hAlign='LEFT',repeatRows=1)
 t.setStyle(TableStyle([
  ('BACKGROUND',(0,0),(-1,0),GREEN),('VALIGN',(0,0),(-1,-1),'TOP'),
  ('ROWBACKGROUNDS',(0,1),(-1,-1),[PALE,colors.white]),
  ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
  ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
  ('LINEBELOW',(0,-1),(-1,-1),0.5,colors.HexColor('#d2ded5')),
 ]))
 return t


class Triangle(Flowable):
 def __init__(self):
  super().__init__(); self.width=WIDTH; self.height=310
 def draw(self):
  c=self.canv; tw=326; th=tw*math.sqrt(3)/2; x0=(WIDTH-tw)/2; y0=13
  def xy(v):
   sand,silt,clay=v
   return x0+tw*(silt+clay/2)/100,y0+th*clay/100
  for (name,verts),color in zip(REGIONS.items(),COLORS):
   path=c.beginPath(); path.moveTo(*xy(verts[0]))
   for v in verts[1:]: path.lineTo(*xy(v))
   path.close();c.setFillColor(colors.HexColor(color));c.setStrokeColor(colors.HexColor('#617368'));c.setLineWidth(.65);c.drawPath(path,fill=1,stroke=1)
  c.setStrokeColor(colors.Color(1,1,1,alpha=.48));c.setLineWidth(.35)
  for t in range(10,100,10):
   for v1,v2 in [((100-t,0,t),(0,100-t,t)),((t,100-t,0),(t,0,100-t)),((100-t,t,0),(0,t,100-t))]:
    c.line(*xy(v1),*xy(v2))
  c.setFillColor(INK);c.setFont('UIB',9)
  for i,(name,verts) in enumerate(REGIONS.items(),1):
   center=[sum(v[j] for v in verts)/len(verts) for j in range(3)]
   x,y=xy(center);c.drawCentredString(x,y-3,str(i))
  c.setFillColor(GREEN);c.setFont('UIB',10)
  c.drawCentredString(WIDTH/2,y0+th+9,'Arcilla 100 %')
  c.drawRightString(x0-6,y0-3,'Arena 100 %')
  c.drawString(x0+tw+6,y0-3,'Limo 100 %')
  x,y=xy((40,40,20));c.setFillColor(colors.HexColor('#c82e31'));c.setStrokeColor(colors.white);c.setLineWidth(1.5);c.circle(x,y,5.4,fill=1,stroke=1)
  c.setFont('UIB',9);c.setFillColor(colors.HexColor('#9b2326'));c.drawString(x+10,y-4,'A: 40 / 40 / 20')


def frame(c,doc):
 c.saveState()
 c.setFillColor(GREEN);c.rect(0,H-13,W,13,fill=1,stroke=0)
 c.setFont('UIB',8.5);c.setFillColor(TEAL);c.drawString(44,H-37,'SOIL TAXONOMY  /  MANUAL DE USUARIO')
 c.setStrokeColor(colors.HexColor('#d6e1d8'));c.line(44,43,W-44,43)
 c.setFont('UI',8);c.setFillColor(GRAY);c.drawString(44,29,'Versión local · 7 de septiembre de 2026')
 c.drawRightString(W-44,29,f'{doc.page}')
 c.restoreState()


story=[]
story += [Spacer(1,28),p('Manual de usuario','h1'),p('Soil Taxonomy','h1'),
 p('Del perfil de campo a una identificación documentada','h2'),
 p('Instrucciones para registrar observaciones, fotografías y ubicación, calcular la textura, recorrer las claves asistidas y utilizar la predicción con datos propios.'),
 p('<b>Alcance:</b> la ficha general sirve para cualquier perfil. Las claves guiadas disponibles cubren Hapludults y Dystrudepts. La textura y las predicciones estadísticas no sustituyen la determinación pedológica.'),
 p('Arranque rápido','h2'),p('1. Abre la carpeta del proyecto en VS Code.<br/>2. En la terminal PowerShell ejecuta el comando siguiente.<br/>3. Entra a la dirección que muestra Streamlit, normalmente http://127.0.0.1:8501.'),
 p('.\\.venv\\Scripts\\python.exe -m streamlit run app.py','code'),
 p('También puedes ejecutar <b>.\\iniciar.ps1</b>. Si el dashboard ya está activo, abre su enlace; no necesitas iniciar otro servidor.','small'),
 table(['Dónde encontrar cada tema','Página'],[
 ('Identificación, fecha y coordenadas','2'),('Fotografías y ayudas al pasar el cursor','3'),
 ('Formulario 2: cálculo y triángulo textural','4'),('Descripción y análisis por horizonte','5'),
 ('Diagnósticos, agua y control de evidencias','6'),('Ruta taxonómica y claves guiadas','7'),
 ('Predicción con CSV o Excel','8'),('Guardar, resolver errores y consultar fuentes','9'),
 ],[WIDTH-60,60]),
 p('Los datos numéricos de este manual son ejemplos didácticos. No representan un perfil real ni justifican por sí mismos un subgrupo.','small'),PageBreak()]

story += title(1,'Identifica y ubica el perfil')
story += [p('En <b>Perfil y subgrupo</b>, abre <b>1. Identificación, profundidad y regímenes</b>. Los campos numéricos vacíos significan que el dato no se midió; cero es un valor real.'),
 table(['Campo','Cómo completarlo'],[
 ('Identificador del perfil','Usa un código único, por ejemplo P-001. Repite el código en muestras y fotografías.'),
 ('Nombre del responsable','Escribe solo el nombre de quien realizó la descripción.'),
 ('Fecha de descripción','Selecciona la fecha en el calendario independiente. Se muestra día/mes/año y se exporta como AAAA-MM-DD.'),
 ('Profundidad y origen','Registra hasta dónde observaste y desde qué superficie mediste. No mezcles profundidad desde la superficie del suelo con profundidad desde la superficie mineral.'),
 ('Contacto y regímenes','Indica el contacto limitante y su profundidad si lo verificaste. Registra humedad y temperatura con la evidencia de sus criterios; no los deduzcas solo de la precipitación o del pH.'),
 ],[145,WIDTH-145]),
 p('Coordenadas geográficas','h2'),
 p('Abre <b>1B. Coordenadas y fotografías</b>. Elige <b>Geográficas (grados decimales)</b> y el datum de tu GPS. Escribe latitud y longitud: norte/este positivos, sur/oeste negativos. No pegues grados, minutos y segundos en estos campos.'),
 p('<b>Ejemplo:</b> latitud 8.982400; longitud -79.519900; datum WGS 84. Añade la precisión horizontal en metros si está disponible. El número de decimales no demuestra esa precisión.','code'),
 p('Coordenadas UTM','h2'),
 p('Elige <b>UTM (metros)</b>. Completa zona (1 a 60), hemisferio, Este y Norte. El hemisferio no es la letra de banda latitudinal. Para WGS 84 la app calcula también latitud y longitud.'),
 p('<b>Ejemplo de comprobación:</b> zona 17, Norte, Este 500000 m y Norte 1000000 m produce aproximadamente latitud 9.046562° y longitud -81.000000° (EPSG:32617).','code'),
 p('Con otro datum, escribe su nombre o código EPSG. La app conserva esas coordenadas sin transformarlas. Si no tienes ubicación, selecciona Sin registrar; no introduzcas valores ficticios.','small'),PageBreak()]

story += title(2,'Añade fotos y consulta las ayudas')
story += [p('Las fotografías complementan las observaciones. En <b>1B</b>, usa <b>Fotografías del perfil</b> para seleccionar uno o varios archivos del equipo.'),
 table(['Paso','Acción'],[
 ('1. Selecciona','Se admiten JPG/JPEG, PNG y WEBP: hasta 10 fotos, 20 MB por foto y 60 MB en conjunto. Cada imagen debe tener como máximo 40 megapíxeles.'),
 ('2. Comprueba','Revisa la vista previa. Un archivo dañado o no compatible se rechaza y no se incluye en la descarga.'),
 ('3. Describe','Completa Descripción / horizonte de la foto: profundidad o intervalo, orientación, escala y rasgo que muestra.'),
 ('4. Conserva','Al terminar, pulsa Descargar ficha + fotos (ZIP). Comprueba que están el JSON y la carpeta fotos.'),
 ],[90,WIDTH-90]),
 p('Qué conviene fotografiar','h2'),
 p('Incluye una vista completa del perfil con escala y código, acercamientos de los límites y estructura, y detalles de películas de arcilla, grietas o rasgos redox. Registra las condiciones de humedad al interpretar colores. Una imagen no demuestra por sí sola un horizonte diagnóstico.'),
 p('Ayuda breve en la propia app','h2'),
 table(['Dónde colocar el cursor','Qué explica la ayuda'],[
 ('Icono de ayuda junto a un campo','El significado del dato, su unidad y una precaución de llenado.'),
 ('Encabezado de una columna','Cómo registrar esa propiedad en la tabla de horizontes, diagnósticos, medidas adicionales o ruta taxonómica.'),
 ('Región o punto del triángulo','El nombre de la clase; sobre el punto, los porcentajes del horizonte seleccionado.'),
 ],[190,WIDTH-190]),
 p('Archivos descargables','h2'),
 p('<b>JSON:</b> ficha, coordenadas, fecha, resultados y referencias de fotos.<br/><b>ZIP:</b> el mismo JSON y los archivos originales de las fotos aceptadas.'),
 p('perfil_con_fotos.zip<br/>  perfil_taxonomico.json<br/>  fotos/01_perfil.jpg<br/>  fotos/02_detalle.png','code'),
 p('Las fotos se mantienen en la sesión, no se guardan automáticamente en una carpeta del proyecto. El JSON solo no contiene las imágenes. Descarga el ZIP antes de cerrar o recargar la sesión.','small'),PageBreak()]

story += title(3,'Calcula la textura en el formulario 2')
story += [p('En <b>2. Descripción y laboratorio por horizonte</b>, crea una fila y escribe su nombre, techo y base. Introduce <b>dos</b> porcentajes de arena, limo o arcilla, en cualquier orden. Confirma cada celda con Enter o sal de ella.'),
 p('<b>La tercera fracción = 100 - suma de las otras dos.</b> Ejemplo: arena 40 % + limo 40 % → arcilla 20 %. Resultado: <b>Franca (loam)</b>.'),
 Triangle(),
 table(['1–4','5–8','9–12'],[
 ('1 Arenosa','5 Franco limosa','9 Franco arcillo limosa'),
 ('2 Arenosa franca','6 Limosa','10 Arcillo arenosa'),
 ('3 Franco arenosa','7 Franco arcillo arenosa','11 Arcillo limosa'),
 ('4 Franca','8 Franco arcillosa','12 Arcillosa'),
 ]),
 p('El dibujo reproduce las regiones y el ejemplo del gráfico de la app. Los números identifican las clases en esta leyenda; en la app consulta la leyenda y pasa el cursor.','small'),
 p('La columna <b>Fracción calculada</b> identifica el valor derivado. Si cambias un dato medido, la derivada se actualiza. Si editas directamente el valor derivado, pasa a ser manual; borra una fracción para volver al cálculo automático.'),
 p('Elige <b>Horizonte para el triángulo</b> para cambiar el punto. Solo se representa una composición válida que sume 100 %. No se normalizan sumas incorrectas ni se generan porcentajes negativos.','small'),PageBreak()]

story += title(4,'Completa la descripción y el laboratorio')
story += [p('Añade filas en la tabla para cada horizonte o intervalo. Desplázate horizontalmente para ver todas las columnas. Elimina una fila solo si no corresponde al perfil; comprueba después los intervalos.'),
 table(['Grupo de campos','Qué debes registrar'],[
 ('Techo y base (cm)','Límites desde el mismo origen. La base debe ser mayor que el techo. No deben existir superposiciones ni intervalos sin describir dentro de la profundidad observada.'),
 ('Textura y fragmentos','Arena, limo y arcilla sobre la tierra fina (<2 mm), en masa. Los fragmentos >2 mm van aparte: no entran en esa suma. Identifica la base de su porcentaje.'),
 ('Color y morfología','Munsell húmedo y seco; estructura; películas de arcilla; rasgos redox. Ejemplo de notación: 10YR 3/2. Describe abundancia, ubicación y condición de la muestra.'),
 ('Carbono y pH','Carbono orgánico (%) no es materia orgánica (%). Registra pH en agua y KCl en columnas separadas, junto con la relación suelo:solución.'),
 ('Saturación de bases','Separa suma de cationes y NH4OAc pH 7. El método y profundidad deben coincidir con los exigidos por la clave.'),
 ('CIC y CICE','No mezcles cmolc/kg de suelo con cmolc/kg de arcilla. Documenta método y correcciones; no copies un resultado en las dos bases.'),
 ('Propiedades ándicas','Densidad aparente, retención de P, Al y Fe en oxalato y vidrio volcánico, con método y fracción analizada. La ceniza visible no reemplaza estos criterios.'),
 ('Sales y otros análisis','CaCO3 equivalente, yeso, CE del extracto saturado, sodio intercambiable, retención de agua a 1500 kPa y ODOE según el análisis disponible.'),
 ('Rasgos y trazabilidad','COLE, slickensides y nódulos/plintita. En Métodos / muestra / observaciones anota código de muestra y fuente de cada medición.'),
 ],[132,WIDTH-132]),
 p('Una fila ilustrativa','h2'),
 p('<b>A:</b> techo 0 cm, base 20 cm, arena 40 %, limo 40 %, arcilla calculada 20 %.<br/><b>Bw:</b> techo 20 cm, base 60 cm. Sus datos analíticos deben corresponder a ese intervalo; no reutilices los del horizonte A por conveniencia.'),
 p('La clase textural calculada es una clase general USDA. Las subdivisiones por tamaño de arena y las clases granulométricas de familia necesitan datos y criterios adicionales.','small'),PageBreak()]

story += title(5,'Evalúa diagnósticos y condiciones')
story += [p('En <b>3. Horizontes y propiedades diagnósticas</b>, revisa solo con evidencia las definiciones necesarias para tu ruta. La designación de campo Bt o Bw no demuestra por sí sola un horizonte argílico o cámbico.'),
 table(['Estado','Cuándo usarlo'],[
 ('No evaluado','Falta observación, análisis o revisión suficiente. No equivale a ausencia y no permite descartar una entrada de la clave.'),
 ('Presente','Cumple todos los requisitos de la definición. Registra techo, base y evidencia / método / criterio.'),
 ('Ausente','Se evaluó y no cumple la definición; conserva en la evidencia el motivo de descarte cuando resulte relevante.'),
 ],[105,WIDTH-105]),
 p('Agua y rasgos diferenciales','h2'),
 p('En <b>4. Saturación, reducción y rasgos diferenciales</b>, registra tipo y profundidad de saturación, días observados y evidencias de reducción. Distingue saturación, reducción y rasgos redox: no son sinónimos.'),
 p('Para grietas, registra ancho en <b>mm</b>, profundidad en <b>cm</b> y duración de apertura en días. La tabla adicional permite indicar espesores, techo de capas, volumen con propiedades frágicas, extensibilidad lineal, pendiente y materiales orgánicos.'),
 p('Días consecutivos y acumulados','h2'),
 p('Si hubo dos episodios de 12 días separados por un intervalo seco, el máximo consecutivo es 12 y el acumulado es 24. No escribas 24 como consecutivos. Los criterios de años normales deben sustentarse con su período y evidencia.'),
 p('Lee el control de evidencias','h2'),
 table(['Mensaje','Cómo actuar'],[
 ('Error de coherencia','Corrige profundidades incompatibles, superposiciones o porcentajes que no suman 100. No lo soluciones cambiando datos reales para forzar un resultado.'),
 ('Dato pendiente','Completa el intervalo o evidencia solicitados. Un diagnóstico presente sin respaldo queda pendiente.'),
 ('Diagnósticos no evaluados','El contador es informativo: la ruta determina cuáles hacen falta. No marques todos como ausentes para eliminar el contador.'),
 ],[125,WIDTH-125]),
 p('La app controla coherencia y documentación, pero no verifica automáticamente todas las relaciones entre análisis y definiciones diagnósticas.','small'),PageBreak()]

story += title(6,'Documenta la ruta hasta el subgrupo')
story += [p('En <b>5. Ruta taxonómica documentada</b>, completa cada nivel en secuencia. Consulta las <i>Keys to Soil Taxonomy</i>, 13.ª edición (2022), y descarta las entradas anteriores antes de aceptar una.'),
 table(['Nivel','Contenido requerido'],[
 ('Orden','Nombre oficial, código/página y evidencia de cumplimiento y descarte de los órdenes anteriores.'),
 ('Suborden','Repite el procedimiento dentro del orden confirmado.'),
 ('Gran grupo','Repite el procedimiento dentro del suborden confirmado.'),
 ('Subgrupo','Registra la determinación manual o utiliza una de las claves guiadas disponibles. La ruta manual no valida la existencia ni la coherencia del nombre escrito.'),
 ],[100,WIDTH-100]),
 p('Claves guiadas disponibles','h2'),
 p('<b>Ultisols → Udults → Hapludults:</b> 15 salidas de subgrupo.<br/><b>Inceptisols → Udepts → Dystrudepts:</b> 26 salidas de subgrupo.'),
 p('Abre <b>6. Identificación con claves guiadas</b> y selecciona el gran grupo. Los tres niveles superiores deben coincidir con la ruta requerida, estar documentados y tener la revisión <b>Cumple; anteriores descartados</b>.'),
 p('Para cada entrada, lee el texto oficial en inglés, incluidos AND/OR, espesores, profundidades y notas. Selecciona No cumple o Cumple y explica por qué. La guía se detiene en una entrada no evaluada o sin evidencia; toma la primera que cumple.'),
 p('Ejemplo condicionado, no diagnóstico de un perfil','h2'),
 p('Supón que Hapludults ya se determinó correctamente. Si HCGA se descarta con evidencia de continuidad y HCGB cumple por un contacto lítico a 40 cm desde la superficie mineral, la salida asistida es <b>Lithic Hapludults</b>. El ejemplo no confirma por sí mismo que el suelo pertenezca a Hapludults.'),
 p('<b>Typic no es una respuesta por falta de información.</b> Solo se alcanza tras descartar y documentar todas las entradas anteriores. Al modificar los datos del perfil, las respuestas de la guía se invalidan para revisarlas nuevamente.'),
 p('El resultado guiado y la propuesta manual se guardan por separado en el JSON. Para otros grandes grupos, utiliza las claves oficiales y la ruta manual.','small'),PageBreak()]

story += title(7,'Entrena y prueba con tus datos')
story += [p('La pestaña <b>Predicciones Geográficas (Carga tu Dataset)</b> utiliza un modelo estadístico. Su nombre no implica que genere un mapa. Predice la clase que selecciones en un CSV o Excel; no aplica las claves taxonómicas.'),
 table(['Paso','Acción'],[
 ('1. Prepara el archivo','Una fila por muestra/perfil y una columna por variable. CSV separado por comas o primera hoja de XLSX. Mantén unidades y métodos consistentes.'),
 ('2. Carga y revisa','Selecciona el archivo y comprueba las primeras filas. Las fotos del perfil se cargan en la primera pestaña, no en este cargador.'),
 ('3. Elige predictoras','Selecciona datos conocidos antes de predecir: propiedades, variables ambientales o categorías. Evita incluir el resultado y variables que lo revelen.'),
 ('4. Elige el resultado','Selecciona Orden_USDA, Subgrupo_USDA u otra clase conocida. Se requieren al menos dos clases con dos filas válidas por clase; ese mínimo permite ejecutar, no garantiza calidad.'),
 ('5. Revisa la evaluación','La app separa filas de entrenamiento y prueba, transforma números y categorías y muestra Accuracy en el conjunto reservado.'),
 ('6. Predice','Introduce las propiedades de una nueva muestra con las mismas unidades y pulsa Calcular Predicción con tus Datos. Revisa la clase y el gráfico de probabilidades.'),
 ],[105,WIDTH-105]),
 p('Cómo se tratan datos incompletos','h2'),
 p('Las filas sin etiqueta conocida se excluyen; no se inventa el resultado. Los valores predictivos faltantes se procesan dentro del flujo de entrenamiento. Una columna totalmente vacía o una clase con muy pocas filas genera un mensaje para corregir el archivo.'),
 p('Cómo interpretar Accuracy','h2'),
 p('Es la proporción de etiquetas acertadas en las filas reservadas. Un valor alto en pocos registros o en muestras muy relacionadas puede ser poco representativo. Las probabilidades del bosque aleatorio no constituyen certeza taxonómica ni una validación independiente.'),
 p('La ficha de campo no se incorpora automáticamente al entrenamiento. El modelo usa el archivo cargado y se vuelve a entrenar cuando interactúas con su configuración; esta versión no exporta el modelo entrenado.','small'),PageBreak()]

story += title(8,'Guarda el trabajo y resuelve dudas')
story += [p('Al terminar la primera pestaña, descarga <b>JSON</b> para la ficha o <b>ZIP</b> para ficha y fotos. El navegador elige la carpeta de descarga; la app no decide esa ubicación. Conserva el ZIP con un nombre que incluya perfil y fecha.'),
 p('<b>Antes de cerrar:</b> verifica nombre y fecha, datum y coordenadas, intervalos, fracciones calculadas, fuentes de diagnóstico y todas las fotos. Abre el ZIP y confirma que contiene el JSON y los archivos esperados.'),
 table(['Situación','Qué hacer'],[
 ('El punto no aparece','Completa dos fracciones válidas y confirma la celda. Si las tres son manuales, deben sumar 100 %. Selecciona el horizonte correcto.'),
 ('No quiero que un porcentaje sea calculado','Edita directamente la fracción derivada: se convierte en manual. Para reactivar el cálculo, deja una fracción vacía.'),
 ('La ubicación UTM no se convierte','Revisa zona, hemisferio, datum y unidades. La conversión solo está disponible para WGS 84 y dentro de la cobertura UTM.'),
 ('La foto no se acepta','Usa JPG, PNG o WEBP válido, dentro de los límites de tamaño, número total y resolución. Vuelve a seleccionar archivos si excediste el total.'),
 ('Subgrupo pendiente','Completa evidencias y niveles superiores. No saltes una entrada sin evaluar ni elijas Typic para evitar un dato faltante.'),
 ('Cerré o recargué y perdí los datos','La sesión no es un guardado permanente. Esta versión exporta JSON/ZIP, pero no los importa para restaurar el formulario. Conserva las descargas.'),
 ('No inicia Streamlit','Desde la carpeta del proyecto usa el Python de .venv. Si faltan dependencias, ejecuta el comando inferior. Usa el puerto que reporte la terminal.'),
 ],[166,WIDTH-166]),
 p('.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt','code'),
 p('Fuentes y alcance de esta edición','h2'),
 p('USDA-NRCS. <a href="https://www.nrcs.usda.gov/resources/guides-and-instructions/keys-to-soil-taxonomy" color="#32816b">Keys to Soil Taxonomy</a>, 13.ª ed., 2022: uso secuencial, pp. 66-67; Dystrudepts, pp. 224-227; Hapludults, pp. 330-331.<br/>USDA-NRCS. <a href="https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf" color="#32816b">Soil Survey Manual</a>, 2017, cap. 3, figura 3-7 y definiciones de las clases texturales; <a href="https://www.nrcs.usda.gov/resources/education-and-teaching-materials/soil-texture-calculator" color="#32816b">calculadora textural oficial</a>.<br/>NGA. <a href="https://earth-info.nga.mil/?action=coordsys&amp;dir=coordsys" color="#32816b">Coordinate Systems</a>: cobertura y parámetros UTM. Transformación local mediante PROJ/pyproj.','small'),
 p('Manual correspondiente a los campos y funciones implementados en la versión local del 07/09/2026. El triángulo es una figura explicativa de las mismas regiones usadas por la app, no una captura de pantalla.','small')]

path=OUT/'Manual_de_usuario_Soil_Taxonomy.pdf'
doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=60,bottomMargin=57,
    title='Manual de usuario - Soil Taxonomy',author='Proyecto Soil Taxonomy',subject='Registro de perfiles, fotografías, coordenadas, textura y clasificación asistida')
doc.build(story,onFirstPage=frame,onLaterPages=frame)
print(path)
