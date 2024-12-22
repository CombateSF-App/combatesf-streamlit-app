import streamlit as st
import duckdb
import pandas as pd
import geopandas as gpd

st.set_page_config(page_title="MAXSATT - Plataforma de Monitoramento", layout="wide")

col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
with col2:
    st.image("logos/logotipo_combate.png")
with col3:
    st.image("logos/logotipo_Maxsatt.png")

st.markdown("<h1 style='text-align:center;'font-size:40px;'>Plataforma de Monitoramento de Formigas por Sensoriamento Remoto</h1>", unsafe_allow_html=True)

conn = duckdb.connect('my_database.db')
conn.execute("CREATE TABLE IF NOT EXISTS pred_attack AS SELECT * FROM 'prediction/pred_attack_2024.parquet'")

query = """
SELECT STAND, FARM, DATE, canopycov
FROM pred_attack;
"""

pred_attack = conn.execute(query).fetchdf()
stands_all = gpd.read_file("prediction/Talhoes_Manulife_2.shp")
stands_all = stands_all.to_crs(epsg=4326)
stands_all['COMPANY'] = stands_all['Companhia'].str.upper()
stands_all['FARM'] = stands_all['Fazenda'].str.replace(" ", "_")
stands_all['STAND'] = stands_all.apply(lambda row: f"{row['Fazenda']}_{row['CD_TALHAO']}", axis=1)

quantile_query = """
SELECT QUANTILE(canopycov, 0.10) AS QT
FROM pred_attack
"""

QT = conn.execute(quantile_query).fetchdf().iloc[0]['QT']

# Merge geometries to calculate areas
pred_attack_planilha = pred_attack.copy()
pred_attack_planilha['Status'] = ['Desfolha' if x < QT else 'Saudavel' for x in pred_attack_planilha['canopycov']]

# Convert 'DATE' to datetime
pred_attack_planilha['DATE'] = pd.to_datetime(pred_attack_planilha['DATE'])

stands_all_planilha = stands_all.set_crs("EPSG:4326").to_crs("EPSG:32722")

# Calcular área em hectares
stands_all_planilha['area_ha'] = stands_all_planilha['geometry'].area / 10000

# Merge geometries
merged_df = pred_attack_planilha.merge(stands_all_planilha[['FARM', 'STAND', 'area_ha']], how='left', on=['FARM', 'STAND'])

unique_area_per_stand = merged_df.drop_duplicates(subset=['FARM', 'STAND'])

st.write(unique_area_per_stand)

        # Renomeia a coluna para evitar confusão
unique_area_per_stand.rename(columns={'area_ha': 'stand_total_area_ha'}, inplace=True)

        # Faz o agrupamento original e junta com a área total da fazenda
grouped_stand = (merged_df.dropna(subset=['Status'])
                .groupby(['DATE', 'Status', 'FARM'])
                .agg(count=('Status', 'size'))
                .reset_index()
                .merge(unique_area_per_stand['STAND', 'stand_total_area_ha'], on='STAND', how='left'))


grouped_stand['desfolha_area_ha'] = grouped_stand['count']/100

        # Add percentages
grouped_stand['total'] = grouped_stand.groupby(['DATE', 'FARM', 'STAND'])['count'].transform('sum')
grouped_stand['percentage'] = (grouped_stand['count'] / grouped_stand['total']) * 100


grouped_stand = grouped_stand[grouped_stand['Status'] == 'Desfolha'].sort_values(by='DATE')




# Agrupar por data e status, e contar as ocorrências
rdown_os_farm = (pred_attack_planilha.dropna(subset=['Status'])
             .groupby(['DATE', 'Status', 'FARM'])
             .size()
             .reset_index(name='count'))

# Calcular a porcentagem de "Desfolha" por data
rdown_os_farm['total'] = rdown_os_farm.groupby(['DATE', 'FARM'])['count'].transform('sum')
rdown_os_farm['percentage'] = (rdown_os_farm['count'] / rdown_os_farm['total']) * 100

# Filtrar apenas os dados de "Desfolha" e ordenar por data
rdown_os_desfolha_farm = rdown_os_farm[rdown_os_farm['Status'] == 'Desfolha'].sort_values(by='DATE')



csv_stand = grouped_stand.to_csv(index=False).encode('utf-8')
csv_farm = rdown_os_desfolha_farm.to_csv(index=False).encode('utf-8')

st.write("**Baixar planilhas:**")


col1, col2 = st.columns([1,1])
with col1:
    st.download_button(
        label="Porcentagem desfolha por talhão",
        data=csv_stand,
        file_name='desfolha_talhao.csv',
        mime='text/csv'
    )
with col2:
    st.download_button(
        label="Porcentagem desfolha por fazenda",
        data=csv_farm,
        file_name='desfolha_fazenda.csv',
        mime='text/csv'
    )

