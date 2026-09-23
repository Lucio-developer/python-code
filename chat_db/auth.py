from database import db_create_user, db_get_user_password, db_get_all_users

def register_user(username, password):
    """Trata a criação e validação de cadastro do usuário."""
    clean_username = username.strip().upper()
    
    if not clean_username:
        return False, "Nome de usuário inválido!"
    if not password:
        return False, "A senha não pode estar em branco!"

    success = db_create_user(clean_username, password)
    if success:
        return True, "Usuário cadastrado com sucesso!"
    else:
        return False, "Erro ao cadastrar: Nome de usuário já está em uso."

def validate_login(username, password):
    """Valida as credenciais do usuário durante o login."""
    clean_username = username.strip().upper()
    saved_password = db_get_user_password(clean_username)

    if saved_password and saved_password == password:
        return True, "Login efetuado com sucesso!"
    return False, "Erro ao logar: Usuário ou senha incorretos."

def get_available_users(current_user):
    """Retorna todos os usuários cadastrados, exceto o usuário logado."""
    all_users = db_get_all_users()
    return [user for user in all_users if user != current_user]