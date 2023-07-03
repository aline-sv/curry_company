# Imports / Bibliotecas
import pandas as pd
from datetime import datetime
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static 

# Imports / Libraries
import plotly.express as px
import plotly.graph_objects as go
import folium
from haversine import haversine

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout= 'wide')

# =========================================
# Funções
# =========================================

def clean_code( df1 ):
    """
    Esta função tem a responsabilidade de limpar o dataframe
    Tipos de limpeza:
    1. Remoção dos dados NaN
    2. Limpeza da coluna de tempo (Time_taken(min)) - retirada do (min)
    3. Conversão de tipos das colunas de dados
    4. Conversão da coluna de datas
    5. Remoção de espaço das variáveis de texto 
    Input: df1
    Output: df1 limpo
    """
    
    # 1. Retirando as linhas NaN
    linhas_sem_nan = df1.loc[:, 'multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_sem_nan, :].copy()
    
    linhas_sem_nan = df1.loc[:, 'Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_sem_nan, :].copy()
    
    linhas_sem_nan = df1.loc[:, 'City'] != 'NaN '
    df1 = df1.loc[linhas_sem_nan, :]
    
    linhas_sem_nan = df1.loc[:, 'Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_sem_nan, :]
    
    linhas_sem_nan = df1.loc[:, 'Festival'] != 'NaN '
    df1 = df1.loc[linhas_sem_nan, :]
    
    # 2. Limpeza coluna Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split ('(min) ')[1])
    
    # 3. Converter type
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # 4. Converter data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    # 5. Retirando espaços
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    return df1

def order_metric( df1 ):
    """Esta função tem a responsabilidade de criar gráfico de barras
    # Critérios do gráfico:
    # 1. Selecionar as colunas ID e Data do Pedido
    # Input: df1
    # Output: Figura do gráfico
    """
    
    col = ['ID', 'Order_Date']

    # Agrupamento das linhas (Seleção das linhas)
    df_aux = ( df1.loc[:, col].groupby(['Order_Date'])
                              .count()
                              .reset_index() )

    # Desenhar o gráfico de barras
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig

def traffic_order_share ( df1 ): 
    """
    Esta função tem a responsabilidade de criar gráfico de pizza
    Critérios do gráfico:
    1. Selecionar as colunas ID e Densidade do Tráfico
    Input: df1
    Output: Figura do gráfico
    """
    
    # Agrupamento das linhas e colunas
    df_aux = ( df1.loc[:, ['ID', 'Road_traffic_density']]
                  .groupby('Road_traffic_density')
                  .count()
                  .reset_index() )
    
    # Transformando em %
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    
    # Desenhar o gráfico de pizza
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

def traffic_order_city( df1 ): 
    """
    Esta função tem a responsabilidade de criar gráfico de pizza
    Critérios do gráfico:
    1. Selecionar as colunas ID e Densidade do Tráfico e Cidade
    Input: df1
    Output: Figura do gráfico
    """
    
    #Agrupamento de linhas e colunas
    df_aux = ( df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                  .groupby(['City', 'Road_traffic_density'])
                  .count()
                  .reset_index() )
    
    # Desenhar o gráfico de bolhas
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def order_by_week( df1 ):
    """
    Esta função tem a responsabilidade de criar gráfico de linha
    Critérios do gráfico:
    1. Criar nova coluna contando a semana do ano
    2. Selecionar as colunas ID e Semana do ano
    Input: df1
    Output: Figura do gráfico
    """
    
    # Criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    
    # Agrupar linhas
    df_aux = ( df1.loc[:, ['ID', 'week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index() )
    
    # Desenhar o gráfico de linhas 
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

def order_share_by_week( df1 ): 
    """
    Esta função tem a responsabilidade de criar gráfico de linha
    Critérios do gráfico:
    1. df1 seleciona columnas ID e semana do ano, df2 seleciona colunas ID_entregador e semana do ano
    2. Merge os dois dfs
    Input: df1
    Output: Figura do gráfico
    """
    
    # Agrupamento por linhas e colunas - ID por Semana
    df_aux1 = ( df1.loc[:, ['ID', 'week_of_year']]
                   .groupby('week_of_year')
                   .count()
                   .reset_index() )
    
    # Agrupamento por linhas e colunas - Entregador por Semana
    df_aux2 = ( df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                   .groupby('week_of_year')
                   .nunique()
                   .reset_index() )
    
    # Juntar 2 df
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    
    # Crio outra coluna com quantas entregas ('ID') tenho por entregador ('Delivery_person_ID')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID'] 
    
    # Desenhar gráfico de linhas
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')

    return fig

def country_maps( df1 ):
    """
    Esta função tem a responsabilidade de criar o mapa
    Critérios do gráfico:
    1. Selecionr colunas relevantes
    2. Roda um for colocando um marker referente a latitude e longitude de cada linha
    Input: df1
    Output: Mapa
    """
    
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = ( df1.loc[:, cols]
                  .groupby(['City', 'Road_traffic_density'])
                  .median()
                  .reset_index() )
    
    # Cria o mapa mundial
    map = folium.Map()
    
    # Coloca os pontos de latitude/longitude no mapa
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)
    
    #Exibe o mapa 
    folium_static(map, width=1024, height=600)
        
    return None
    
# ========== Início da Estrutura lógica do código ========== 

# Import Dataset
df = pd.read_csv('dataset/train.csv')
    
# Limpando os dados
df1 = clean_code( df )
    
# =========================================
# Barra Lateral no Streamlit
# =========================================
st.header('Market Place - Visão Cliente')

# image_path ='C:/Users/Aline/Documents/repos/ftc_programacao_python/target.jpg'
# image = Image.open( image_path )
image = Image.open( 'target.jpg' )
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?', 
                  value = datetime(2022, 4, 13), 
                  min_value = datetime(2022, 2, 11), 
                  max_value = datetime(2022, 4, 6), 
                  format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito', 
                       ['Low', 'Medium', 'High', 'Jam'], 
                       default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""___""")

st.sidebar.markdown('Powered by Comunidade DS')

# Filtro de Data (date_slider)
linhas_selecionadas = df1['Order_Date'] < date_slider 
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options) 
df1 = df1.loc[linhas_selecionadas, :]

# =========================================
# Layout no Streamlit
# =========================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric            
        st.markdown('# Orders by Day')
        fig = order_metric( df1 )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('# Orders by traffic density')
            fig = traffic_order_share( df1 )
            st.plotly_chart(fig, use_container_width=True)
                
        with col2:
            st.markdown('# Orders by city and traffic density')
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig, use_container_width=True)
            
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week( df1 )
        st.plotly_chart(fig, user_container_width=True)
            
    with st.container():
        st.markdown('# Order Sharter by Week')
        fig = order_share_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    st.markdown('# Country Maps by traffic density')
    map = country_maps( df1 )