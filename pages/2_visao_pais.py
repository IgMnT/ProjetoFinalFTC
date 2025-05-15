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
import inflection




#=======================================
#Funções
#=======================================

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

df1['price_range'] = df1['price_range'].astype(int)
df1['country_code'] = df1['country_code'].astype(int)
df1['votes'] = df1['votes'].astype(int)
df1.loc[df1['has_table_booking'] == 1, 'has_table_booking'] = True
df1.loc[df1['has_table_booking'] == 0, 'has_table_booking'] = False



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
def country_name(country_id):
    return COUNTRIES[country_id]




def pais_top(df1,col):
    if col == 'city':
        # Conta o número de cidades únicas por país
        cidades_por_pais = df1.groupby('country_code')['city'].nunique()
        pais_code = cidades_por_pais.idxmax()
        valor = cidades_por_pais.max()
        pais = country_name(pais_code)
    else:
        linha = df1.loc[df1[col].idxmax()]
        pais_code = linha['country_code']
        pais = country_name(pais_code)
        valor = linha[col]
    return pais, valor

def nivel_preco(df1):
    code = df1.loc[df1['price_range'] == 4, 'country_code'].value_counts()
    pais = country_name(code.idxmax())
    quantidade = code.max()
    return pais, quantidade

def cuisines(df1):
    culinarias_distintas = df1.groupby('country_code')['cuisines'].nunique()
    pais_mais_diverso = culinarias_distintas.idxmax()
    quantidade = culinarias_distintas.max()
    pais = country_name(pais_mais_diverso)
    return pais, quantidade

def entregas_reservas(df1,col):
    code = df1.loc[df1[col] == True, 'country_code'].value_counts()
    pais = country_name(code.idxmax())
    quantidade = code.max()
    return pais, quantidade
  
def media_avaliacoes(df1, col, func):
    media = df1.groupby('country_code')[col].mean()
    country_id = media.idxmax() if func == pd.Series.idxmax else media.idxmin()
    valor = round(media[country_id], 2)
    return country_name(country_id), valor

def prato_pais(df1):
    preco_medio = df1.groupby('country_code')['average_cost_for_two'].mean()
    visao = preco_medio.reset_index(name='Preco médio')
    visao['country_code'] = visao['country_code'].apply(country_name)
    visao = visao.rename(columns={'country_code': 'País'})
    # Ordena o dataframe pelo preço médio em ordem decrescente
    visao = visao.sort_values('Preco médio', ascending=False)
    return visao





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

st.header('Visão País')

with st.container():
    col1,col2 = st.columns(2)
    
    with col1:
        st.markdown('### País com maior quantidade de cidades registradas')
        col = 'city'
        pais, valor = pais_top(df1,col)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=valor)
    with col2:
        st.markdown('### País com maior quantidade de restaurantes cadastrados')
        col = 'restaurant_id'
        pais, valor = pais_top(df1,col)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=valor)

with st.container():
    st.markdown('### país que possui mais restaurantes com o nível de preço igual a 4 registrados')
    pais, quantidade = nivel_preco(df1)
    st.metric(label='País', value=pais)
    st.metric(label='Quantidade', value=quantidade)

with st.container():
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('### País com maior quantidade de culinarias distintas')
        pais, quantidade = cuisines(df1)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=quantidade)
    with col2:
        st.markdown('### País com maior quantidade de avaliações registradas')
        col = 'votes'
        pais, valor = pais_top(df1,col)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=valor)

with st.container():
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('### País com maior quantidade de restaurantes com entregas')
        col = 'has_online_delivery'
        pais, quantidade = entregas_reservas(df1,col)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=quantidade)
    with col2:
        st.markdown('### País com maior quantidade de restaurantes com reservas')
        col = 'has_table_booking'
        pais, quantidade = entregas_reservas(df1,col)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=quantidade)
with st.container():
    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown('### País com maior quantidade média de avaliações:')
        col = 'votes'
        pais, valor = media_avaliacoes(df1,col,pd.Series.idxmax)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=valor)
    with col2:
        st.markdown('### País com maior média de nota:')
        col = 'aggregate_rating'
        pais, valor = media_avaliacoes(df1,col,pd.Series.idxmax)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=valor)
    with col3:
        st.markdown('### País com menor média de nota:')   
        col = 'aggregate_rating'
        pais, valor = media_avaliacoes(df1,col,pd.Series.idxmin)
        st.metric(label='País', value=pais)
        st.metric(label='Quantidade', value=valor)
with st.container():
    st.markdown('### Média de preço de prato para dois p/ país:')
    visao = prato_pais(df1)
    fig = px.bar(visao, 
                 x='País', 
                 y='Preco médio',
                 title='Preço Médio do Prato para Dois por País',
                 labels={'País': 'País', 'Preco médio': 'Preço Médio'},
                 template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)
