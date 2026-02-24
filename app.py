import streamlit as st  # La herramienta que crea la página web
import pandas as pd     # La herramienta que maneja tablas de datos (como Excel)
import numpy as np      # Herramienta para cálculos matemáticos avanzados
import plotly.express as px  # Herramienta para hacer gráficos interactivos "pro"

# =====================================================
# 1. DICCIONARIO DE TRADUCCIÓN
# =====================================================
# Esto es como un "traductor automático" interno. 
# Según el idioma elegido, la app busca las palabras en este cofre.
texts = {
    "ES": {
        "titulo": "📊 Análisis de Educación STEM",
        "subtitulo": "Análisis de graduados y paridad de género en América (1990-2030)",
        "sidebar_config": "Configuración",
        "seleccionar_idioma": "Seleccionar Idioma",
        "paises_sel": "Seleccionar Países:",
        "anio_sel": "Rango de años:",
        "metrica_mujeres": "Paridad de Género (Mujeres %)",
        "ranking_titulo": "Ranking de Graduados en el año",
        "evolucion_titulo": "Evolución Histórica (Líneas)",
        "fuente_dato": "Fuente: Banco Mundial / UNESCO",
        "descarga": "Ver tabla de datos detallada"
    },
    "EN": {
        "titulo": "📊 STEM Education Analysis",
        "subtitulo": "STEM graduates and gender parity analysis (1990-2030)",
        "sidebar_config": "Settings",
        "seleccionar_idioma": "Select Language",
        "paises_sel": "Select Countries:",
        "anio_sel": "Year Range:",
        "metrica_mujeres": "Gender Parity (Women %)",
        "ranking_titulo": "Graduates Ranking in year",
        "evolucion_titulo": "Historical Evolution (Lines)",
        "fuente_dato": "Source: World Bank / UNESCO",
        "descarga": "View detailed data table"
    }
}

# =====================================================
# 2. CARGA DE DATOS (Nuestra base de información)
# =====================================================
@st.cache_data # Esto le dice a la web: "No vuelvas a leer esto cada vez, guardalo en memoria"
def obtener_datos_stem():
    # Creamos una lista con datos reales/estimados de graduados STEM
    # Formato: (Año, País, Cantidad de Graduados, % de Mujeres, % Inversión PBI)
    data = [
        (1990, "Argentina", 15, 30, 4.0), (2000, "Argentina", 22, 32, 4.5), (2010, "Argentina", 35, 38, 5.0), (2022, "Argentina", 48, 42, 5.1),
        (1990, "USA", 300, 25, 5.0), (2000, "USA", 450, 28, 5.2), (2010, "USA", 580, 31, 5.4), (2022, "USA", 820, 35, 5.6),
        (1990, "Brasil", 40, 20, 3.8), (2000, "Brasil", 65, 24, 4.2), (2010, "Brasil", 110, 29, 5.5), (2022, "Brasil", 190, 33, 6.0),
        (1990, "México", 30, 18, 3.5), (2000, "México", 55, 22, 4.0), (2010, "México", 95, 27, 4.8), (2022, "México", 160, 30, 5.2),
        (1990, "Canadá", 40, 28, 6.0), (2000, "Canadá", 60, 30, 6.2), (2010, "Canadá", 85, 34, 6.4), (2022, "Canadá", 120, 38, 6.5),
        (1990, "Chile", 8, 15, 3.2), (2000, "Chile", 15, 19, 3.8), (2010, "Chile", 28, 24, 4.5), (2022, "Chile", 45, 28, 5.0),
    ]
    # Convertimos esa lista en un DataFrame (una tabla inteligente de Pandas)
    return pd.DataFrame(data, columns=["anio", "pais", "graduados", "mujeres_pct", "gasto_pbi"])

# =====================================================
# 3. PROCESAMIENTO MATEMÁTICO (Lógica de la OMA)
# =====================================================
def procesar_dataset(df):
    paises = df["pais"].unique() # Identifica todos los países sin repetirlos
    lista_completa = []
    
    for pais in paises:
        # Filtramos la tabla solo para el país que estamos analizando en este ciclo
        sub_df = df[df["pais"] == pais].set_index("anio")
        
        # INTERPOLACIÓN: Si tenemos el dato de 1990 y el de 2000, 
        # esta línea rellena los años 91, 92, 93... con una estimación lineal.
        anios_todos = pd.DataFrame(index=range(1990, 2031))
        sub_df = anios_todos.join(sub_df).interpolate(method='linear')
        
        # PROYECCIÓN AL 2030: Tomamos el último dato real (2022) 
        # y le sumamos un 2% de crecimiento por cada año que pasa.
        ultima_grad = sub_df.loc[2022, "graduados"]
        for a in range(2023, 2031):
            anios_pasados = a - 2022
            sub_df.loc[a, "graduados"] = ultima_grad * (1.02 ** anios_pasados)
            sub_df.loc[a, "pais"] = pais
            # Mantenemos los otros datos estables para no inventar de más
            sub_df.loc[a, "mujeres_pct"] = sub_df.loc[2022, "mujeres_pct"]
            sub_df.loc[a, "gasto_pbi"] = sub_df.loc[2022, "gasto_pbi"]
            
        lista_completa.append(sub_df.reset_index().rename(columns={"index": "anio"}))
    
    # Unimos todos los países procesados en una sola tabla gigante
    return pd.concat(lista_completa)

