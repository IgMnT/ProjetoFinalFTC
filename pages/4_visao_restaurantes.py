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

df = pd.read_csv('dataset/zomato.csv')
df1 = rename_columns(df)


def restaurante_mais_avaliado(df1):
    idx = df1['votes'].idxmax()
    restaurante = df1.loc[idx, 'restaurant_name']
    votos_restaurante = df1.loc[idx, 'votes']
    return restaurante, votos_restaurante

def restaurante_maior_nota(df1):
    idx = df1['aggregate_rating'].idxmax()
    restaurante = df1.loc[idx, 'restaurant_name']
    nota = df1.loc[idx, 'aggregate_rating']
    return restaurante, nota

def restaurante_mais_caro(df1):
    idx = df1['average_cost_for_two'].idxmax()
    restaurante = df1.loc[idx, 'restaurant_name']
    preco = df1.loc[idx, 'average_cost_for_two']
    preco_prefixo = df1.loc[idx,'currency'].split('(')[1].split(')')[0]
    return restaurante, preco, preco_prefixo

def restaurante_menor_nota_brazil(df1):
    idx = (df1[df1['cuisines'] == 'Brazilian']['aggregate_rating'].idxmin())
    restaurante = df1.loc[idx, 'restaurant_name']
    nota = df1.loc[idx, 'aggregate_rating']
    return restaurante, nota

def restaurante_brasileiro_maior_nota_brazil(df1):
    mask = (df1['cuisines'] == 'Brazilian') & (df1['country_code'] == 30)
    idx = df1.loc[mask, 'aggregate_rating'].idxmax()
    restaurante = df1.loc[idx, 'restaurant_name']
    nota = df1.loc[idx, 'aggregate_rating']
    return restaurante, nota

def restaurante_pedido_online_avaliacoes_medias(df1):
    # Calcula a média de avaliações para restaurantes com e sem pedido online
    comparison_dfx = df1.groupby('has_online_delivery')['aggregate_rating'].mean().reset_index()
    comparison_dfx['has_online_delivery'] = comparison_dfx['has_online_delivery'].map({True: 'Com Delivery', False: 'Sem Delivery'})
    comparison_dfx = comparison_dfx.rename(columns={'has_online_delivery': 'Tipo de Entrega', 'aggregate_rating': 'Média de Avaliações'})
    return comparison_dfx

def restaurante_reserva_valor_medio(df1):
    # Calcula a média de preço para duas pessoas para restaurantes com e sem reserva
    comparison_df = df1.groupby('has_table_booking')['average_cost_for_two'].mean().reset_index()
    comparison_df['has_table_booking'] = comparison_df['has_table_booking'].map({True: 'Com Reserva', False: 'Sem Reserva'})
    comparison_df = comparison_df.rename(columns={'has_table_booking': 'Tipo de Reserva', 'average_cost_for_two': 'Preço Médio'})
    return comparison_df

def restaurante_culinaria_japonesa_bbq(df1):
    # Filtra apenas restaurantes dos EUA e com as culinárias de interesse
    df_eua = df1[df1['country_code'] == 216]  # Código dos EUA
    culinarias = ['Japanese', 'BBQ']
    df_culinarias = df_eua[df_eua['cuisines'].isin(culinarias)]
    
    # Calcula a média de preço por tipo de culinária
    media_total = df_culinarias.groupby('cuisines')['average_cost_for_two'].mean().reset_index()
    media_total = media_total.rename(columns={'cuisines': 'Tipo de Culinária', 'average_cost_for_two': 'Preço Médio'})
    return media_total

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

st.header('Visão Restaurantes')

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('#### Restaurante mais avaliado')
        restaurante, votos_restaurante = restaurante_mais_avaliado(df1)
        st.metric(label=restaurante, value=f'{votos_restaurante} votos')
    with col2:
        st.markdown('#### Restaurante com maior nota')
        restaurante, nota = restaurante_maior_nota(df1)
        st.metric(label = restaurante, value=f'{nota} estrelas')
with st.container():
    st.markdown('#### Restaurante mais caro')
    restaurante, preco, preco_prefixo = restaurante_mais_caro(df1)
    st.metric(label = restaurante, value=f'{preco_prefixo}{preco}')

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('#### Restaurante de culinaria brasileira com menor nota')
        restaurante, nota = restaurante_menor_nota_brazil(df1)
        st.metric(label = restaurante, value=f'{nota} estrelas')
    
    with col2:
        st.markdown('#### Restaurante brasileiro de culinaria brasileira com maior nota')
        restaurante, nota = restaurante_brasileiro_maior_nota_brazil(df1)
        st.metric(label = restaurante, value=f'{nota} estrelas')

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('#### Média de avaliações por tipo de entrega')
        comparison_dfx = restaurante_pedido_online_avaliacoes_medias(df1)
        fig1 = px.bar(comparison_dfx, 
                     x='Tipo de Entrega', 
                     y='Média de Avaliações',
                     title='Média de Avaliações por Tipo de Entrega',
                     template='plotly_white')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown('#### Média de preço para duas pessoas por tipo de reserva')
        comparison_df = restaurante_reserva_valor_medio(df1)
        fig2 = px.bar(comparison_df, 
                     x='Tipo de Reserva', 
                     y='Preço Médio',
                     title='Preço Médio por Tipo de Reserva',
                     template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)

with st.container():
    st.markdown('#### Média de preço por tipo de culinária nos EUA')
    media_total = restaurante_culinaria_japonesa_bbq(df1)
    fig3 = px.bar(media_total, 
                  x='Tipo de Culinária', 
                  y='Preço Médio',
                  title='Preço Médio por Tipo de Culinária nos EUA',
                  template='plotly_white')
    st.plotly_chart(fig3, use_container_width=True)
