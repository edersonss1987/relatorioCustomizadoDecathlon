#################################################################################################################################################
#################################################################################################################################################
################################################### IMPORTAÇÃO DOS BIBLIOTECAS  #################################################################
#################################################################################################################################################
#################################################################################################################################################

import requests
import json

import pandas as pd
import re
import numpy as np
import os
import streamlit as st

import time
import datetime

from datetime import timedelta
from dotenv import load_dotenv
from getpass import getpass
from streamlit_autorefresh import st_autorefresh


# Atualiza a cada X segundos (30000 ms) = 30segundos
st_autorefresh(interval=60000, key="auto_refresh")


#################################################################################################################################################
#################################################################################################################################################
############################################## DEFININDO AS FUNÇÕES QUE UTEIS DE APP  ###########################################################
#################################################################################################################################################
#################################################################################################################################################
load_dotenv()


def carregar_css(caminho):
    with open(caminho) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


carregar_css("css/style.css")


def validar_email(email):
    # Regex para validar e-mails
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None


# configurador das colunas pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# verificando email valido


def validar_email(email):
    # Regex para validar e-mails
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# conversor de horas no pandas


def convert_to_time(time_str):
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time() if time_str else None
    except ValueError:
        return None

# Calcula percentual


def calcular_percentual(parte, total):
    if total == 0:
        return 0
    percentual = (parte / total) * 100
    return percentual


# definindo uma função que trate colunas numeriacas para valores monetarios
def formatar_coluna(valores):
    # Convertendo para float
    valores = valores.astype(float)
    # Selecionando o primeiro valor (assumindo que você queira formatar apenas um valor)
    valor_formatado = valores[0]
    # Formatando como string com duas casas decimais e separadores de milhares
    valor_formatado = f'{valor_formatado:_.2f}'
    # Substituindo ponto por vírgula e underscore por ponto
    valor_formatado = valor_formatado.replace('.', ',').replace('_', '.')

    return valor_formatado


def formatar_coluna_int(valores):
    # Convertendo para float
    valores = valores[0].astype(int)
    # Selecionando o primeiro valor
    valor_formatado = valores
    # Formatando como string com zero casas decimais e atribuindo os  em "," separadores de milhares
    valor_formatado = f'{valor_formatado:,.0f}'
    # Substituindo ponto por vírgula e underscore por ponto
    valor_formatado = valor_formatado.replace(',', '.')

    return valor_formatado


# Conversão de DATA E HORA no formato TIMESTAMP /  # definindo a função que convert TIMESTAMP >> DATA E HORA
def convert_data_hora_para_timestamp(data_hora: str):
    # Substitua 'data_string' pela sua data e hora no formato 'AAAA-MM-DD HH:MM:SS'
    data_string = data_hora
    formato = '%Y-%m-%d %H:%M'

    # Convertendo a string de data e hora para um objeto datetime
    data_objeto = datetime.datetime.strptime(data_string, formato)

    #  Convertendo o objeto datetime para timestamp
    timestamp = datetime.datetime.timestamp(data_objeto)
    return timestamp


# definindo a função que convert TIMESTAMP >> DATA E HORA
def convert_timestamp_para_data_hora(timestamp: float):
    # Seu timestamp
    timestamp = float(timestamp)

    # Convertendo o timestamp para data e hora local
    data_hora_local = time.localtime(timestamp)

    # Formatando a data e hora em uma string legível
    data_hora_formatada = time.strftime('%d/%m/%Y %H:%M:%S', data_hora_local)
    return data_hora_formatada

#################################################################################################################################################
#################################################################################################################################################
##################################################### CRIANDO AS BASES DA API  ##################################################################
#################################################################################################################################################
#################################################################################################################################################


# base da tela inicial
base = "https://main.idsecure.com.br:5000"

# base de API Relatórios
base_rel = "https://report.idsecure.com.br:5000/api/v1/accesslog/logs"

# base de login na plataforma
login_api = f'{base}/api/v1/operators/login'


# VARIAVEIS DE LOGIN ESTÃO 'NO MEU AMBIENTE' PARA EVITAR QUE SEJAM COMPARTILHADAS,
EMAIL = os.getenv('email')
PSW = os.getenv('psw')
TOKEN = os.getenv('tokenDeAcesso')


#################################################################################################################################################
#################################################################################################################################################
############################################## INSIRA O E-MAIL AQUI PARA LOGAR NA API  ##########################################################
#################################################################################################################################################
#################################################################################################################################################


# Loop para solicitar ao usuário um e-mail válido
# O loop continuará solicitando um e-mail até que um formato válido seja fornecido, garantindo que o usuário possa prosseguir apenas com um e-mail correto.
user = None
while True:

    user = EMAIL
    if validar_email(EMAIL):
        # print(f"Digite a senha por favor!\n")
        break
    else:
        print("E-mail no formato inválido.\nTente novamente.")
        break