# =====================================================
# 4. DISEÑO DE LA PÁGINA (Frontend)
# =====================================================
# Configuramos la pestaña del navegador para que ocupe toda la pantalla (wide)
st.set_page_config(page_title="Ro's STEM Monitor", layout="wide")

# Seleccionador de idioma en el costado izquierdo (Sidebar)
lang = st.sidebar.radio("🌐 Select Language / Idioma", ["ES", "EN"])
t = texts[lang] # 't' ahora contiene todas las palabras en el idioma elegido

st.title(t["titulo"])
st.markdown(t["subtitulo"])

# Ejecutamos las funciones de datos que explicamos arriba
df_final = procesar_dataset(obtener_datos_stem())

# -- Controles de la izquierda --
st.sidebar.header(t["sidebar_config"])

# Selector múltiple de países
paises_seleccionados = st.sidebar.multiselect(
    t["paises_sel"], 
    options=list(df_final["pais"].unique()),
    default=["Argentina", "USA", "Brasil", "México"]
)

# El deslizador (slider) para elegir los años
rango_anios = st.sidebar.slider(t["anio_sel"], 1990, 2030, (1990, 2030))

# FILTRO FINAL: Creamos una tabla que solo tiene lo que el usuario eligió
df_filtrado = df_final[
    (df_final["pais"].isin(paises_seleccionados)) & 
    (df_final["anio"].between(rango_anios[0], rango_anios[1]))
]

# =====================================================
# 5. TARJETAS DE MÉTRICAS (KPIs)
# =====================================================
# Dividimos la pantalla en 3 columnas
c1, c2, c3 = st.columns(3)

if not df_filtrado.empty:
    # Miramos solo el último año del rango elegido para las tarjetas
    data_ahora = df_filtrado[df_filtrado["anio"] == rango_anios[1]]
    
    # Calculamos el promedio de mujeres en STEM
    avg_mujeres = data_ahora["mujeres_pct"].mean()
    
    # Delta: La diferencia con el año anterior para saber si subió o bajó
    prev_mujeres = df_final[df_final["anio"] == rango_anios[1]-1]["mujeres_pct"].mean()
    cambio = avg_mujeres - prev_mujeres

    # Mostramos las tarjetas con color (verde si sube, rojo si baja)
    c1.metric(t["metrica_mujeres"], f"{avg_mujeres:.1f}%", f"{cambio:.1f}%")
    c2.metric("Total Countries", len(paises_seleccionados))
    c3.metric("Status", "Projections Active" if rango_anios[1] > 2022 else "Historical")

# =====================================================
# 6. GRÁFICOS INTERACTIVOS
# =====================================================
col_izq, col_der = st.columns([2, 1]) # La columna izquierda es el doble de ancha

with col_izq:
    st.subheader(t["evolucion_titulo"])
    # Gráfico de líneas con Plotly (permite hacer zoom y ver datos al pasar el mouse)
    fig_line = px.line(df_filtrado, x="anio", y="graduados", color="pais", 
                       template="plotly_dark", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

with col_der:
    st.subheader(f"{t['ranking_titulo']} {rango_anios[1]}")
    # Gráfico de barras horizontales para el ranking del año final elegido
    fig_bar = px.bar(data_ahora.sort_values("graduados"), x="graduados", y="pais", 
                     orientation='h', color="graduados", color_continuous_scale="Agsunset")
    # Quitamos la leyenda de colores para que se vea más limpio
    fig_bar.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# =====================================================
# 7. ANÁLISIS ECONÓMICO (Burbujas)
# =====================================================
st.divider() # Una línea decorativa
st.subheader(f"💡 {t['fuente_dato']}: Gasto PBI vs Graduados")

# Gráfico de burbujas: el tamaño de la burbuja depende de la cantidad de graduados
fig_scatter = px.scatter(data_ahora, x="gasto_pbi", y="graduados", 
                         size="graduados", color="pais", hover_name="pais",
                         size_max=60, template="plotly_white")
st.plotly_chart(fig_scatter, use_container_width=True)

# Sección expandible para ver los "números crudos"
with st.expander(t["descarga"]):
    st.write("Explora la tabla completa que generó los gráficos:")
    st.dataframe(df_filtrado, use_container_width=True)