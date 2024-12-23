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

st.set_page_config(page_title="Visão geral", layout="wide")


#Barra superior com logos
col1, col2, col3, col4 = st.columns([3, 2, 1, 3])
with col2:
    st.image("logos\logotipo_combate.png")
with col3:
    st.image("logos\logotipo_Maxsatt.png")


st.title("Visão geral")

# Query para carregar os dados de forma mais rápida
conn = duckdb.connect('my_database.db')
conn.execute("CREATE TABLE IF NOT EXISTS pred_attack AS SELECT * FROM 'prediction\pred_attack_2024.parquet'")
query = """
SELECT * FROM pred_attack
WHERE DATE = ?
"""

query_recent = """
SELECT MAX(DATE) AS most_recent_date
FROM pred_attack
"""

# Executar a query e retornar a data mais recente
most_recent_date_df = conn.execute(query_recent).fetchdf()

# Obter a data como um valor individual
most_recent_date = most_recent_date_df['most_recent_date'][0]

# Validar e converter a data para o formato correto
if pd.notna(most_recent_date):
    most_recent_date = pd.to_datetime(most_recent_date).date()

if 'selectedvariable3' not in st.session_state:
    st.session_state.selectedvariable3 = pd.to_datetime(most_recent_date).strftime('%Y-%m-%d')

st.sidebar.title("Filtros")
selectedvariable3 = st.sidebar.date_input(
    'Selecione a Data',
    value=pd.to_datetime(st.session_state.selectedvariable3),
    min_value=pd.to_datetime('2018-01-01'),
    max_value=pd.to_datetime('2024-12-31')
)

if st.sidebar.button('Confirmar Data'):
    st.session_state.selectedvariable3 = selectedvariable3.strftime('%Y-%m-%d')
    st.success(f"Data selecionada: {st.session_state.selectedvariable3}")

