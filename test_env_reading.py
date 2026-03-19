# test_env_reading.py
def load_api_key_from_env():
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            print("Conteúdo do .env:")
            print(repr(content))
            for line in content.splitlines():
                if line.startswith('GEMINI_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    print("Chave encontrada:", repr(key))
                    return key
    except Exception as e:
        print("Erro:", e)
    return None

load_api_key_from_env()