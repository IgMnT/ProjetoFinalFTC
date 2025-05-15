import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🏠',
)


image_path = './images.png'
image = Image.open( image_path )
st.sidebar.image (image, width=120)
st.sidebar.markdown('# Fome Zero')
st.sidebar.markdown('## Dados para a Fome Zero')
st.sidebar.markdown("""___""")
st.write("# Fome Zero Dashboard")
st.markdown(
    """
    ### 📈 Fome Zero Dashboard
    ### Como usar:
    - Visão Geral - Fornece uma visão generalizada acerca dos indicadores de países, restaurantes, cidades e culinarias
    - Visão Cidade - Forenece uma visão detalhada dos dados das cidades
    - Visão Pais - Fornece uma visão detalhada dos dados dos países
    - Visão Restaurantes - Fornece uma visão detalhada dos dados dos restaurantes
    - Visão Culinaria - Fornece uma visão detalhada dos dados das culinarias
    
    """
)