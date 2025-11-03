import webbrowser
import os

def get_vk_token_instructions():
    """Инструкция по получению VK токена"""
    print("=" * 50)
    print("🎵 ПОЛУЧЕНИЕ VK SERVICE TOKEN")
    print("=" * 50)
    
    print("\n1. Перейдите на страницу: https://vk.com/apps?act=manage")
    print("2. Создайте новое приложение (тип: Standalone)")
    print("3. После создания нажмите на приложение → 'Редактировать'")
    print("4. В разделе 'Настройки' скопируйте 'Service Token'")
    print("5. Добавьте его в файл .env как VK_SERVICE_TOKEN=your_token")
    
    print("\n📋 Альтернативный способ:")
    print("1. Зарегистрируйте приложение: https://vk.com/editapp?act=create")
    print("2. Платформа: 'Standalone'")
    print("3. Название: 'Discord Music Bot'")
    print("4. После создания скопируйте Service Token")
    
    input("\nНажмите Enter чтобы открыть страницу управления приложениями...")
    webbrowser.open("https://vk.com/apps?act=manage")

if __name__ == "__main__":
    get_vk_token_instructions()