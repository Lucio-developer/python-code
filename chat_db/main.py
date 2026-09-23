import streamlit as st
import time
from database import init_db, db_load_messages, db_save_message
from auth import register_user, validate_login, get_available_users

RERUN_INTERVAL = 3

def main():
    init_db()
    initialize_session()

    if st.session_state['current_page'] == 'login':
        page_login()
    elif st.session_state['current_page'] == 'chat':
        # Renderiza a barra lateral primeiro
        sidebar_container = st.sidebar.container()
        page_conversations(sidebar_container)

        # Só renderiza o chat se houver um destinatário selecionado
        if st.session_state['recipient_user'] != '':
            page_chat()

def initialize_session():
    if 'current_page' not in st.session_state:
        change_page('login')

    if 'logged_user' not in st.session_state:
        st.session_state['logged_user'] = ''

    if 'recipient_user' not in st.session_state:
        st.session_state['recipient_user'] = ''

    # Garante que a chave existe para a comparação
    if 'last_sent_message' not in st.session_state:
        st.session_state['last_sent_message'] = ''

def change_page(page_name):
    st.session_state['current_page'] = page_name

# ---------------------------------- PÁGINAS -------------------------------- #

def page_login():
    st.header('🟢​ Sistema de Mensagens Particular', divider=True)
    tab1, tab2 = st.tabs(['Entrar', 'Cadastrar'])

    with tab1.form(key='login'):
        username = st.text_input('Digite seu nome de usuário')
        password = st.text_input('Digite sua senha', type='password')
        if st.form_submit_button('Entrar'):
            success, message = validate_login(username, password)
            if success:
                st.success(message)
                time.sleep(1)
                st.session_state['logged_user'] = username.strip().upper()
                change_page('chat')
                st.rerun()
            else:
                st.error(message)

    with tab2.form(key='cadastro'):
        username = st.text_input('Cadastre um novo nome de usuário')
        password = st.text_input('Cadastre uma nova senha', type='password')
        if st.form_submit_button('Cadastrar'):
            success, message = register_user(username, password)
            if success:
                st.success(message)
                time.sleep(1)
                st.session_state['logged_user'] = username.strip().upper()
                change_page('chat')
                st.rerun()
            else:
                st.error(message)

# FRAGMENTO DE MENSAGENS: Atualiza isoladamente a cada 3 segundos
@st.fragment(run_every=3)
def render_chat_messages(user1, user2):
    messages = db_load_messages(user1, user2)
    
    container = st.container()
    for msg in messages:
        sender_name = 'user' if msg['username'] == user1 else msg['username']
        avatar = None if msg['username'] == user1 else '⚪'
        chat = container.chat_message(sender_name, avatar=avatar)
        chat.markdown(msg['content'])

# --------------------------------------------------------------------------
# PÁGINA DE CHAT
# --------------------------------------------------------------------------
def page_chat():
    st.title(f'🟢 My Chat, {st.session_state["logged_user"]}')
    st.divider()

    user1 = st.session_state['logged_user']
    user2 = st.session_state['recipient_user']

    # 1. Chama o fragmento que fica recarregando sozinho em segundo plano
    render_chat_messages(user1, user2)

    # 2. Caixa de texto para envio fora do fragmento (uma única caixa fixa)
    new_message = st.chat_input('Digite uma mensagem')
    
    if new_message:
        if new_message != st.session_state.get('last_sent_message', ''):
            st.session_state['last_sent_message'] = new_message
            db_save_message(user1, user2, new_message)
            st.rerun()

    def send_message_callback():
        texto = st.session_state.get('chat_input_key', '')
        if texto.strip():
            db_save_message(user1, user2, texto)
            # Limpa o input para não re-enviar nos próximos reruns automáticos
            st.session_state['chat_input_key'] = ''

def page_conversations(element):
    if st.session_state['recipient_user'] != "":
        element.title(f"Conversando com :green[{st.session_state['recipient_user']}]")
        element.divider()
    
    users = get_available_users(st.session_state['logged_user'])
    
    if not users:
        element.warning("Nenhum outro usuário cadastrado no momento.")
        return

    recipient_user = element.selectbox('Selecione o usuário para conversar', users)
    
    element.button(
        'Iniciar conversa',
        on_click=select_conversation,
        args=(recipient_user, )
    )

def select_conversation(recipient_user):
    st.session_state['recipient_user'] = recipient_user
    st.success(f'Iniciando conversa com {recipient_user}')
    time.sleep(1)
    change_page('chat')

if __name__ == '__main__':
    main()