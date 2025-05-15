#=======================================
#Bibliotecas
#=======================================

from haversine import haversine 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import datetime 
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static
import inflection

#=======================================
#Funções
#=======================================
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def rename_columns(df):
    df = df.copy()
    
    # Renomeando colunas
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    
    df['restaurant_id'] = df['restaurant_id'].fillna(0).astype(int)
    df['country_code'] = df['country_code'].fillna(0).astype(int)
    
     
    text_columns = ['restaurant_name', 'city', 'address', 'locality', 
                   'locality_verbose', 'currency', 'rating_color', 'rating_text']
    for col in text_columns:
        df[col] = df[col].fillna('').astype(str)
    
    df['longitude'] = df['longitude'].fillna(0.0).astype(float)
    df['latitude'] = df['latitude'].fillna(0.0).astype(float)
    
    df['cuisines'] = df['cuisines'].fillna('').astype(str)
    df['cuisines'] = df['cuisines'].apply(lambda x: x.split(',')[0] if x != '' else x)
    
    df['average_cost_for_two'] = df['average_cost_for_two'].fillna(0).astype(float)
    df['aggregate_rating'] = df['aggregate_rating'].fillna(0.0).astype(float)
    
    bool_columns = ['has_table_booking', 'has_online_delivery', 
                   'is_delivering_now', 'price_range', 'votes']
    for col in bool_columns:
        df[col] = df[col].fillna(0).astype(int)
    
    return df

def culinaria_rank(df1, col, max_min):
    id = df1[df1['cuisines'] == col]['aggregate_rating']
    indice = id.idxmax() if max_min == 'max' else id.idxmin()
    rest = df1.loc[indice, 'restaurant_name']
    nota = df1.loc[indice, 'aggregate_rating']
    return rest, nota

def culinaria_rank2(df1, col):
    df_grouped = df1.groupby('cuisines')[col].mean().reset_index()
    indice = df_grouped[col].idxmax()
    culinaria = df_grouped.loc[indice, 'cuisines']
    valor = df_grouped.loc[indice, col]
    return culinaria, valor

def culinaria_rank3(df1):
    mask = (df1['has_online_delivery'] == 1) & (df1['is_delivering_now'] == 1)
    df_filtered = df1[mask]
    df_grouped = df_filtered.groupby('cuisines').size().reset_index(name='count')
    indice = df_grouped['count'].idxmax()
    culinaria = df_grouped.loc[indice, 'cuisines']
    numero_restaurantes = df_grouped.loc[indice, 'count']
    return culinaria, numero_restaurantes


df = pd.read_csv('dataset/zomato.csv')
df1 = rename_columns(df)


#=======================================
#Barra Lateral
#=======================================

image_path = './images.png'
image = Image.open(image_path)

st.sidebar.image(image, width=120)

st.sidebar.markdown('# Fome Zero')
st.sidebar.markdown('## Filtros')

country = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar os restaurantes:',
    list(COUNTRIES.values()),
    default=list(COUNTRIES.values())
)

country_code_map = {v: k for k, v in COUNTRIES.items()}

linhas_selecionadas = df1['country_code'].isin([country_code_map[pais] for pais in country])
df1 = df1.loc[linhas_selecionadas, :]

#=======================================
#Layout
#=======================================

st.header('Visão Culinária')

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Restaurante de culinária italiana com maior nota')
        restaurante, nota = culinaria_rank(df1, 'Italian', 'max')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')
    with col2:
        st.markdown('#### Restaurante de culinária italiana com menor nota')
        restaurante, nota = culinaria_rank(df1, 'Italian', 'min')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Restaurante de culinária americana com maior nota')
        restaurante, nota = culinaria_rank(df1, 'American', 'max')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')
    with col2:
        st.markdown('#### Restaurante de culinária americana com menor nota')
        restaurante, nota = culinaria_rank(df1, 'American', 'min')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Restaurante de culinária árabe com maior nota')
        restaurante, nota = culinaria_rank(df1, 'Arabian', 'max')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')
    with col2:
        st.markdown('#### Restaurante de culinária árabe com menor nota')
        restaurante, nota = culinaria_rank(df1, 'Arabian', 'min')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Restaurante de culinária japonesa com maior nota')
        restaurante, nota = culinaria_rank(df1, 'Japanese', 'max')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')
    with col2:
        st.markdown('#### Restaurante de culinária japonesa com menor nota')
        restaurante, nota = culinaria_rank(df1, 'Japanese', 'min')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Restaurante de culinária caseira com maior nota')
        restaurante, nota = culinaria_rank(df1, 'Home-made', 'max')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')
    with col2:
        st.markdown('#### Restaurante de culinária caseira com menor nota')
        restaurante, nota = culinaria_rank(df1, 'Home-made', 'min')
        st.metric(label=restaurante, value=f'{nota:.1f} estrelas')

with st.container():
    st.markdown('#### Tipo de culinária mais cara:')
    col = 'average_cost_for_two'
    culinaria, valor = culinaria_rank2(df1, col)
    st.metric(label=culinaria, value=f'{valor:.2f}')

with st.container():
    st.markdown('#### Tipo de culinária mais bem avaliada:')
    col = 'aggregate_rating'
    culinaria, valor = culinaria_rank2(df1, col)
    st.metric(label=culinaria, value=f'{valor:.2f}')

with st.container():
    st.markdown('#### Tipo de culinária que possui mais restaurantes que aceitam pedidos online e fazem entregas:')
    culinaria, numero_restaurantes = culinaria_rank3(df1)
    st.metric(label=culinaria, value=f'{numero_restaurantes} restaurantes')
