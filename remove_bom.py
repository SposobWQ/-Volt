# Создай файл remove_bom.py и запусти его:
import os
import glob

def remove_bom_from_files():
    python_files = glob.glob('**/*.py', recursive=True)
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # Если файл начинается с BOM, перезаписываем без него
            if content.startswith('\ufeff'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content.lstrip('\ufeff'))
                print(f"✅ Удален BOM из: {file_path}")
        except Exception as e:
            print(f"❌ Ошибка обработки {file_path}: {e}")

if __name__ == "__main__":
    remove_bom_from_files()