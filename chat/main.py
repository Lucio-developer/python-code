import streamlit as st
from unidecode import unidecode
from pathlib import Path
import pickle

PASTA_MENSAGENS = Path(__file__).parent /'mensagens'
PASTA_MENSAGENS.mkdir(exist_ok=True)

def main():
    page_chat()

def ler_mensagens_armazenadas(user1, user2):
    nome_arquivo = nome_arquivo_armazenado(user1, user2)
    if (PASTA_MENSAGENS / nome_arquivo).exists():
        with open(PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
            return pickle.load()
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
    return '&'.join(nome_arquivo)

def page_chat():
    st.title('🟢​ Chat...')
    st.divider()

    user1 = 'Lúcio'
    user2 = 'Mori'
    mensagens = ler_mensagens_armazenadas(user1, user2)

    for mensagem in mensagens:
        nome_user = 'user' if mensagem['nome_usuario'] == user1 else mensagens
        avatar = None if mensagem['nome_usuario'] == user1 else '😀'
        chat = st.chat_message(nome_user, avatar = avatar)
        chat.markdown(mensagem['conteudo'])

    nova_mensagem = st.chat_input('Digite uma mensagem')
    if nova_mensagem:
        nova_dict_mensagem = {'nome_user1': user1,
                              'conteudo': nova_mensagem}
        chat = st.chat_menssage('user')
        chat.markdown(nova_dict_mensagem['conteudo'])
        mensagens.append(nova_dict_mensagem)
        armazena_mensagens(user1, user2, mensagens)


if __name__ == '__main__':
    main()