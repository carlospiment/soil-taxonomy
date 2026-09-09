import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from profile_ui import render_profile
from structure_ui import render_estructura_usda
from color_ui import render_color
from storage_ui import render_study_import, render_study_export

# Configuración de la página del Dashboard
st.set_page_config(page_title="SoilTaxonomy AI Dashboard", layout="wide", page_icon="🌱")

st.title("🌱 Dashboard de Clasificación y Predicción de Suelos (USDA)")
st.write("Herramienta estructurada de IA convencional para la investigación edafológica.")
render_study_import()

# Crear las pestañas del Dashboard
tab1, tab2, tab3, tab4 = st.tabs(["🔬 Perfil y subgrupo", "🌍 Predicciones Geográficas (Carga tu Dataset)", "Análisis de Estructura USDA", "Color: región y calidad"])

# ==========================================
# PESTAÑA 1: CLASIFICADOR DE LABORATORIO
# ==========================================
with tab1:
    render_profile()


with tab2:
    st.header("Predicción Personalizada mediante Machine Learning")
    st.write("Sube tus propios datos de investigación para entrenar un modelo predictivo.")

    # 1. Cargador de Archivo (Excel o CSV)
    archivo_subido = st.file_uploader("Sube tu archivo de datos de suelos (.xlsx o .csv)", type=["xlsx", "csv"], help="Una fila por muestra/perfil y una columna por variable. Incluye la clase conocida para entrenar; CSV separado por comas o primera hoja de Excel.")

    if archivo_subido is not None:
        # Leer el archivo dependiendo de la extensión
        try:
            if archivo_subido.name.lower().endswith('.xlsx'):
                df = pd.read_excel(archivo_subido)
            else:
                df = pd.read_csv(archivo_subido)
            df.columns = df.columns.map(str)
            if df.empty or not df.columns.is_unique:
                raise ValueError("El archivo debe tener filas y nombres de columnas únicos.")
            
            st.success("¡Archivo cargado con éxito!")
            st.write("Vista previa de tus datos (primeras 5 filas):")
            st.dataframe(df.head())

            # 2. Selección de Columnas para la IA
            st.subheader("Configuración del Modelo de IA")
            columnas = df.columns.tolist()
            
            col_features = st.multiselect(
                "Selecciona las columnas predictoras (ej. Altitud, Precipitación, pH, etc.)", 
                columnas, key="ml_features", help="Variables conocidas antes de predecir: mediciones numéricas o categorías. Excluye la columna resultado y los identificadores sin significado predictivo."
            )
            col_target = st.selectbox(
                "Selecciona la columna que contiene el resultado (ej. Orden_USDA o Subgrupo_USDA)", 
                [None] + columnas, key="ml_target", help="Clase conocida que quieres aprender, por ejemplo Subgrupo_USDA. Se requieren dos clases y al menos dos filas por clase."
            )

            # 3. Entrenamiento si las columnas están seleccionadas
            if col_features and col_target:
                if col_target in col_features:
                    raise ValueError("La columna resultado no puede ser también predictora.")
                # No inventar etiquetas para las filas sin resultado conocido.
                validas = df[col_target].notna() & df[col_target].astype(str).str.strip().ne("")
                if not validas.all():
                    st.info(f"Se excluyeron {(~validas).sum()} filas sin resultado conocido.")
                X = df.loc[validas, col_features].copy()
                y = df.loc[validas, col_target].astype(str)
                numericas = X.select_dtypes(include="number").columns.tolist()
                categoricas = [c for c in col_features if c not in numericas]
                X[numericas] = X[numericas].astype(float).replace([np.inf, -np.inf], np.nan)
                for c in categoricas:
                    X[c] = X[c].map(lambda v: str(v) if pd.notna(v) else np.nan)
                vacias = X.columns[X.isna().all()].tolist()
                if vacias:
                    raise ValueError(f"Estas predictoras no tienen valores válidos: {', '.join(vacias)}")
                conteos = y.value_counts()
                if len(conteos) < 2 or conteos.min() < 2:
                    raise ValueError("Se necesitan al menos dos clases y dos filas con resultado por clase.")
                n_prueba = max(len(conteos), int(np.ceil(len(y) * 0.2)))
                
                # Separar datos de entrenamiento y prueba
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=n_prueba, random_state=42, stratify=y
                )
                
                # Aprender el tratamiento de datos solo con entrenamiento y
                # reutilizarlo sin alterar las columnas durante la predicción.
                preprocesador = ColumnTransformer([
                    ("numericas", SimpleImputer(strategy="median", keep_empty_features=True), numericas),
                    ("categoricas", Pipeline([
                        ("faltantes", SimpleImputer(strategy="constant", fill_value="(sin dato)", keep_empty_features=True)),
                        ("codificacion", OneHotEncoder(handle_unknown="ignore")),
                    ]), categoricas),
                ])
                modelo_personalizado = Pipeline([
                    ("preprocesamiento", preprocesador),
                    ("clasificador", RandomForestClassifier(n_estimators=100, random_state=42)),
                ])
                modelo_personalizado.fit(X_train, y_train)
                
                # Calcular Precisión
                y_pred = modelo_personalizado.predict(X_test)
                precision = accuracy_score(y_test, y_pred)
                
                st.metric(label="Precisión del modelo entrenado (Accuracy)", value=f"{precision*100:.2f}%")
                st.caption(f"Evaluación sobre {len(y_test)} filas reservadas; entrenamiento con {len(y_train)} filas.")
                
                # 4. Formulario de predicción interactiva para el usuario
                st.subheader("🤖 Probar el modelo entrenado")
                st.write("Introduce nuevos valores ambientales para predecir la clase seleccionada:")
                
                inputs_usuario = {}
                col_inputs = st.columns(min(3, len(col_features)))
                
                for i, col_name in enumerate(col_features):
                    with col_inputs[i % len(col_inputs)]:
                        # Detectar si la columna original es numérica o categórica para dar el input correcto
                        if col_name in numericas:
                            val_medio = float(X[col_name].median())
                            inputs_usuario[col_name] = st.number_input(f"{col_name}", value=val_medio, key=f"predict_{col_name}", help="Usa la misma unidad y método que en el dataset. El valor inicial es la mediana de los datos disponibles.")
                        else:
                            opciones = sorted(X[col_name].dropna().unique().tolist())
                            inputs_usuario[col_name] = st.selectbox(f"{col_name}", opciones, key=f"predict_{col_name}", help="Selecciona la categoría de la nueva muestra, usando el vocabulario del dataset.")

                if st.button("Calcular Predicción con tus Datos", key="ml_predict"):
                    # Crear DataFrame con la fila ingresada
                    df_usuario = pd.DataFrame([inputs_usuario], columns=col_features)
                    pred_resultado = modelo_personalizado.predict(df_usuario)[0]
                    probabilidades = modelo_personalizado.predict_proba(df_usuario)[0]
                    
                    st.success(f"**El suelo predicho es:** {pred_resultado}")
                    
                    # Gráfico de probabilidades
                    df_prob = pd.DataFrame({
                        'Orden': modelo_personalizado.classes_,
                        'Confianza (%)': probabilidades * 100
                    }).sort_values(by='Confianza (%)', ascending=False)
                    st.bar_chart(df_prob.set_index('Orden'))

        except Exception as e:
            st.error(f"No se pudo procesar el archivo o entrenar el modelo: {e}")
            
    else:
        st.info("A la espera de un archivo Excel o CSV para activar las funciones de Machine Learning.")


with tab3:
    render_estructura_usda()

with tab4:
    render_color()

render_study_export()