#################################################################################################################################################
#################################################################################################################################################
############################################ INSIRA O SENHA DE ACESSO AO SISTEMA  ###############################################################
#################################################################################################################################################
#################################################################################################################################################


# usando as credenciais para logar na plataforma
login_api_user = {
    "email": f"{EMAIL}",
    "password": f"{PSW}",
    "tenantId": "2785",  # especificando a conta de acesso
}


# requisição de login no end-point
logado = requests.post(login_api, json=login_api_user)


if logado.status_code == 200:
    # imprimindo o conteudo da pagina apos login
    print("Login realizado com sucesso")
else:
    # imprimindo o conteudo da pagina apos login
    print("Erro ao realizar login")
    login_api_user = {
        "email": input(f'Email de acesso:   '),
        "password": getpass(prompt='Senha de acesso:   '),
        "tenantId": "2785",  # especificando a conta de acesso
    }
    logado = requests.post(login_api, json=login_api_user)


#################################################################################################################################################
#################################################################################################################################################
################################################## CONEXÃO COM END-POINT DA API  ################################################################
#################################################################################################################################################
#################################################################################################################################################

# criando o contxto da pagina após login
content_login = json.loads(logado.content)
token = content_login['data']['token']


# os dados abaixo podem ser printados para verificar o login e o acesso a API, mas não são necessários para o funcionamento
email_logado = json.loads(logado.text)


# criando o cabeçalho def
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Authorization": f"Bearer {token}"  # Substitua pelo token real
}


#################################################################################################################################################
#################################################################################################################################################
################################################# MANIPULAÇÃO DE DATAS PARA CONSULTAS  ##########################################################
#################################################################################################################################################
#################################################################################################################################################

##################################################
####### PESSOAS QUE FIZERAM O ACESO HOJE #########
##################################################


inicio_time_filtro = time.time()
hoje = datetime.datetime.now()
data_hora = hoje - timedelta(hours=3)
hojeFotmated = data_hora.strftime('%Y-%m-%d %H:%M')

# mesAnterior = hoje -  datetime.timedelta(days=30)
# mesAnterior = mesAnterior.strftime('%Y-%m-%d 00:00')

primeiraHoraHoje = data_hora
primeiraHoraHoje = primeiraHoraHoje.strftime('%Y-%m-%d 00:01')

# data_hora_inicial = input(f'Incio do relatório (Formato: {primeiraHoraHoje})   ')
data_hora_inicial = primeiraHoraHoje
data_hora_inicial = str(convert_data_hora_para_timestamp(data_hora_inicial))


data_hora_final = data_hora
data_hora_final = data_hora_final.strftime('%Y-%m-%d 23:59')
# data_hora_final = input(f'Data fim do relatório (Formato: {hojeFotmated})   ')
# data_hora_final =hojeFotmated
data_hora_final = str(convert_data_hora_para_timestamp(data_hora_final))

#################################################################################################################################################
#################################################################################################################################################
#################################################### CONSUMINDO DADOS DA API  ###################################################################
#################################################################################################################################################
#################################################################################################################################################


acessos_hoje = requests.get(
    f'{base_rel}?pageSize=500&pageNumber=1&sortOrder=desc&sortField=Time&dtStart={data_hora_inicial}&dtEnd={data_hora_final}&getPhotos=false', headers=headers)


acessos_hoje.json()
# convertendo o resultado da requisição para json
acessos_hoje = acessos_hoje.json()
# acessando a chave "data" do resultado da requisição, que contém os dados de acesso
acessos_hoje = acessos_hoje['data']['data']
# convertendo o resultado para um dataframe do pandas


#################################################################################################################################################
#################################################################################################################################################
################################################# MANIPULAÇÃO DOS DADOS USANDO PANDAS  ##########################################################
#################################################################################################################################################
#################################################################################################################################################


acessos_hoje = pd.DataFrame(acessos_hoje)


# criando um dicionário para corrigir os nomes de dispositivos que possuem espaços a mais
saida_ = {
    'Saida pedestre lado direito': 'Saída pedestre lado direito',
    'Saida pedestre lado esquerdo': 'Saída pedestre lado esquerdo',
}

# removendo os espaços nos resultados de nomes de dispositivos
acessos_hoje['deviceName'] = acessos_hoje['deviceName'].str.strip()
# aplicando o dicionário para corrigir os nomes de dispositivos que possuem espaços a mais
acessos_hoje['deviceName'] = acessos_hoje['deviceName'].replace(saida_)


# primeiro filtro, mantendo pessoas que tiveram acesso permitido
teviram_acesso_hoje = acessos_hoje.loc[acessos_hoje['eventDescription']
                                       == 'AccessGranted']

