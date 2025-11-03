# create_correct_env.py
correct_token = "MTQzNDYxMTkyOTIxMjc4MDcwNA.GWug8t.3dq_vT1Ck-_PlFEHZroeIeH_dN4OHo8lK2ZkVw"

with open('.env', 'w', encoding='utf-8') as f:
    f.write(f'DISCORD_BOT_TOKEN={correct_token}')

print("✅ .env файл создан с ПРАВИЛЬНЫМ токеном!")
print("🔑 Проверка токена...")

with open('.env', 'r') as f:
    content = f.read()
    print(f"📄 Содержимое: {content}")
    
    if correct_token in content:
        print("✅ Токен записан правильно!")
    else:
        print("❌ Токен записан НЕПРАВИЛЬНО!")

input("🎯 Нажмите Enter...")