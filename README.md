# EHR - EASY HTTP REQUEST
A HTTP request library like the others.

## PYPI
https://test.pypi.org/project/ehr-library/0.3.0/

## USAGE EXAMPLE

```python
    In [1]: from ehr_library.core import Request
    ...:
    ...:
    ...: if __name__ == "__main__":
    ...:     client = Request("GET")
    ...:
    ...:     response = client.request(
    ...:         url="https://httpbin.org/get"
    ...:     )
    ...:     print("GET Status:", response.status)
    ...:     print("GET Data:", response.data.decode("utf-8"))
    ...:
    GET Status: 200
    GET Data: {
    "args": {},
    "headers": {
        "Accept-Encoding": "identity",
        "Host": "httpbin.org",
        "User-Agent": "python-urllib3/2.2.3",
        "X-Amzn-Trace-Id": "Root=1-6748eb9b-03a82d60743c0774012c5735"
    },
    "origin": "138.122.133.5",
    "url": "https://httpbin.org/get"
    }
```

## License
This project is licensed under the Freedom Reciprocal License 1.0 - see the [LICENSE](https://github.com/ONEMANCOMPANY/ehr/blob/master/license) file for details.