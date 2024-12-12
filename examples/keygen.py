import time
import random
from ehr_library.core import Request
from ehr_library.misc.keys import APIKeyManager


keys_with_limits = {
    "key1": {"value": "valor_real_chave_1", "limit": 2},
    "key2": {"value": "valor_real_chave_2", "limit": 3},
    "key3": {"value": "valor_real_chave_3", "limit": 1},
}
rotation_interval = 600
key_manager = APIKeyManager(keys_with_limits, rotation_interval)
url = "https://api.example.com/endpoint"
method = "GET"

for i in range(5):
    try:
        key = key_manager.get_next_key()
        headers = {"Authorization": f"Bearer {key}"}
        response = request_instance.request(url, headers=headers)
        print(f"Requisição {i + 1}: Status: {response.status}, Key Used: {key}")
    except RuntimeError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    time.sleep(1)


"""
EXPECTED OUTPUT

DEBUG: HTTP Request
Method::: GET
Url::: https://api.example.com/endpoint
Headers::: {'Authorization': '[REDACTED]'}
Requisição 1: Status: 200, Key Used: valor_real_chave_1
DEBUG: HTTP Request
Method::: GET
Url::: https://api.example.com/endpoint
Headers::: {'Authorization': '[REDACTED]'}
Requisição 2: Status: 200, Key Used: valor_real_chave_2

"""
