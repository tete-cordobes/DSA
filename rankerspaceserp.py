import streamlit as st
import requests
import pandas as pd
from key import SpaceSerp
import trafilatura
import re
from lxml import etree

# Configura tu clave de API de SpaceSerp (reemplaza con tu clave de API real)
api_key = SpaceSerp
# Título de la aplicación en Streamlit
st.title('Buscador de Servicios en SpaceSerp')
def extract_content(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        xml_complete = trafilatura.extract(xml_content, xml_input=True)
        root = etree.fromstring(xml_complete)
        print(xml_complete)
        
        h1_text = re.findall(r'<.*"h1">(.*?)</head>', xml_complete)
        h2_text = re.findall(r'<.*"h2">(.*?)</head>', xml_complete)
        h3_text = re.findall(r'<.*"h3">(.*?)</head>', xml_complete)
        p_text = re.findall(r'<.*"p">(.*?)</p>', xml_complete)



        return h1_text, h2_text, h3_text, p_text
    else:
        return None, None, None, None
def merge_extracted_content(df_results_all):
    # Asegurarse de que 'url' es el nombre de la columna en tu DataFrame que contiene las URLs
    url_column = 'link'

    # Crear un DataFrame vacío para almacenar los resultados de extract_content
    df_extracted_content = pd.DataFrame()

    # Iterar sobre cada fila en df_results_all
    for index, row in df_results_all.iterrows():
        # Obtener la URL de la fila actual
        url = row[url_column]

        # Llamar a extract_content con la URL actual
        h1_text, h2_text, h3_text, p_text = extract_content(url)

        # Crear un diccionario con los resultados
        extracted_data = {
            url_column: url,
            'h1_text': h1_text,
            'h2_text': h2_text,
            'h3_text': h3_text,
            'p_text': p_text,
        }

        # Convertir el diccionario a DataFrame y agregarlo a df_extracted_content
        df_extracted_content = df_extracted_content.append(extracted_data, ignore_index=True)

    # Hacer un merge de df_results_all con df_extracted_content usando la columna de URL
    df_combined = pd.merge(df_results_all, df_extracted_content, on=url_column)

    return df_combined

with st.sidebar:
    # Sidebar para entrada de dominio y location
    location_usuario = st.text_input('Introduce la location:', 'Barcelona, Catalonia, Spain')

    # Campo para que el usuario ingrese la consulta
    queries = st.text_area('Introduce las consultas (una por línea):', 'cerrajeros en Barcelona\nfontaneros en Madrid').splitlines()

# Botón para realizar la búsqueda
if st.button('Buscar'):
    # DataFrame para almacenar los resultados de todas las keywords
    df_results_all = pd.DataFrame()

    total_queries = len(queries)
    progress_bar = st.progress(0)

    for i, query in enumerate(queries):
        # Parámetros de búsqueda
        params = {
            'apiKey': api_key,
            'q': query,
            'location': location_usuario,
            'gl': 'es',  # País: España
            'hl': 'es',  # Idioma: Español
        }

        # Realiza la solicitud a la API de SpaceSerp
        response = requests.get('https://api.spaceserp.com/google/search', params=params)

        # Verifica si la solicitud fue exitosa
        if response.status_code == 200:
            # Procesa la respuesta
            search_results = response.json()

            # Convierte los resultados en un DataFrame
            df_results = pd.DataFrame(search_results['organic_results'])

            # Agrega una columna con la keyword correspondiente
            df_results['Keyword'] = query

            # Agrega los resultados al DataFrame general
            df_results_all = pd.concat([df_results_all, df_results], ignore_index=True)

        # Actualiza la barra de progreso con el progreso actual
        progress_text = st.empty()

        progress = (i + 1) / total_queries
        progress_bar.progress(progress)
        progress_text.text(f'Progress: {progress * 100:.2f}%')
        st.text(f'Processing: {query}')

    # Muestra el DataFrame completo con resultados de todas las keywords
    st.write(df_results_all)
    df_total = merge_extracted_content(df_results_all)
    st.write(df_total)
