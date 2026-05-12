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

    #FILTRO ERRORES EN COLUMNAS
    bd["ESTAMPAS"] = pd.to_numeric(bd["ESTAMPAS"], errors="coerce").fillna(0)
    if "REPETIDAS" in bd.columns:
        bd["REPETIDAS"] = pd.to_numeric(bd["REPETIDAS"], errors="coerce").fillna(0)

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
        xpais.index = xpais.index + 1

        st.dataframe(xpais, use_container_width=True, height=350, hide_index=True)

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

                if tiene_estampa >= 1:
                    st.success(f"✅ Ya tienes a {nombre_completo} de {jugador_pais}")
                else:
                    st.warning(f"❌ Te falta conseguir a {nombre_completo} de {jugador_pais}")
            else:
                st.error("⚠️ ID no existente en tu base de datos. Verifica!!")
    
    st.divider()

    #INTERCAMBIOS
    st.header("🔄 Intercambios")
    col_rep1, col_rep2 = st.columns(2)

    with col_rep1:
        st.subheader("📦 Repetidas")
        st.write("Lista de tus estampas disponibles para cambiar:")
        
        # Verificamos que la columna REPETIDAS
        if 'REPETIDAS' in bd.columns:
            # Filtramos REPETIDAS sea mayor a 0
            df_repetidas = bd[bd['REPETIDAS'] > 0]
            
            if not df_repetidas.empty:
                # Seleccionamos las columnas
                tabla_rep = df_repetidas[['ID', 'NOMBRE', 'APELLIDO', 'PAIS', 'REPETIDAS']].reset_index(drop=True)
                tabla_rep.index = tabla_rep.index + 1
                
                # Usamos key="busc_rep" para que no interfiera con el otro buscador
                buscar_rep = st.text_input("🔍 Buscar ID en repetidas (Ej: MEX o MEX-02):", key="busc_rep").upper().strip()
                
                if buscar_rep:
                    # Filtramos la tabla usando str.contains para coincidencias exactas o parciales
                    tabla_rep = tabla_rep[tabla_rep['ID'].str.contains(buscar_rep)]
                
                if not tabla_rep.empty:
                    tabla_rep.index = tabla_rep.index + 1
                    st.dataframe(tabla_rep, use_container_width=True, height=300, hide_index=True)
                    st.info(f"Se muestran {int(tabla_rep['REPETIDAS'].sum())} estampas para intercambiar en esta lista.")
                else:
                    st.warning("No tienes repetidas que coincidan con esa búsqueda.")
            else:
                st.info("No tienes estampas repetidas registradas.")
        else:
            st.warning("No se encontró la columna REPETIDAS en tu Google Sheet.")

    with col_rep2:
        st.subheader("🤝 Oportunidad de Intercambio")
        st.write("Escribe los IDs de las repetidas para ver cuales te sirven:")
        
        # Espacio para escribir los IDs
        lista_ids_amigos = st.text_area("Ejemplo: MEX-01, ARG-04, BRA-10", height=100)
        
        if lista_ids_amigos:
            # Separamos por comas, quitamos espacios extra y convertimos a mayúsculas
            ids_limpios = [x.strip().upper() for x in lista_ids_amigos.split(",") if x.strip()]
            
            # Buscamos en la base de datos: que el ID esté en la lista que pegaste Y que NO la tengas (ESTAMPAS == 0)
            me_faltan = bd[(bd['ID'].isin(ids_limpios)) & (bd['ESTAMPAS'] == 0)]
            
            if not me_faltan.empty:
                st.success(f"🎉 De esa lista, sirven {len(me_faltan)} estampas:")
                tabla_faltantes = me_faltan[['ID', 'NOMBRE', 'APELLIDO', 'PAIS']].reset_index(drop=True)
                tabla_faltantes.index = tabla_faltantes.index + 1
                st.dataframe(tabla_faltantes, use_container_width=True, hide_index=True)
            else:
                st.warning("😭 De esa lista no te sirve ninguna")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