# definindo uma lista para consulta de pessoas que deram entrada
entradas = [
    'Entrada pedestre lado direito',
    'Entrada pedestre lado esquerdo',
    'Entrada de carros lado interno',
    'Entrada de carros lado externo',
    'Ponto de encontro',
    'Entrada de Caminhão',
    'Entrada fretado'
]

# definindo uma lista para consulta de pessoas que deram saida
saidas = [
    'Saida pedestre lado direito',
    'Saida pedestre lado esquerdo',
    'Saída de carros lado externo',
    'Saída de carros lado interno',
    'Saída Caminhões',
    'Ponto de encontro'
]


# Pegar ÚLTIMO evento de cada pessoa do dia,
# para evitar que pessoas que deram entrada como ultimo registro, sejam contabilizadas.
# por tanto o sistema entenderá que elas estão dentro da empresa,
teviram_acesso_hoje = teviram_acesso_hoje.loc[teviram_acesso_hoje.groupby(
    'personName')['time'].idxmax()]


#################################################################################################################################################
############  INICIO------------------------            FILTROS para o PANDAS/STREAMLIT                                  ########################
#################################################################################################################################################

# removendo os acessos duplicados, para evitar que pessoas que deram entrada e saída mais de uma vez, sejam contabilizadas mais de uma vez.
teviram_acesso_hoje = teviram_acesso_hoje.drop_duplicates(subset=[
                                                          'personName'])


# filtro de pessoas que deram entrada
teve_acesso_de_entrada_hoje = teviram_acesso_hoje[teviram_acesso_hoje['deviceName'].isin(
    entradas)]

# filtro de pessoas que deram saida
teve_acesso_de_saida_hoje = teviram_acesso_hoje[teviram_acesso_hoje['deviceName'].isin(
    saidas)]


# precisamos filtar pessoas que deram entada e não derem saída
pessoas_sem_saida = teve_acesso_de_entrada_hoje[
    ~teve_acesso_de_entrada_hoje['personName'].isin(
        teve_acesso_de_saida_hoje['personName']
    )
]

ponto_de_encontro = teve_acesso_de_saida_hoje.loc[
    teve_acesso_de_saida_hoje['deviceName'] == "Ponto de encontro"]

#################################################################################################################################################
############  FIM------------------------            FILTROS para o PANDAS/STREAMLIT                                  ###########################
#################################################################################################################################################

#################################################################################################################################################
#################################################################################################################################################
################################################ PLOTANDO OS DADOS USANDO O STREAMLIT  ##########################################################
#################################################################################################################################################
#################################################################################################################################################


# _____________________________________________________________________________________________


#################################################################################################################################################
###################################                   KPI'S (CARDS)                   ###########################################################
#################################################################################################################################################


st.set_page_config(layout="wide")

col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
total_sem_saida = len(pessoas_sem_saida)
with col1:
    if total_sem_saida > 0:
        st.markdown(
            f"""
            <div class="card-alerta">
                🚨 Pessoas sem saída<br>
                {total_sem_saida}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.metric("Pessoas sem saída", total_sem_saida)

with col2:
    st.markdown(
        f"""
            <div class="card-green">
                Já saíram <br>
                {len(teve_acesso_de_saida_hoje)}
            </div>
            """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card-blue">
        Entradas/Saídas<br>
        {len(teviram_acesso_hoje)}
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="card-purple">
        Ponto de Encontro<br>
        {len(ponto_de_encontro)}
        <div>
        """,
        unsafe_allow_html=True
    )


st.markdown('<div class="divisor"></div>', unsafe_allow_html=True)
# ______________________________________________________________________________________________

#################################################################################################################################################
###################################                   BODY (DADOS)                     ##########################################################
#################################################################################################################################################
col1, col2, col3 = st.columns([3, 1, 2])

with col1:
    st.subheader("🚨 PESSOAS DENTRO")

    df_dentro = pessoas_sem_saida[['personName',
                                   'deviceName']].reset_index(drop=True)
    df_dentro.index = range(1, len(df_dentro) + 1)

    st.dataframe(
        df_dentro,
        use_container_width=True,
        height=400
    )
with col2:
    st.empty()


with col3:
    st.subheader("✅ SAÍRAM")

    df_saida = teve_acesso_de_saida_hoje[['personName']].reset_index(drop=True)
    df_saida.index = range(1, len(df_saida) + 1)

    st.dataframe(
        df_saida,
        use_container_width=True,
        height=400
    )


#################################################################################################################################################
###################################                   SIDEBAR (FILTROS)                     #####################################################
#################################################################################################################################################
agora = datetime.datetime.now().strftime('%H:%M:%S')
st.sidebar.write(agora)
