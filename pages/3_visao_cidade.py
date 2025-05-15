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

def rename_columns(df):
    df = df.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

#Inicialização do dataframe
df = pd.read_csv('dataset/zomato.csv')
df1 = rename_columns(df)    

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

def cidade_mais_restaurantes(df1):
    """Esta função retorna a cidade com maior quantidade de restaurantes
    
    Input: Dataframe
    Output: Tupla com nome da cidade e quantidade de restaurantes
    """
    # Agrupa por cidade e conta os restaurantes
    cidade_restaurantes = df1.loc[:, ['city', 'restaurant_id']].groupby('city').count().reset_index()
    
    # Ordena em ordem decrescente e pega a primeira cidade
    cidade_mais_rest = cidade_restaurantes.sort_values('restaurant_id', ascending=False).iloc[0]
    
    return cidade_mais_rest['city'], cidade_mais_rest['restaurant_id']

def cidade_mais_nota_acima_4(df1):
    cidade = df1.loc[df1['aggregate_rating'] > 4, ['city', 'aggregate_rating']].groupby('city').value_counts().idxmax()[0]
    return cidade 

def cidade_mais_nota_abaixo_2_5(df1):
    cidade = df1.loc[df1['aggregate_rating'] < 2.5, ['city', 'aggregate_rating']].groupby('city').value_counts().idxmax()[0]
    return cidade

def cidade_prato_mais_caro(df1):
    cidade = df1.loc[df1['average_cost_for_two'].idxmax(), 'city']
    return cidade

def cidade_mais_culinarias(df1):
    df1['numero_cozinhas'] = df1['cuisines'].str.count(',') + 1
    cidade_cuisines = df1.groupby('city')['numero_cozinhas'].sum().reset_index()
    cidade = cidade_cuisines.loc[cidade_cuisines['numero_cozinhas'].idxmax(), 'city']
    return cidade

def cidade_mais_bool(df1):
    cidade = df1.loc[df1[col] == 1, ['city', col]].groupby('city').value_counts().idxmax()[0]
    return cidade


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

st.header('Visão Cidades')

with st.container():
    st.markdown('### Cidade com mais restaurantes')
    cidade, qtd_restaurantes = cidade_mais_restaurantes(df1)
    st.metric(label=cidade, value=qtd_restaurantes)

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('##### Cidade com mais notas acima de 4')
        cidade = cidade_mais_nota_acima_4(df1)
        st.metric(label='Cidade', value=cidade)
        
    with col2:
        st.markdown('##### Cidade com mais notas abaixo de 2.5')
        cidade = cidade_mais_nota_abaixo_2_5(df1)
        st.metric(label='Cidade', value=cidade)


with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('##### Cidade com o prato para dois mais caro')
        cidade = cidade_prato_mais_caro(df1)
        st.metric(label='Cidade', value=cidade)
        
    with col2:
        st.markdown('##### Cidade com maior numero de culinarias distintas')
        cidade = cidade_mais_culinarias(df1)
        st.metric(label='Cidade', value=cidade)


with st.container():
    col1, col2 , col3= st.columns(3)
    
    with col1:
        st.markdown('##### Cidade com maior numero de restaurantes com reservas')
        col = 'has_table_booking'
        cidade = cidade_mais_bool(df1)
        st.metric(label='Cidade', value=cidade)        
    with col2:
        st.markdown('##### Cidade com maior numero de restaurantes com delivery')
        col = 'is_delivering_now'
        cidade = cidade_mais_bool(df1)
        st.metric(label='Cidade', value=cidade)
    with col3:
        st.markdown('##### Cidade com maior numero de restaurantes com pedidos online')
        col = 'has_online_delivery'
        cidade = cidade_mais_bool(df1)
        st.metric(label='Cidade', value=cidade)
