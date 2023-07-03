# =========================================
# Imports
# =========================================
import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from haversine import haversine
import numpy as np

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽', layout= 'wide')

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

def distance( df1, op ):  
    """
    Esta função tem a responsabilidade de calcular a distância média de entregas.
    Input: - df1: dataframe com os dados necessários para cálculo
    Output: - Média da distância
    """
    
    cols = ['Restaurant_latitude', 'Delivery_location_latitude', 'Restaurant_longitude', 'Delivery_location_longitude'] 
    df1['Distance'] = df1.loc[:, cols].apply(lambda x: 
                                             haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                        (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1 )
    if op == 'avg':
        avg_distance = np.round(df1['Distance'].mean(), 2)
        return avg_distance

    elif op == 'fig': 
        fig = go.Figure( data=[ go.Pie( labels= df1['City'], values=df1['Distance'], pull=[0, 0.1, 0])])
        return fig

def festival_avg_std( df1, festival, col ):
    """
    Esta função tem a responsabilidade de calcular a média e o desvio padrão do tempo de entrega, em Festival e Não Festival.
    Input: - df1: dataframe com os dados necessários para cálculo
           - festival: condiciona para entregas que ocorreram:
                       'Yes': entregas que ocorreram durante festival
                       'No': entregas que ocorream fora do festival 
           - col: define a coluna de operação a ser selecionada:
                  'Time_mean' = coluna com o cáculo do tempo médio
                  'Time_std' = coluna com o cáculo do tempo desvio padrão
    Output: df: dataframe com 2 colunas e linhas selecionadas.
    """
    
    df_avg_std_time_festival = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
                                    .groupby(['Festival'])
                                    .agg({'Time_taken(min)':['mean', 'std']}) )
    df_avg_std_time_festival.columns = ['Time_mean', 'Time_std']
    df_avg_std_time_festival = df_avg_std_time_festival.reset_index()
    df_avg_std_time_festival = np.round( df_avg_std_time_festival.loc[df_avg_std_time_festival['Festival'] == festival, col], 2)

    return df_avg_std_time_festival


def bar_time_city( df1 ):  
    df_avg_std_time_per_city = ( df1.loc[:, ['Time_taken(min)', 'City']]
                                    .groupby('City')
                                    .agg({'Time_taken(min)':['mean', 'std']}) )
    df_avg_std_time_per_city.columns = ['Time_mean', 'Time_std']
    df_avg_std_time_per_city = df_avg_std_time_per_city.reset_index()
        
    fig = go.Figure()
    fig.add_trace (go.Bar (name='Control',
                              x= df_avg_std_time_per_city['City'],
                              y= df_avg_std_time_per_city ['Time_std'],
                              error_y=dict(type='data', array=df_avg_std_time_per_city['Time_std'])))
    fig.update_layout(barmode='group')

    return fig

def avg_std_time_city( df1 ):
    df_avg_std_time_per_city_order = ( df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                                          .groupby(['City', 'Type_of_order'])
                                          .agg({'Time_taken(min)':['mean', 'std']}) )
    df_avg_std_time_per_city_order.columns = ['Time_mean', 'Time_std']
    df_avg_std_time_per_city_order = df_avg_std_time_per_city_order.reset_index()
    
    return df_avg_std_time_per_city_order


def avg_std_time_per_city_traf ( df1 ):
    df_avg_std_time_per_city_traf = ( df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                                         .groupby(['City', 'Road_traffic_density'])
                                         .agg({'Time_taken(min)':['mean', 'std']}) )
    df_avg_std_time_per_city_traf.columns = ['Time_mean', 'Time_std']
    df_avg_std_time_per_city_traf = df_avg_std_time_per_city_traf.reset_index()
    
    fig = px.sunburst( df_avg_std_time_per_city_traf, path=['City', 'Road_traffic_density'], values='Time_mean', 
                       color='Time_std', color_continuous_scale='rdbu', 
                       color_continuous_midpoint=np.average(df_avg_std_time_per_city_traf['Time_std']) )

    return fig

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

st.header('Market Place - Visão Restaurante')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '', ''])

with tab1:
    
    with st.container():    
        st.title('Médias')
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        # Total Entregadores Únicos
        with col1: 
            total_deliver = df1['Delivery_person_ID'].nunique()
            col1.metric('Total Entregadores', total_deliver)
        
        # Distância Média
        with col2:
            avg_distance = distance( df1, 'avg' )
            col2.metric('Distância Média', avg_distance)

        # Tempo médio de entrega durante os festivais
        with col3:
            df_avg_std_time_festival = festival_avg_std( df1, 'Yes', 'Time_mean' )
            col3.metric('AVG Entrega Festival', df_avg_std_time_festival)
            
        # Tempo desvio padrão durante os festivais
        with col4:
            df_avg_std_time_festival = festival_avg_std( df1, 'Yes', 'Time_std' )
            col4.metric('STD Entrega Festival', df_avg_std_time_festival)

        # Tempo médio de entrega fora dos festivais
        with col5:
            df_avg_std_time_festival = festival_avg_std( df1, 'No', 'Time_mean' )
            col5.metric('AVG Não Festival', df_avg_std_time_festival)

        # Tempo desvio padrão de entrega fora dos festivais
        with col6:
            df_avg_std_time_festival = festival_avg_std( df1, 'No', 'Time_std' )
            col6.metric('STD Não Festival', df_avg_std_time_festival)
            
    with st.container():
        st.markdown('''___''')
        st.title('Gráficos')
        col1, col2 = st.columns(2)

        with col1: 
            # Distribuição do tempo por cidade
            st.markdown('##### Distribuição do tempo por cidade')
            fig = bar_time_city( df1 ) 
            st.plotly_chart( fig, use_container_width= True )
            
        with col2:
            # Tempo médio por cidade e tipo de pedido
            st.markdown('##### Tempo médio por cidade e tipo de pedido')
            df_avg_std_time_per_city_order = avg_std_time_city( df1 )
            st.dataframe(df_avg_std_time_per_city_order)
                
    with st.container():
        st.markdown('''___''')
        st.title('Distribuição do tempo de Entrega')
        col1, col2 = st.columns(2)

        with col1:
            # Tempo Médio de Entrega por Cidade
            st.markdown('##### Tempo Médio de Entrega por Cidade')
            fig = distance( df1, 'fig' )
            st.plotly_chart( fig, use_container_width=True )

        with col2:
            # Tempo médio e desvio padrão de entrega por cidade e tráfego de trânsito
            st.markdown('##### Tempo médio e desvio padrão de entrega por cidade e tráfego de trânsito')
            fig = avg_std_time_per_city_traf ( df1 )             
            st.plotly_chart( fig, use_container_width= True  )

    with st.container():
        st.markdown('''___''')
