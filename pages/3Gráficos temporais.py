import dask.dataframe as dd
import geopandas as gpd
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import contextily as ctx
from matplotlib.colors import ListedColormap
from matplotlib_scalebar.scalebar import ScaleBar
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import duckdb

st.set_page_config(page_title="Mapa da fazenda", layout="wide")


#Barra superior com logos
col1, col2, col3, col4 = st.columns([3, 2, 1, 3])
with col2:
    st.image("logos\logotipo_combate.png")
with col3:
    st.image("logos\logotipo_Maxsatt.png")


st.title("Gráficos temporais")

# Query para carregar os dados de forma mais rápida
conn = duckdb.connect('my_database.db')
conn.execute("CREATE TABLE IF NOT EXISTS pred_attack AS SELECT * FROM 'prediction\pred_attack_2024.parquet'")
query = """
SELECT STAND, FARM, DATE, canopycov, COMPANY, canopycovfit, cover_min, cover_max FROM pred_attack
WHERE UPPER(FARM) = ?
"""

query_farm = """
SELECT DISTINCT UPPER(FARM) AS FARM 
FROM pred_attack
"""
unique_farm = conn.execute(query_farm).fetchdf()
unique_farms_list = unique_farm['FARM'].tolist()

if 'selectedvariable1' not in st.session_state:
    st.session_state.selectedvariable1 = None
    st.write("Escolha uma fazenda!")

st.sidebar.title("Filtros")
selectedvariable1 = st.sidebar.selectbox(
    'Selecione a Fazenda',
    unique_farms_list
)

if st.sidebar.button('Confirmar Fazenda'):
    st.session_state.selectedvariable1 = selectedvariable1
    st.success(f"Fazenda selecionada: {st.session_state.selectedvariable1}")

