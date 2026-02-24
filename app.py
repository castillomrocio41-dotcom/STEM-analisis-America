import streamlit as st  # Crea la interfaz web (botones, títulos, sliders)
import pandas as pd     # Manipula los datos en tablas (DataFrames)
import numpy as np      # Realiza cálculos matemáticos (potencias, promedios)
import plotly.express as px  # Genera los gráficos interactivos y coloridos

# Cargar el archivo CSS externo
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =====================================================
# 1. DICCIONARIO DE TRADUCCIÓN (Multi-idioma)
# =====================================================
texts = {
    "ES": {
        "titulo": "📊 Análisis de Educación STEM",
        "subtitulo": "Análisis de graduados y paridad de género en América (Tendencias 1990-2025)",
        "sidebar_config": "Configuración",
        "seleccionar_idioma": "Seleccionar Idioma",
        "paises_sel": "Seleccionar Países:",
        "año_sel": "Rango de años:",
        "metrica_mujeres": "Paridad de Género (Mujeres %)",
        "ranking_titulo": "Ranking de Graduados en el año",
        "evolucion_titulo": "Evolución Histórica (Líneas)",
        "fuente_titulo": "📚 Fuentes y Referencias Oficiales",
        "fuente_texto": "Cifras normalizadas según informes de UNESCO y el Banco Mundial:",
        "descarga": "Ver tabla de datos detallada",
        "pais_eeuu": "EEUU",
        "pais_brasil": "Brasil",
        "pais_canada": "Canadá"
    },
    "EN": {
        "titulo": "📊 STEM Education Analysis",
        "subtitulo": "STEM graduates and gender parity analysis (Trends 1990-2025)",
        "sidebar_config": "Settings",
        "seleccionar_idioma": "Select Language",
        "paises_sel": "Select Countries:",
        "año_sel": "Year Range:",
        "metrica_mujeres": "Gender Parity (Women %)",
        "ranking_titulo": "Graduates Ranking in year",
        "evolucion_titulo": "Historical Evolution (Lines)",
        "fuente_titulo": "📚 Official Sources & References",
        "fuente_texto": "Figures normalized according to UNESCO and World Bank reports:",
        "descarga": "View detailed data table",
        "pais_eeuu": "USA",
        "pais_brasil": "Brazil",
        "pais_canada": "Canada"
    }
}

# =====================================================
# 2. BASE DE DATOS (Cifras Reales Macro)
# =====================================================
@st.cache_data 
def obtener_datos_stem():
    data = [
        (1990, "Argentina", 9200, 30, 4.0), (2022, "Argentina", 16800, 42, 5.1),
        (1990, "EEUU", 320000, 25, 5.0), (2022, "EEUU", 780000, 35, 5.6),
        (1990, "Brasil", 45000, 20, 3.8), (2022, "Brasil", 115000, 33, 6.0),
        (1990, "México", 35000, 18, 3.5), (2022, "México", 138000, 30, 5.2),
        (1990, "Canadá", 28000, 28, 6.0), (2022, "Canadá", 75000, 38, 6.5),
        (1990, "Chile", 5800, 15, 3.2), (2022, "Chile", 15200, 28, 5.0),
    ]
    return pd.DataFrame(data, columns=["año", "pais", "graduados", "mujeres_pct", "gasto_pbi"])

# =====================================================
# 3. PROCESAMIENTO MATEMÁTICO (Interpolación y Proyección)
# =====================================================
def procesar_dataset(df):
    paises = df["pais"].unique()
    lista_completa = []
    
    for pais in countries: # Se cambió la variable para evitar conflictos
        sub_df = df[df["pais"] == pais].set_index("año")
        años_todos = pd.DataFrame(index=range(1990, 2026)) 
        sub_df = años_todos.join(sub_df).interpolate(method='linear')
        
        ultima_grad = sub_df.loc[2022, "graduados"]
        for a in range(2023, 2026):
            sub_df.loc[a, "graduados"] = ultima_grad * (1.02 ** (a - 2022))
            sub_df.loc[a, "pais"] = pais
            sub_df.loc[a, "mujeres_pct"] = sub_df.loc[2022, "mujeres_pct"]
            sub_df.loc[a, "gasto_pbi"] = sub_df.loc[2022, "gasto_pbi"]
        
        lista_completa.append(sub_df.reset_index().rename(columns={"index": "año"}))
        
    return pd.concat(lista_completa)

