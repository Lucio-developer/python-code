from database import db_get_all_users, db_load_messages

print("--- USUÁRIOS CADASTRADOS ---")
users = db_get_all_users()
print(users)

print("\n--- MENSAGENS ENTRE USUÁRIOS ---")
if len(users) >= 2:
    # Testa a busca de mensagens entre os dois primeiros usuários
    mensagens = db_load_messages(users[0], users[1])
    for msg in mensagens:
        print(f"[{msg['username']}]: {msg['content']}")
else:
    print("Cadastre pelo menos 2 usuários no chat para ver mensagens.")