from ehr_library.misc.call import AsyncRequestHandler


# Lista de URLs para testar
urls = [
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/posts/2",
    "https://jsonplaceholder.typicode.com/posts/3",
    "https://jsonplaceholder.typicode.com/posts/4",
    "https://invalid.url",  # Exemplo de URL com erro
]

# Cria o manipulador e faz as requisições
handler = AsyncRequestHandler(urls)
responses = handler.request()

# Exibe as respostas
for url, result in responses.items():
    print(f"URL: {url}")
    if "error" in result:
        print(f"  Erro: {result['error']}")
    else:
        print(result)
