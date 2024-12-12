import urllib3
import certifi
from urllib3.util.retry import Retry
from http.cookiejar import CookieJar
from urllib3.contrib.pyopenssl import inject_into_urllib3


class HTTPSessionManager:
    """
    Centralized session manager for HTTP requests with retry policy.
    """

    def __init__(self, retries=3, backoff_factor=0.3):
        self.cookie_jar = CookieJar()
        self.http = urllib3.PoolManager(
            headers={},
            retries=Retry(
                total=retries,
                backoff_factor=backoff_factor,
                status_forcelist=[500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PUT", "DELETE"],
            ),
            cert_reqs="CERT_REQUIRED",
            ca_certs=certifi.where(),
        )
        self.retries = retries
        self.backoff_factor = backoff_factor

    def request(self, method, url, headers=None, body=None, download_path=None):
        """
        Make an HTTP request using the managed session.

        :param method: HTTP method (GET, POST, etc.)
        :param url: URL for the request
        :param headers: Optional headers dictionary
        :param body: Optional request body
        :param download_path: Optional path to save the response content as a file.
        :return: Response data or path to the saved file.
        """

        cookie_headers = self._generate_cookie_header(url)
        print(f'HEADERS::: {headers}')
        headers = cookie_headers

        response = self.http.request(
            method=method,
            url=url,
            headers=headers,
            body=body,
            retries=self.retries,
        )

        self._store_cookies(url, response)

        if download_path and method.upper() == "GET" and response.status == 200:
            try:
                with open(download_path, "wb") as file:
                    file.write(response.data)
                return {"message": "File downloaded successfully", "path": download_path}
            except IOError as e:
                return {"error": f"Failed to save file: {e}"}
        else:
            return {
                "status": response.status,
                "data": response.data.decode('utf-8') if response.data else None,
            }

    def _generate_cookie_header(self, url):
        """
        Generate the Cookie header based on the current cookies in the jar.
        """
        cookies = [f"{cookie.name}={cookie.value}" for cookie in self.cookie_jar if cookie.domain in url]
        return {"Cookie": "; ".join(cookies)} if cookies else {}

    def _store_cookies(self, url, response):
        """
        Store cookies from the response headers into the CookieJar.
        """
        set_cookie_headers = response.headers.get_all("Set-Cookie", [])
        for header in set_cookie_headers:
            self.cookie_jar.extract_cookies_from_response(header, url)

    def get_cookies(self):
        """
        Get all cookies as a dictionary.
        """
        return {cookie.name: cookie.value for cookie in self.cookie_jar}

    def clear_cookies(self):
        """
        Clear all stored cookies.
        """
        self.cookie_jar.clear()
