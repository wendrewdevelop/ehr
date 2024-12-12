import time
import base64
import urllib3
import gzip
import zlib
from urllib3.exceptions import SSLError
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from http.cookiejar import CookieJar
from .session import HTTPSessionManager
from .sockets import WebSocketManager


class Request:
    def __init__(self, method, debug=False,
                 proxies=None,
                 user_agent=None,
                 auth=None):
        self.method = method
        self.session_manager = HTTPSessionManager()
        self.debug = debug
        self.proxies = proxies
        self.user_agent = user_agent or "MyHttpClient/1.0"
        self.auth = auth
        self.token_info = None

    def _add_user_agent(self, headers):
        """
        Add or override the User-Agent header.

        :param headers: The existing headers
        :return: Updated headers with User-Agent included
        """
        if headers is None:
            headers = {}
        headers["User-Agent"] = self.user_agent
        return headers

    def _add_authentication(self, headers):
        """
        Add authentication headers based on the provided authentication type.

        :param headers: Existing headers
        :return: Updated headers with authentication
        """
        if not headers:
            headers = {}

        if self.auth:
            if "basic" in self.auth:
                # Basic Authentication
                username, password = self.auth["basic"]
                credentials = f"{username}:{password}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded_credentials}"

            elif "bearer" in self.auth:
                # Bearer Token Authentication
                token = self.auth["bearer"]
                headers["Authorization"] = f"Bearer {token}"

            elif "oauth2" in self.auth:
                # OAuth 2.0 Authentication
                if self.token_info is None or time.time() > self.token_info["expires_at"]:
                    self.token_info = self._fetch_oauth2_token(self.auth["oauth2"])
                headers["Authorization"] = f"Bearer {self.token_info['access_token']}"

        return headers

    def _fetch_oauth2_token(self, oauth_config):
        """
        Fetch OAuth 2.0 token using client credentials.

        :param oauth_config: Dictionary with OAuth 2.0 configuration
        :return: Token information
        """
        token_url = oauth_config["token_url"]
        client_id = oauth_config["client_id"]
        client_secret = oauth_config["client_secret"]
        scope = oauth_config.get("scope", "")

        body = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.session_manager.request(
            method="POST", url=token_url, headers=headers, body=urlencode(body)
        )

        if response.status != 200:
            raise Exception(f"Failed to fetch OAuth 2.0 token: {response.data.decode()}")

        token_data = response.json()
        return {
            "access_token": token_data["access_token"],
            "expires_at": time.time() + token_data["expires_in"],
        }

    def _decode_compressed_response(self, response):
        """
        Decode the compressed response content if necessary.

        :param response: urllib3.response.HTTPResponse object
        :return: Decoded content as string
        """
        encoding = response.headers.get("Content-Encoding", "").lower()

        if encoding == "gzip":
            return gzip.decompress(response.data).decode("utf-8")
        elif encoding == "deflate":
            return zlib.decompress(response.data).decode("utf-8")
        else:
            return response.data.decode("utf-8")

    def _sanitize_headers(self, headers):
        if not headers:
            return {}

        sanitized = headers.copy()
        sensitive_keys = {"Authorization", "Cookie", "Set-Cookie"}
        for key in sensitive_keys:
            sanitized[key] = "[REDACTED]"

        return sanitized

    def _log_request(self, method, url, headers, params=None):
        if self.debug:
            sanitized_headers = self._sanitize_headers(headers)
            print("DEBUG: HTTP Request")
            print(f'Method::: {method}')
            print(f'Url::: {url}')
            if params:
                print(f'Params::: {params}')
            print(f'Headers::: {sanitized_headers}')
            if self.proxies:
                print(f'PROXIES::: {self.proxies}')

    def build_url(self, base_url, params=None):
        """
        Constrói uma URL com query strings adicionadas ou atualizadas.

        :param base_url: URL base.
        :param params: Dicionário contendo os parâmetros de consulta.
        :return: URL com query strings.
        """
        if not params:
            return base_url

        parsed_url = urlparse(base_url)
        existing_params = parse_qs(parsed_url.query)
        existing_params.update(params)

        new_query_string = urlencode(existing_params, doseq=True)
        new_url = urlunparse((
            parsed_url.scheme, parsed_url.netloc, parsed_url.path,
            parsed_url.params, new_query_string, parsed_url.fragment
        ))

        return new_url

    def parse_response(self, response):
        """
        Analisa a resposta HTTP com base no tipo de conteúdo.
        """
        try:
            if isinstance(response, dict):
                content_type = response.get("Content-Type", "").lower()
                status = response.get("status", None)
                data = response.get("data", None)
            else:
                # Assume que é um objeto HTTPResponse
                content_type = response.headers.get("Content-Type", "").lower()
                status = response.status
                data = response.data

                if "application/json" in content_type:
                    return status, data.decode("utf-8"), json.loads(data)
                elif "application/xml" in content_type or "text/xml" in content_type:
                    return status, data.decode("utf-8"), ET.fromstring(data)
                elif "text/" in content_type:
                    return status, data.decode("utf-8")
                else:
                    return status, data
        except Exception as e:
            print(f"Erro ao analisar a resposta: {e}")
            return 500, "Erro na análise da resposta", None

    def request(self, url: str, headers=None, body=None, params=None):
        """
        Send an HTTP request using the specified method.

        :param url: URL for the request
        :param headers: Optional dictionary of headers
        :param body: Optional body for the request (used in POST, PUT, etc.)
        :param params: Optional query parameters for the request
        :return: Parsed response based on content type
        """
        headers = self._add_user_agent(headers)
        headers = self._add_authentication(headers)
        url = self.build_url(url, params)
        self._log_request(self.method, url, headers, params)

        if self.proxies:
            proxy_manager = urllib3.ProxyManager(
                proxy_url=self.proxies.get("https", self.proxies.get("http")),
                proxy_headers=headers
            )
            request_function = proxy_manager.request
        else:
            request_function = self.session_manager.request

            try:
                match self.method.upper():
                    case "POST":
                        raw_response = request_function(
                            method="POST", url=url, headers=headers, body=body
                        )
                    case "GET":
                        raw_response = request_function(
                            method="GET", url=url, headers=headers
                        )
                    case "PUT":
                        raw_response = request_function(
                            method="PUT", url=url, headers=headers, body=body
                        )
                    case "DELETE":
                        raw_response = request_function(
                            method="DELETE", url=url, headers=headers
                        )
                    case _:
                        raw_response = request_function(
                            method="GET", url=url, headers=headers
                        )

                return self.parse_response(raw_response)

            except SSLError as e:
                print(f"SSL Error: {e}")
                raise
            except urllib3.exceptions.ProxyError as e:
                print(f"Proxy Error: {e}")
                raise
            except Exception as e:
                print(f"Request Error: {e}")
                raise