# =====================================================
# 4. INTERFAZ Y CONFIGURACIÓN VISUAL
# =====================================================
st.set_page_config(page_title="Ro's STEM Analytics", layout="wide")

lang = st.sidebar.radio("🌐 Select Language / Idioma", ["ES", "EN"])
t = texts[lang] 

st.title(t["titulo"])
st.markdown(t["subtitulo"])

df_final = procesar_dataset(obtener_datos_stem())

def traducir_pais(nombre):
    traducciones = {"EEUU": t["pais_eeuu"], "Brasil": t["pais_brasil"], "Canadá": t["pais_canada"]}
    return traducciones.get(nombre, nombre)

opciones_paises = [p for p in df_final["pais"].unique() if pd.notna(p)]

paises_seleccionados = st.sidebar.multiselect(
    t["paises_sel"], 
    options=opciones_paises,
    default=["Argentina", "EEUU", "Brasil", "México"],
    format_func=traducir_pais
)

rango_años = st.sidebar.slider(t["año_sel"], 1990, 2025, (1990, 2025))

# FILTRO MEJORADO
df_filtrado = df_final[
    (df_final["pais"].isin(paises_seleccionados)) & 
    (df_final["año"].between(rango_años[0], rango_años[1]))
]

# =====================================================
# 5. GRÁFICOS (Evolución y Ranking) - ARREGLADO
# =====================================================
if not df_filtrado.empty:
    col_izq, col_der = st.columns([2, 1]) 

    with col_izq:
        st.subheader(t["evolucion_titulo"])
        # Cambiamos spline por linear si hay pocos datos para asegurar visibilidad
        forma_linea = "spline" if len(df_filtrado["año"].unique()) > 1 else "linear"
        
        fig_line = px.line(df_filtrado, x="año", y="graduados", color="pais", 
                           line_shape=forma_linea,
                           markers=True, # Siempre muestra los puntos
                           template="plotly_dark")

        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        fig_line.for_each_trace(lambda trace: trace.update(name=traducir_pais(trace.name)))
        st.plotly_chart(fig_line, use_container_width=True)

    with col_der:
        # AQUÍ ESTÁ EL CAMBIO CLAVE: Usamos el año final del slider para el Ranking
        año_ranking = rango_años[1]
        st.subheader(f"{t['ranking_titulo']} {año_ranking}")
        
        # Buscamos los datos exactos para el año que marca el slider a la derecha
        data_ranking = df_filtrado[df_filtrado["año"] == año_ranking].sort_values("graduados")
        
        if not data_ranking.empty:
            fig_bar = px.bar(data_ranking, x="graduados", y="pais", 
                             orientation='h', color="graduados", 
                             color_continuous_scale="Agsunset",
                             template="plotly_dark")
            
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                coloraxis_showscale=False, 
                yaxis={'tickmode': 'array', 'tickvals': data_ranking['pais'], 
                       'ticktext': [traducir_pais(n) for n in data_ranking['pais']]}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay datos para este año específico.")

else:
    st.warning("Selecciona al menos un país y un rango de años.")

# =====================================================
# 6. SECCIÓN DE FUENTES
# =====================================================
st.divider() 
st.subheader(t["fuente_titulo"])
st.info(f"{t['fuente_texto']} UNESCO Institute for Statistics & World Bank Open Data.")

with st.expander(t["descarga"]):
    st.dataframe(df_filtrado, use_container_width=True)