if st.session_state.selectedvariable1:
    pred_attack = conn.execute(query, [st.session_state.selectedvariable1]).fetchdf()
    pred_attack['COMPANY'] = pred_attack['COMPANY'].str.upper()
    pred_attack['FARM'] = pred_attack['FARM'].str.upper()
    pred_attack['STAND'] = pred_attack['STAND'].str.upper()

    stands_all = gpd.read_file("prediction\Talhoes_Manulife_2.shp")
    stands_all = stands_all.to_crs(epsg=4326)
    stands_all['COMPANY'] = stands_all['Companhia'].str.upper()
    stands_all['FARM'] = stands_all['Fazenda'].str.replace(" ", "_")
    stands_all['STAND'] = stands_all.apply(lambda row: f"{row['Fazenda']}_{row['CD_TALHAO']}", axis=1)

    unique_stands_filtered = pred_attack['STAND'].unique()
    unique_stands = {farm: stands_all[stands_all['FARM'] == farm][stands_all['STAND'].isin(unique_stands_filtered)]['STAND'].unique().tolist() for farm in unique_farms_list}

    selectedvariable2 = st.sidebar.selectbox(
        'Selecione o Talhão:',
        unique_stands[selectedvariable1]
        )

    unique_company = pred_attack['COMPANY'].unique()
    unique_farms = pred_attack['FARM'].unique()
    unique_stands_filtered = pred_attack['STAND'].unique()
    unique_stands = {
        farm: stands_all[stands_all['FARM'] == farm][stands_all['STAND'].isin(unique_stands_filtered)]['STAND'].unique().tolist() 
        for farm in unique_farms
    }

    # Definir variáveis e tabelas que serão usadas pelos gráficos
    # Definir QT usando query para não sobrecarregar a memória
    quantile_query = """
    SELECT QUANTILE(canopycov, 0.10) AS QT
    FROM pred_attack
    """

    QT = conn.execute(quantile_query).fetchdf().iloc[0]['QT']

    pred_attack_BQ = pred_attack[pred_attack['FARM'] == selectedvariable1]

    stands_sel = stands_all[stands_all['STAND'] == selectedvariable2]
    stands_sel_farm = stands_all[stands_all['FARM'] == selectedvariable1]

    pred_stand = pred_attack_BQ[pred_attack_BQ['STAND'] == selectedvariable2].copy()
    pred_stand['DATE'] = pred_stand['DATE'].astype('category')
    pred_stand['Status'] = ['Desfolha' if x < QT else 'Saudavel' for x in pred_stand['canopycov']]

    rdown_os = (pred_stand.dropna(subset=['Status'])
             .groupby(['DATE', 'Status'])
             .size()
             .reset_index(name='count'))

    # Calcular a porcentagem de "Desfolha" por data
    total_counts = rdown_os.groupby('DATE')['count'].sum().reset_index(name='total')
    rdown_os = rdown_os.merge(total_counts, on='DATE')
    rdown_os['percentage'] = (rdown_os['count'] / rdown_os['total']) * 100

    # Filtrar apenas os dados de "Desfolha" e ordenar por data
    rdown_os_desfolha = rdown_os[rdown_os['Status'] == 'Desfolha'].sort_values(by='DATE')

    # Calculando médias e desvios padrão
    pred_avg_agg = (pred_stand.groupby('DATE').agg(
        canopycover=('canopycovfit', 'mean'),
        cover_min=('cover_min', 'mean'),
        canopycovSD=('canopycov', 'std')
    ).reset_index())

    # Calculando a raiz quadrada da cobertura do dossel
    pred_avg_agg['canopycovSqrt'] = np.sqrt(pred_avg_agg['canopycover'])

    # Calculando limites de confiança
    pred_avg_agg['canopycoverSDmax'] = pred_avg_agg['canopycover'] + (1.96 * pred_avg_agg['canopycovSD'] / pred_avg_agg['canopycovSqrt'])
    pred_avg_agg['canopycoverSDmin'] = pred_avg_agg['canopycover'] - (1.96 * pred_avg_agg['canopycovSD'] / pred_avg_agg['canopycovSqrt'])

    # Grupo de decisão
    pred_avg_agg['groups'] = np.where(pred_avg_agg['canopycover'] > QT, 'D', 'S')

    # Decisões
    pred_avg_agg['decision'] = np.where(pred_avg_agg['groups'] == 'D', 
                                        np.where(pred_avg_agg['canopycover'].rolling(2).count() >= 2, 'Tomada de decisão', 'Não combate'), 
                                        '')

    # Convertendo a coluna DATE para datetime
    pred_avg_agg['DATE'] = pd.to_datetime(pred_avg_agg['DATE'])



    # GRÁFICO TEMPORAL

    # Criando o gráfico com Plotly
    fig4 = go.Figure()

    # Linha principal de cobertura do dossel
    fig4.add_trace(go.Scatter(
        x=pred_avg_agg['DATE'],
        y=pred_avg_agg['canopycover'],
        mode='lines+markers',
        name='Reflectância (%)',
        line=dict(color='blue'),
        marker=dict(size=6)
    ))

    # Intervalo de confiança
    fig4.add_trace(go.Scatter(
        x=pd.concat([pred_avg_agg['DATE'], pred_avg_agg['DATE'][::-1]]),
        y=pd.concat([pred_avg_agg['canopycoverSDmax'], pred_avg_agg['canopycoverSDmin'][::-1]]),
        fill='toself',
        fillcolor='rgba(173, 216, 230, 0.4)',  # Azul claro com transparência
        line=dict(color='rgba(255,255,255,0)'),
        name='Intervalo de Confiança (95%)',
        hoverinfo='skip'
    ))

    # Personalização do layout
    fig4.update_layout(
        title=f"Talhão {selectedvariable2}, Reflectância no tempo",
        xaxis_title="Data",
        yaxis_title="Cobertura do Dossel (%)",
        xaxis=dict(tickangle=45),
        legend_title="Grupos",
        template="plotly_white",
        hovermode="x unified",
    )


    # GRÁFICO DESFOLHA TEMPORAL

    fig5 = go.Figure()

    # Adicionar a linha de desfolha
    fig5.add_trace(go.Scatter(
        x=rdown_os_desfolha['DATE'],
        y=rdown_os_desfolha['percentage'],
        mode='lines+markers',
        name='Desfolha (%)',
        line=dict(color='red', width=2),
        marker=dict(size=8)
    ))

    # Configuração do layout
    fig5.update_layout(
        title="Desfolha (%) no Tempo",
        xaxis_title="Data",
        yaxis_title="Desfolha (%)",
        xaxis=dict(tickangle=45),
        template="plotly_white",
        hovermode="x unified",
        showlegend=True
    )

    col4, col_ = st.columns([8, 1])
    with col4:
        st.plotly_chart(fig4, use_container_width=True)

    col5, col_ = st.columns([8, 2])
    with col5:
        st.plotly_chart(fig5, use_container_width=True)