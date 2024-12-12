from ehr_library.core import Request


def get_example():
    """
    Exemplo de uma requisição HTTP GET.
    """
    url = "https://jsonplaceholder.typicode.com/posts/1"
    client = Request(method="GET", debug=True)
    response = client.request(url)
    print("GET Response:", response)


if __name__ == "__main__":
    get_example()
