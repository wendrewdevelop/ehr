from ehr_library.core import Request


if __name__ == "__main__":
    client = Request("GET")

    response = client.request(
        url="https://httpbin.org/get"
    )
    print("GET Status:", response.status)
    print("GET Data:", response.data.decode("utf-8"))