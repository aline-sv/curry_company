import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲'
)

# image_path = 'C:/Users/Aline/Documents/repos/ftc_programacao_python/'
image = Image.open( 'target.jpg' )
st.sidebar.image( image, width=200)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write( ' # Cury Company Growth Dashboard' )

st.markdown(
    '''
    Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
### Como utilizaresse Growth Dashboard?
- Visão Empresa:
	- Visão Gerencial: Métricas gerais de comportamento.
	- Visão Tática: Indicadores semanais de crescimento.
	- Visão Geográfica: Insights de geolocalização.
- Visão Entregador:
	- Acompanhamento dos indicadores semanais de crescimento
- Visão Restaurante:
	-Indicadores semanais de crescimento dos restaurantes
### Ask for Help
- Time de Data Science no Discord
	-@aline.sps
    ''')