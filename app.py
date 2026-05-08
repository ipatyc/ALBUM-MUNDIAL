
import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Mi Álbum del Mundial ⚽", layout="wide")
st.title("⚽ Control de mi Álbum del Mundial 2026")

# base de datos
SHEET_URL = "https://docs.google.com/spreadsheets/d/1jKeKGxcNwWWFma1gxgLWNkHrX4uNsUWf9AQQB0hagzg/export?format=csv"

#cache bd
@st.cache_data(ttl=60)
def cargar_datos(url):
    return pd.read_csv(url)

try:
    with st.spinner("Descargando base de datos desde Google Sheets... ⏳"):
        bd = cargar_datos(SHEET_URL)

    bd = bd.fillna("")

    # MÉTRICAS GENERALES 
    total_coleccionadas = bd['ESTAMPAS'].sum()
    total_registros = len(bd)

    col_m1, col_m2 = st.columns(2)
    col_m1.metric(label="✅ Estampas que tengo", value=int(total_coleccionadas))
    col_m2.metric(label="🗂️ Total de estampas", value=total_registros)

    st.divider()

    # Creamos dos columnas para organizar la información
    col_izq, col_der = st.columns(2)

    # Aparecerá en la mitad izquierda
    with col_izq:
        st.header("🌍 Avance por País")

        xpais = bd.groupby("PAIS")["ESTAMPAS"].sum().reset_index()
        xpais["COMPLETADO%"] = (xpais["ESTAMPAS"] / 20) * 100
        xpais = xpais.sort_values(by="ESTAMPAS", ascending=False).reset_index(drop=True)

        # NUEVO: height=350 mantiene la tabla contenida en un cuadro pequeño
        st.dataframe(xpais, use_container_width=True, height=350)

    # Aparecerá en la mitad derecha
    with col_der:
        st.header("🔍 Buscador de Estampas")
        st.write("Escribe el ID para saber si ya lo tienes (ejemplo: MEX-02)")

        id_buscado = st.text_input("Ingresa el ID:")

        if id_buscado:
            id_buscado = id_buscado.upper()
            resultado = bd[bd['ID'] == id_buscado]

            if not resultado.empty:
                tiene_estampa = resultado['ESTAMPAS'].values[0]
                jugador_nombre = resultado['NOMBRE'].values[0]
                jugador_apellido = resultado['APELLIDO'].values[0]
                jugador_pais = resultado['PAIS'].values[0]

                nombre_completo = f"{jugador_nombre} {jugador_apellido}".strip()

                if tiene_estampa == 1:
                    st.success(f"✅ Ya tienes a {nombre_completo} de {jugador_pais}")
                else:
                    st.warning(f"❌ Te falta conseguir a {nombre_completo} de {jugador_pais}")
            else:
                st.error("⚠️ ID no existente en tu base de datos. Verifica!!")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
