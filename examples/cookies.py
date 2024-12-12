from ehr_library.core import Request


if __name__ == "__main__":
    manager = Request(method="GET")
    
    manager.request(url="https://httpbin.org/cookies/set?name=value")
    print("Cookies armazenados:", manager.session_manager.get_cookies())
    
    response = manager.request(url="https://httpbin.org/cookies")
    print("Resposta:", response)