if st.session_state.selectedvariable3:
    pred_attack = conn.execute(query, [st.session_state.selectedvariable3]).fetchdf()
    pred_attack['COMPANY'] = pred_attack['COMPANY'].str.upper()
    pred_attack['FARM'] = pred_attack['FARM'].str.upper()
    pred_attack['STAND'] = pred_attack['STAND'].str.upper()

    stands_all = gpd.read_file("prediction\Talhoes_Manulife_2.shp")
    stands_all = stands_all.to_crs(epsg=4326)
    stands_all['COMPANY'] = stands_all['Companhia'].str.upper()
    stands_all['FARM'] = stands_all['Fazenda'].str.replace(" ", "_")
    stands_all['STAND'] = stands_all.apply(lambda row: f"{row['Fazenda']}_{row['CD_TALHAO']}", axis=1)

    unique_company = pred_attack['COMPANY'].unique()
    unique_farms = pred_attack['FARM'].unique()
    unique_stands_filtered = pred_attack['STAND'].unique()
    unique_stands = {farm: stands_all[stands_all['FARM'] == farm][stands_all['STAND'].isin(unique_stands_filtered)]['STAND'].unique().tolist() for farm in unique_farms}

    selectedvariable4 = st.sidebar.selectbox(
        'Selecione a empresa:', unique_company
        )

    selectedvariable1 = st.sidebar.selectbox(
        'Selecione a Fazenda:',
        unique_farms
        )

    selectedvariable2 = st.sidebar.selectbox(
        'Selecione o Talhão:',
        unique_stands[selectedvariable1]
        )

    # Definir variáveis e tabelas que serão usadas pelos gráficos
    # Definir QT usando query para não sobrecarregar a memória
    quantile_query = """
    SELECT QUANTILE(canopycov, 0.10) AS QT
    FROM pred_attack
    """

    QT = conn.execute(quantile_query).fetchdf().iloc[0]['QT']

    pred_attack_BQ = pred_attack[pred_attack['FARM'] == selectedvariable1]
    pred_attack_BQ_FARM = pred_attack_BQ.groupby(['FARM', 'STAND', 'DATE']).agg(
        {'X': 'mean', 'Y': 'mean', 'canopycov': 'mean', 'cover_min': 'mean'}).reset_index()

    stands_sel = stands_all[stands_all['STAND'] == selectedvariable2]
    stands_sel_farm = stands_all[stands_all['FARM'] == selectedvariable1]

    selectedvariable2 = selectedvariable2.upper()

    list_stands_healthy = pred_attack_BQ_FARM[pred_attack_BQ_FARM['canopycov'] > QT]
    list_stands_attack = pred_attack_BQ_FARM[pred_attack_BQ_FARM['canopycov'] < QT]

    stands_sel_farm_health = stands_sel_farm[stands_sel_farm['STAND'].isin(list_stands_healthy['STAND'])]
    stands_sel_farm_attack = stands_sel_farm[stands_sel_farm['STAND'].isin(list_stands_attack['STAND'])]

    pred_attack_BQ_NEW = pred_attack_BQ[(pred_attack_BQ['STAND'] == selectedvariable2) & 
                                        (pred_attack_BQ['DATE'] == st.session_state.selectedvariable3)]

    pred_stand = pred_attack_BQ[pred_attack_BQ['STAND'] == selectedvariable2].copy()
    pred_stand['DATE'] = pred_stand['DATE'].astype('category')

    pred_attack_BQ_NEW['Status'] = ['Desfolha' if x < QT else 'Saudável' for x in pred_attack_BQ_NEW['canopycov']]
        


    # HEATMAP DO TALHÃO - GRADIENTE
    fig1, ax = plt.subplots(figsize=(6, 3), constrained_layout=True)

    # Plotar polígonos (stands) no mapa
    stands_sel.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.5)

    # Plotar pontos rasterizados para cobertura do dossel
    sc = ax.scatter(pred_attack_BQ_NEW['X'], pred_attack_BQ_NEW['Y'], 
                    c=pred_attack_BQ_NEW['canopycov'], cmap='RdYlGn', 
                    s=1, alpha=1, marker='s', label='Cobertura do Dossel (%)')

    # Adicionar barra de escala e seta norte
    ax.annotate('N', xy=(0.9, 0.1), xytext=(0.9, 0.2), 
                arrowprops=dict(facecolor='black', width=3, headwidth=10),
                ha='center', va='center', fontsize=3, color='black')

    # Estilizar o gráfico e adicionar mapa de fundo
    ctx.add_basemap(ax, crs=stands_sel.crs, source=ctx.providers.Esri.WorldImagery, attribution=False)

    ax.axis('off')

    # Ajustar a cor da legenda
    cbar = plt.colorbar(sc, ax=ax, fraction=0.02, pad=0.02)  # Ajusta o tamanho da barra
    cbar.set_label("Cobertura do dossel (%)", fontsize=8)  # Ajusta o tamanho do rótulo da barra
    cbar.ax.tick_params(labelsize=6)

    #ax.set_title("Cobertura do Dossel", fontsize=5, pad=10)

    # HEATMAP DO TALHÃO - BINÁRIO

    # Criar um mapeamento de cores para o status

    #fig4, ax = plt.subplots(figsize=(6, 3))
    #color_map = {'Saudável': 'green', 'Desfolha': 'red'}
    #pred_attack_BQ_NEW['color'] = pred_attack_BQ_NEW['Status'].map(color_map)

    # Plotar polígonos (stands) no mapa
    #stands_sel.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.5)

    # Plotar pontos com cores binárias para cobertura do dossel
    #ax.scatter(pred_attack_BQ_NEW['X'], pred_attack_BQ_NEW['Y'], 
    #        color=pred_attack_BQ_NEW['color'], s=1, alpha=1, marker='s', label='Cobertura do Dossel')

    # Adicionar barra de escala e seta norte
    #ax.annotate('N', xy=(0.9, 0.1), xytext=(0.9, 0.2), 
    #            arrowprops=dict(facecolor='black', width=3, headwidth=10),
    #            ha='center', va='center', fontsize=3, color='black')

    # Estilizar o gráfico e adicionar mapa de fundo
    #ctx.add_basemap(ax, crs=stands_sel.crs, source=ctx.providers.Esri.WorldImagery, attribution=False)

    #ax.axis('off')

    # Adicionar uma legenda personalizada para os dois tipos de status
    #handles = [
    #    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='green', markersize=4, label='Saudável'),
    #    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=4, label='Desfolha')
    #]
    #ax.legend(handles=handles, fontsize=4, loc='lower left', title="Status", title_fontsize=6)

    # Adicionar título ao gráfico
    #ax.set_title("Status do Dossel", fontsize=5, pad=10)


    #GRÁFICO DE ROSCA ÁREA MONITORADA
    total_area_df = stands_all[stands_all['COMPANY'] == selectedvariable4]

    specific_area_df = total_area_df[total_area_df['FARM'] == selectedvariable1]

    # Calcular a área total e a área específica
    total_area_m2 = total_area_df['geometry'].to_crs("EPSG:32722").area.sum()  # Total em metros quadrados
    specific_area = specific_area_df['geometry'].to_crs("EPSG:32722").area.sum()  # Área específica em metros quadrados

    # Calcular a porcentagem da área específica em relação à área total
    specific_percentage = (specific_area / total_area_m2) * 100
    healthy_percentage = 100 - specific_percentage

    # Convertendo a área total para hectares
    total_area_ha = total_area_m2 / 10000
    specific_area_ha = specific_area / 10000
    healthy_area_ha = total_area_ha - specific_area_ha

    sizes = [healthy_area_ha, specific_area_ha]
    colors = ['lightgray', 'darkgreen']
    labels = ['Demais fazendas', selectedvariable1]

    # Criar o gráfico de rosca usando Plotly
    fig2 = go.Figure()

    fig2.add_trace(go.Pie(
        labels=labels,
        values=sizes,
        hole=0.5,
        marker=dict(colors=colors),
        insidetextorientation='radial',
        textinfo='label+percent',
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Área: %{value:.2f} ha<br>'
            'Porcentagem: %{percent:.1%}<extra></extra>'
        )
    ))

    # Adicionar título e centralizar a área total no meio do gráfico
    fig2.update_layout(
        title={
            'text': f"Área Monitorada {selectedvariable4}",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        annotations=[dict(text=f"{total_area_ha:.2f} ha", x=0.5, y=0.5, font_size=20, showarrow=False)],
        showlegend=False
    )


    # GRÁFICO DE ROSCA ÁREA DE DOSSEL

    pred_attack_BQ_NEW['Status'] = ['Desfolha' if x < QT else 'Saudável' for x in pred_attack_BQ_NEW['canopycov']]

    stands_all['area_ha'] = stands_all['geometry'].area / 10000

    merged_df = pred_attack_BQ_NEW.merge(stands_all[['FARM', 'STAND', 'area_ha']], 
                                        how='left', 
                                        on=['FARM', 'STAND'])

    total_area_ha = merged_df['area_ha'].mean()

    area_status = merged_df.groupby('Status').size().reset_index()
    area_status['area_status_ha'] = area_status[0]/100
    area_status['percentage'] = (area_status['area_status_ha'] / total_area_ha) * 100
    total_area_ha_2 = area_status['area_status_ha'].sum()

    # Configurando as cores
    colors = {'Desfolha': 'red', 'Saudável': 'darkgreen'}

    # Criando o gráfico de rosca com Plotly
    fig3 = go.Figure()

    fig3.add_trace(go.Pie(
        labels=area_status['Status'],
        values=area_status['area_status_ha'],  # Usando a área proporcional calculada
        hole=0.5,  # Para criar o efeito de rosca
        marker=dict(colors=[colors[status] for status in area_status['Status']]),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        texttemplate='%{label}: %{value:.2f} ha<br>(%{percent:.2f}%)'
    ))


    # Adicionando o texto central com a área total
    fig3.update_layout(
        annotations=[
            dict(
                text=f"{total_area_ha_2:.2f} ha",
                x=0.5, y=0.5,
                font_size=20,
                showarrow=False
            )
        ],
        title={
            'text': f"Área de dossel em {selectedvariable2}",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        title_font_size=16,
        showlegend=False
    )



    # GRÁFICO FAZENDAS MAIS INFESTADAS

    stands_all = stands_all.to_crs("EPSG:32722")

    # Filtrar as fazendas apenas da empresa especificada
    stands_all_filtered = stands_all[stands_all['COMPANY'] == selectedvariable4]

    # Juntar a base pred_attack com stands_all filtrado para ter todas as informações em um só dataframe
    merged_df = pred_attack.merge(stands_all_filtered[['FARM', 'STAND', 'geometry']], on=['FARM', 'STAND'], how='left')

    # Converter merged_df em um GeoDataFrame
    merged_df = gpd.GeoDataFrame(merged_df, geometry='geometry', crs="EPSG:32722")

    # Criar a coluna 'Status' baseada nos critérios para definir 'Desfolha' e 'Saudável'
    merged_df['Status'] = ['Desfolha' if x < QT else 'Saudavel' for x in merged_df['canopycov']]

    # Calcular a área de cada polígono em hectares
    merged_df['area_ha'] = merged_df['geometry'].area / 10000  # Convertendo de m² para ha

    unique_area_per_farm = merged_df[merged_df['Status'] == 'Desfolha'].drop_duplicates(subset=['FARM', 'STAND']).groupby('FARM', as_index=False)['area_ha'].sum()

    # Renomeia a coluna para evitar confusão
    unique_area_per_farm.rename(columns={'area_ha': 'farm_desfolha_area_ha'}, inplace=True)

    # Faz o agrupamento original e junta com a área total da fazenda
    grouped = (merged_df.dropna(subset=['Status'])
            .groupby(['DATE', 'Status', 'COMPANY', 'FARM'])
            .agg(count=('Status', 'size'))
            .reset_index()
            .merge(unique_area_per_farm, on='FARM', how='left'))


    grouped = grouped[grouped['Status']=='Desfolha']
    

    fig4 = px.bar(
        grouped,
        x='farm_desfolha_area_ha',
        y='FARM',
        orientation='h',
        labels={'farm_desfolha_area_ha': 'Área de Desfolha (ha)', 'FARM': 'Fazenda'},
        title='Área de Desfolha por Fazenda (ha)',
        color_discrete_sequence=['darkgreen']
    )

    # Personalizar o layout do gráfico
    fig4.update_layout(
        xaxis_title="Área de Desfolha (ha)",
        yaxis_title="Fazenda",
        title_font=dict(size=14, family='Arial', color='black'),
        yaxis=dict(autorange='reversed')  # Inverter a ordem do eixo Y
    )

    # GRÁFICO TALHÕES MAIS INFESTADO POR FAZENDA

    unique_area_per_stand = merged_df[merged_df['Status'] == 'Desfolha'].drop_duplicates(subset=['FARM', 'STAND']).groupby('STAND', as_index=False)['area_ha'].sum()

    # Renomeia a coluna para evitar confusão
    unique_area_per_stand.rename(columns={'area_ha': 'stand_desfolha_area_ha'}, inplace=True)

    # Faz o agrupamento original e junta com a área total da fazenda
    grouped = (merged_df.dropna(subset=['Status'])
            .groupby(['DATE', 'Status', 'COMPANY', 'FARM', 'STAND'])
            .agg(count=('Status', 'size'))
            .reset_index()
            .merge(unique_area_per_stand, on='STAND', how='left'))

    grouped = grouped[grouped['Status']=='Desfolha'].sort_values(by='stand_desfolha_area_ha', ascending=False)

    # Obter apenas os 10 talhões com maior área de desfolha
    top_10_defoliation_stands = grouped.head(10)

    # Criar o gráfico de barras horizontais usando Plotly
    fig5 = px.bar(
        top_10_defoliation_stands,
        x='stand_desfolha_area_ha',
        y='STAND',
        orientation='h',
        labels={'stand_desfolha_area_ha': 'Área de Desfolha (ha)', 'STAND': 'Talhão'},
        title=f'Top 10 Talhões com Maior Área de Desfolha na Fazenda {selectedvariable1}',
        color_discrete_sequence=['darkgreen']
    )

    # Personalizar o layout do gráfico
    fig5.update_layout(
        xaxis_title="Área de Desfolha (ha)",
        yaxis_title="Talhão",
        title_font=dict(size=14, family='Arial', color='black'),
        yaxis=dict(autorange='reversed')  # Inverter a ordem do eixo Y
    )


    col_, col4, col_  = st.columns([5, 6, 5])
    with col4:
        st.pyplot(fig1)

    col6, col7 = st.columns([1,1])
    with col6:
        st.plotly_chart(fig3, use_container_width=True)
    with col7:
        st.plotly_chart(fig2, use_container_width=True)

    col8, col9 = st.columns([1, 1])
    with col8:
        st.plotly_chart(fig4, use_container_width=True)
    with col9:
        st.plotly_chart(fig5, use_container_width=True)