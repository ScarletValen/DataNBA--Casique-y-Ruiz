import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="NBA Interactive Analytics", layout="wide", page_icon="")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_csv('30. NBA.csv')
    df['GAME_DATE_EST'] = pd.to_datetime(df['GAME_DATE_EST'])
    return df

df_raw = load_data()

# --- SIDEBAR INTERACTIVA ---
st.sidebar.header("Configuración del Análisis")
temporada_sel = st.sidebar.selectbox("Selecciona la Temporada", sorted(df_raw['SEASON'].unique(), reverse=True), index=3) # Index 3 suele ser 2019

# Filtrar datos por la temporada seleccionada
df = df_raw[df_raw['SEASON'] == temporada_sel].copy()

# --- TÍTULO ---
st.title(f" Análisis Interactivo NBA: Temporada {temporada_sel}")
st.markdown(f"Análisis del impacto de la localía basado en **{len(df)}** partidos.")

# --- PROCESAMIENTO PARA GRÁFICOS ---
# Agregados por equipo
home_stats = df.groupby('TEAM_ID_home').agg({
    'HOME_TEAM_WINS': 'mean',
    'PTS_home': 'mean', 'FG_PCT_home': 'mean', 'FG3_PCT_home': 'mean',
    'AST_home': 'mean', 'REB_home': 'mean'
}).reset_index()

away_stats = df.groupby('TEAM_ID_away').agg({
    'PTS_away': 'mean', 'FG_PCT_away': 'mean', 'FG3_PCT_away': 'mean',
    'AST_away': 'mean', 'REB_away': 'mean'
}).reset_index()

# Unir y calcular diferenciales
comparativa = pd.merge(home_stats, away_stats, left_on='TEAM_ID_home', right_on='TEAM_ID_away')
comparativa['DIFF_PTS'] = comparativa['PTS_home'] - comparativa['PTS_away']
comparativa['WIN_PCT_HOME'] = comparativa['HOME_TEAM_WINS'] * 100

# --- TABS INTERACTIVAS ---
tab1, tab2, tab3 = st.tabs(["🎯 Victoria Local", "📊 Comparativa Local/Visita", "📈 Correlaciones"])

with tab1:
    st.subheader("Objetivo A: Porcentaje de Victorias en Casa")
    
    # Gráfico de barras interactivo
    fig_win = px.bar(comparativa.sort_values('WIN_PCT_HOME', ascending=False), 
                     x='TEAM_ID_home', y='WIN_PCT_HOME',
                     color='WIN_PCT_HOME',
                     labels={'WIN_PCT_HOME': '% Victoria Local', 'TEAM_ID_home': 'ID Equipo'},
                     title="Efectividad de cada equipo jugando en casa",
                     color_continuous_scale='RdBu')
    st.plotly_chart(fig_win, use_container_width=True)
    st.info("Pasa el mouse sobre las barras para ver el ID del equipo y su porcentaje exacto.")

with tab2:
    st.subheader("Objetivo B: E (Diferenciales)")
    
    # Selector interactivo de métrica
    metrica = st.selectbox("Selecciona la estadística para comparar:", 
                          ['Puntos (PTS)', 'Asistencias (AST)', 'Rebotes (REB)','Porcentaje de tiros de campo (FG_PCT)'])
    
    dict_metrica = {
        'Puntos (PTS)': 'DIFF_PTS',
        'Asistencias (AST)': 'AST_home',     }
    
    # Gráfico de dispersión para ver consistencia
    fig_diff = px.scatter(comparativa, x='PTS_away', y='PTS_home', 
                          size='WIN_PCT_HOME', color='DIFF_PTS',
                          hover_name='TEAM_ID_home',
                          labels={'PTS_away': 'Promedio Puntos Visita', 'PTS_home': 'Promedio Puntos Casa'},
                          title="Rendimiento: Casa vs Visita (El tamaño indica % de Victoria)",
                          color_continuous_scale='Viridis')
    
    # Añadir línea de referencia (donde Casa = Visita)
    fig_diff.add_shape(type="line", x0=90, y0=90, x1=130, y1=130, line=dict(color="Red", dash="dash"))
    
    st.plotly_chart(fig_diff, use_container_width=True)

with tab3:
    st.subheader("Objetivo C: Factores Críticos de Victoria")
    
    # Matriz de correlación visual
    corr_cols = ['PTS_home', 'AST_home', 'REB_home', 'FG_PCT_home', 'FG3_PCT_home', 'HOME_TEAM_WINS']
    df_corr = df[corr_cols].corr()
    
    fig_corr = px.imshow(df_corr, text_auto=True, aspect="auto",
                         title="Mapa de Calor",
                         color_continuous_scale='Blues')
    st.plotly_chart(fig_corr, use_container_width=True)
    
    st.write("Interpretación: Los valores más cercanos a 1 indican una relación más fuerte con la victoria local.")

# --- SECCIÓN EXTRA: BUSCADOR DE EQUIPOS ---
st.divider()
st.subheader("🔍 Consulta Individual por Equipo")
equipo_id = st.number_input("Ingresa el ID de un equipo para ver su perfil:", value=int(comparativa['TEAM_ID_home'].iloc[0]))

perfil = comparativa[comparativa['TEAM_ID_home'] == equipo_id]
if not perfil.empty:
    c1, c2, c3 = st.columns(3)
    c1.metric("Puntos Local", round(perfil['PTS_home'].values[0], 2))
    c2.metric("Puntos Visita", round(perfil['PTS_away'].values[0], 2))
else:
    st.error("ID de equipo no encontrado.")