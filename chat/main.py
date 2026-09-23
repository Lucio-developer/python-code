import streamlit as st
from unidecode import unidecode
from pathlib import Path
import pickle
import time

#------------------------------FOLDERS-------------------------------#
MESSAGES_FOLDER = Path(__file__).parent / 'mensagens'
MESSAGES_FOLDER.mkdir(exist_ok=True)

USERS_FOLDER = Path(__file__).parent / 'usuarios'
USERS_FOLDER.mkdir(exist_ok=True)

#----------------------------VARIABLES-------------------------------#
RERUN_INTERVAL = 3

#------------------------------INITIAL-------------------------------#

def main():
    initialize_session()

    if st.session_state['current_page'] == 'login':
        page_login()
    elif st.session_state['current_page'] == 'chat':
        if st.session_state['recipient_user'] == '':
            container = st.container()
            page_conversations(container)
        else:
            page_chat()
            container = st.sidebar.container()
            page_conversations(container)
            time.sleep(RERUN_INTERVAL)
            st.rerun()

def initialize_session():
    if 'current_page' not in st.session_state:
        change_page('login')

    if 'logged_user' not in st.session_state:
        st.session_state['logged_user'] = ''

    if 'recipient_user' not in st.session_state:
        st.session_state['recipient_user'] = ''

    if 'last_sent_message' not in st.session_state:
        st.session_state['last_sent_message'] = ''

#------------------------------FILES------------------------------#
def load_stored_messages(user1, user2):
    file_name = get_storage_file_name(user1, user2)
    if (MESSAGES_FOLDER / file_name).exists():
        with open(MESSAGES_FOLDER / file_name, 'rb') as f:
            return pickle.load(f)
    else:
        return []

def save_messages(user1, user2, messages):
    file_name = get_storage_file_name(user1, user2)
    with open(MESSAGES_FOLDER / file_name, 'wb') as f:
        pickle.dump(messages, f)

def get_storage_file_name(user1, user2):
    file_name = [user1, user2]
    file_name.sort()
    file_name = [i.replace(' ', '_') for i in file_name]
    file_name = [unidecode(i) for i in file_name]
    return '&'.join(file_name).lower()

def save_new_user(username, password):
    file_name = unidecode(username.replace(' ', '_').lower())
    if (USERS_FOLDER / file_name).exists():
        return False
    else:
        with open(USERS_FOLDER / file_name, 'wb') as f:
            pickle.dump({'username': username, 'password': password}, f)
        return True

def get_user_list():
    users = list(USERS_FOLDER.glob('*'))
    users = [i.stem.upper() for i in users]
    return users

#----------------------------------LOGIN---------------------------------#
def login_user(username, password):
    if validate_password(username, password):
        st.success('Login efetuando com sucesso')
        time.sleep(1)
        st.session_state['logged_user'] = username.upper()
        change_page('chat')
        st.rerun()
    else:
        st.error('Erro ao logar')
        st.rerun()

def validate_password(username, password):
    file_name = unidecode(username.replace(' ', '_').lower())
    if not (USERS_FOLDER / file_name).exists():
        return False
    else:
        with open(USERS_FOLDER / file_name, 'rb') as f:
            user_data = pickle.load(f)
        return user_data['password'] == password 

def register_user(username, password):
    if save_new_user(username, password):
        st.success('Usuario cadastrado com sucesso')
        time.sleep(1)
        st.session_state['logged_user'] = username.upper()
        change_page('chat')
        st.rerun()
    else:
        st.error('Erro ao cadastrar usuário')
    
#----------------------------------PAGES--------------------------------#     
def change_page(page_name):
    st.session_state['current_page'] = page_name
    
def page_login():
    st.header('🟢​ Sistema de Mensagens Particular', divider=True)
    tab1, tab2 = st.tabs(['Entrar', 'Cadastrar'])

    with tab1.form(key='login'):
        username = st.text_input('Digite seu nome de usuario')
        password = st.text_input('Digite sua senha', type='password')
        if st.form_submit_button('Entrar'):
            login_user(username, password)

    with tab2.form(key='cadastro'):
        username = st.text_input('Cadastre um novo nome de usuario')
        password = st.text_input('Cadastre uma nova senha', type='password')
        if st.form_submit_button('Cadastrar'):
            if password == "":
                st.error("Senha Invalida!")
            else:
                register_user(username, password)

def page_chat():
    st.title(f'🟢​ My Chat, {st.session_state["logged_user"]}')
    st.divider()

    user1 = st.session_state['logged_user']
    user2 = st.session_state['recipient_user']
    messages = load_stored_messages(user1, user2)

    container = st.container()
    for msg in messages:
        sender_name = 'user' if msg['username'] == user1 else msg['username']
        avatar = None if msg['username'] == user1 else '⚪'
        chat = container.chat_message(sender_name, avatar=avatar)
        chat.markdown(msg['content'])

    new_message = st.chat_input('Digite uma mensagem')
    if new_message:
        if new_message != st.session_state['last_sent_message']:
            st.session_state['last_sent_message'] = new_message

            message_dict = {
                'username': user1,
                'content': new_message
            }
            chat = container.chat_message('user')
            chat.markdown(message_dict['content'])
            messages.append(message_dict)
            save_messages(user1, user2, messages)

def page_conversations(element):
    if st.session_state['recipient_user'] != "":
        element.title(f"Conversando com :green[{st.session_state['recipient_user']}]")
        element.divider()
    
    # Comentar para falar comigo mesmo
    users = get_user_list() 
    users = [i for i in users if i != st.session_state['logged_user']]
    recipient_user = element.selectbox('Selecione o usuário para conversar', users)
    
    # recipient_user = element.selectbox('Selecione o usuário para conversar', get_user_list())
    element.button(
        'Iniciar conversa',
        on_click=select_conversation,
        args=(recipient_user, )
    )

def select_conversation(recipient_user):
    st.session_state['recipient_user'] = recipient_user
    st.success(f'Iniciando conversa com {recipient_user}')
    time.sleep(2)
    change_page('chat')

if __name__ == '__main__':
    main()