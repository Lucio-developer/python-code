import streamlit as st
from unidecode import unidecode
from pathlib import Path
import pickle
import time

#------------------------------PASTAS-------------------------------#
PASTA_MENSAGENS = Path(__file__).parent /'mensagens'
PASTA_MENSAGENS.mkdir(exist_ok=True)

PASTA_USUARIOS = Path(__file__).parent /'usuarios'
PASTA_USUARIOS.mkdir(exist_ok=True)

#------------------------------INICIAL-------------------------------#
def main():
    inicialização()

    if st.session_state['pagina_atual'] == 'login':
        page_login()
    elif st.session_state['pagina_atual'] == 'chat':
        if st.session_state['user2'] == '':
            page_conversas()
        else:
            page_chat()

def inicialização():
    if not 'pagina_atual' in st.session_state:
        mudar_pagina('login')

    if not 'usuario_logado' in st.session_state:
        st.session_state['usuario_logado'] = ''

    if not 'user2' in st.session_state:
        st.session_state['user2'] = ''

#------------------------------ARQUIVOS------------------------------#
def ler_mensagens_armazenadas(user1, user2):
    nome_arquivo = nome_arquivo_armazenado(user1, user2)
    if (PASTA_MENSAGENS / nome_arquivo).exists():
        with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
            return pickle.load(f)
    else:
        return []

def armazena_mensagens(user1, user2, mensagens):
    nome_arquivo = nome_arquivo_armazenado(user1, user2)
    with open(PASTA_MENSAGENS / nome_arquivo, 'wb') as f:
        pickle.dump(mensagens, f)

def nome_arquivo_armazenado(user1, user2):
    nome_arquivo = [user1, user2]
    nome_arquivo.sort()
    nome_arquivo = [i.replace(' ', '_') for i in nome_arquivo]
    nome_arquivo = [unidecode(i) for i in nome_arquivo]
    return '&'.join(nome_arquivo).lower()

def salvar_novo_usuario(nome, senha):
    nome_arquivo = unidecode(nome.replace(' ', '_').lower())
    if (PASTA_USUARIOS / nome_arquivo).exists():
        return False
    else:
        with open(PASTA_USUARIOS / nome_arquivo, 'wb') as f:
            pickle.dump({'nome_usuario' : nome,'senha' : senha}, f)
        return True

def lista_usuarios():
    usuarios = list(PASTA_USUARIOS.glob('*'))
    usuarios = [i.stem.upper() for i in usuarios]
    return usuarios
#----------------------------------LOGIN---------------------------------#
def _login_usuario(nome, senha):
    if validacao_de_senha(nome, senha):
        st.success('Login efetuando com sucesso')
        time.sleep(1)
        st.session_state['usuario_logado'] = nome.upper()
        mudar_pagina('chat')
        st.rerun()
    else:
        st.error('Erro ao logar')

def validacao_de_senha(nome, senha):
    nome_arquivo = unidecode(nome.replace(' ', '_').lower())
    if not (PASTA_USUARIOS / nome_arquivo).exists():
        return False
    else:
        with open(PASTA_USUARIOS / nome_arquivo, 'rb') as f:
            arquivo_senha = pickle.load(f)
        return arquivo_senha['senha'] == senha 

def _casdastrar_usuario(nome, senha):
    if salvar_novo_usuario(nome, senha):
        st.success('Usuario cadastrado com sucesso')
        time.sleep(1)
        st.session_state['usuario_logado'] = nome.upper()
        mudar_pagina('chat')
        st.rerun()
    else:
        st.error('Erro ao cadastrar usuário')
    
#----------------------------------PAGINAS--------------------------------#     
def mudar_pagina(nome_pagina):
    st.session_state['pagina_atual'] = nome_pagina
    
def page_login():
    st.header('🟢​ Sistema de Mensagens Particular', divider=True)
    tab1, tab2 = st.tabs(['Entrar','Cadastrar'])

    with tab1.form(key='login'):
        nome = st.text_input('Digite seu nome de usuario')
        senha = st.text_input('Digite sua senha')
        if st.form_submit_button('Entrar'):
            _login_usuario(nome, senha)

    with tab2.form(key='cadastro'):
        nome = st.text_input('Cadastre um novo nome de usuario')
        senha = st.text_input('Cadastre uma nova senha')
        if st.form_submit_button('Cadastrar'):
            _casdastrar_usuario(nome, senha)

def page_chat():
    st.title('🟢​ Bier Chat...')
    st.divider()

    user1 = st.session_state['usuario_logado']
    user2 = 'Mori'
    mensagens = ler_mensagens_armazenadas(user1, user2)

    for mensagem in mensagens:
        nome_user = 'user' if mensagem['nome_usuario'] == user1 else mensagens
        avatar = None if mensagem['nome_usuario'] == user1 else '😀'
        chat = st.chat_message(nome_user, avatar = avatar)
        chat.markdown(mensagem['conteudo'])

    nova_mensagem = st.chat_input('Digite uma mensagem')
    if nova_mensagem:
        nova_dict_mensagem = {'nome_usuario': user1,
                              'conteudo': nova_mensagem}
        chat = st.chat_message('user')
        chat.markdown(nova_dict_mensagem['conteudo'])
        mensagens.append(nova_dict_mensagem)
        armazena_mensagens(user1, user2, mensagens)

def page_conversas():
    user2 = st.selectbox('Selecione o usuário para conversar',
                         lista_usuarios())
    st.button('Iniciar conversa',
              on_click=_sel_conversa,
              args=(user2, ))

def _sel_conversa(user2):
    st.session_state['user2'] = user2
    st.success(f'Iniciando conversa com {user2}')
    time.sleep(1)
    mudar_pagina('chat')

if __name__ == '__main__':
    main()