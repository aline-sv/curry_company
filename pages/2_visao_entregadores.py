# =========================================
# Imports
# =========================================
import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px
from PIL import Image

st.set_page_config( page_title='Visão Entregadores', page_icon='🛵', layout= 'wide')

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

def rating_by_traffic_weather ( df1, col ):
    """
    Esta função tem a responsabilidade de retornar um dataframe contendo a média e desvio padrão das notas dos entregadores.
    Critérios:
    1. Média e desvio padrão de notas por tráfego
    2. Média e desvio padrão de notas por condições climáticas
    Input: df1 e coluna (por tráfico ou por clima)
    Output: df com os resultados
    """
        
    df_avg_std_per_traffic_weather = ( df1.loc[:, ['Delivery_person_Ratings', col]]
                                  .groupby(col)
                                  .agg({'Delivery_person_Ratings':['mean','std']}) )
    df_avg_std_per_traffic_weather.columns = ['mean', 'std']
    df_avg_std_per_traffic_weather = df_avg_std_per_traffic_weather.reset_index()
    results = st.dataframe(df_avg_std_per_traffic_weather)

    return results

def faster_deliver ( df1, top_asc ):
    """
    Esta função tem a responsabilidade de retornar um dataframe contendo os top 10 entregadores mais rápidos e mais lentos por cidade.
    Critérios:
    1. Identificar se o ascending é True ou False
    Input: - df1: dataframe com os dados a serem calculados 
           - ascending: critério de ordem dos entregadores
                        'True': do maior para o menor
                        'False': do menor para o maior
    Output: - df: dataframe com os resultados calculados
    """   
    
    df_aux = ( df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                  .groupby(['City', 'Delivery_person_ID'])
                  .mean()
                  .sort_values(['City','Time_taken(min)'], ascending=top_asc)
                  .reset_index() )
      
    df_aux1 = df_aux.loc[ df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df_aux.loc[ df_aux['City'] == 'Urban', :].head(10)
    df_aux3 = df_aux.loc[ df_aux['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
    st.dataframe( df3 )
    
    return df3
                
# ========== Início da Estrutura lógica do código ========== 

# Import Dataset
df = pd.read_csv('dataset/train.csv')
    
# Limpando os dados
df1 = clean_code( df )
    
# =========================================
# Barra Lateral no Streamlit
# =========================================

# image_path ='C:/Users/Aline/Documents/repos/ftc_programacao_python/target.jpg'
# image = Image.open( image_path )
image = Image.open( 'target.jpg' )
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')

st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

# Filtro de Data (date_slider)
date_slider = st.sidebar.slider('Até qual valor?', 
                  value = datetime(2022, 4, 13), 
                  min_value = datetime(2022, 2, 11), 
                  max_value = datetime(2022, 4, 6), 
                  format='DD-MM-YYYY')

linhas_selecionadas = df1['Order_Date'] < date_slider 
df1 = df1.loc[linhas_selecionadas, :]

st.sidebar.markdown("""___""")

# Filtro de trânsito
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito:', 
                       ['Low', 'Medium', 'High', 'Jam'], 
                       default=['Low', 'Medium', 'High', 'Jam'])

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options) 
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de clima
weather_options = st.sidebar.multiselect('Quais as condições de clima:',
                                         ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
                                         default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

linhas_selecionadas = df1['Weatherconditions'].isin(weather_options) 
df1 = df1.loc[linhas_selecionadas, :]

st.sidebar.markdown("""___""")

st.sidebar.markdown('Powered by Comunidade DS')

# =========================================
# Contents
# =========================================

st.header('Market Place - Visão Entregadores')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '', ''])

with tab1:
    
    with st.container():    
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        
        # Maior Idade dos Entregadores
        with col1: 
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        
        # Menor Idade dos Entregadores
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)           

        # Melhor Condição de Veículos
        with col3:
            melhor_veic = df1['Vehicle_condition'].max()
            col3.metric('Melhor veículo', melhor_veic)
            
        # Pior Condição de Veículos
        with col4:
            pior_veic = df1['Vehicle_condition'].min()
            col4.metric('Pior veículo', pior_veic)
    
    with st.container():
        st.markdown('''___''')
        st.title('Avaliações')
        
        # Avaliação Média por Entregador
        st.markdown('##### Avaliação Média por Entregador')
        col1, col2 = st.columns(2)
        
        with col1: 
            df_avg_rating_per_deliver = ( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                             .groupby(['Delivery_person_ID'])
                                             .mean()
                                             .reset_index() )
            st.dataframe(df_avg_rating_per_deliver)
            
        with col2:
            st.markdown('##### Avaliação média e o desvio padrão por tipo de tráfego')
            results = rating_by_traffic_weather( df1, 'Road_traffic_density' )
            
            st.markdown('##### Avaliação média e o desvio padrão por condições climáticas')
            results = rating_by_traffic_weather( df1, 'Weatherconditions' )
            
    with st.container():
        st.markdown('''___''')
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)

        with col1:
            
            # Os 10 entregadores mais rápidos por cidade.
            st.markdown('##### Os 10 entregadores mais rápidos por cidade')
            df3 = faster_deliver( df1, top_asc=True )
                    
        with col2:
            
            # Os 10 entregadores mais lentos por cidade.
            st.markdown('##### Os 10 entregadores mais lentos por cidade')
            df3 = faster_deliver( df1, top_asc=False )            