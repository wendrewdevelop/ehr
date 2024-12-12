import asyncio
import aiohttp


class AsyncRequestHandler:
    def __init__(self, urls):
        self.urls = urls

    async def fetch(self, session, url):
        """Faz uma requisição GET assíncrona a um URL."""
        try:
            async with session.get(url) as response:
                return {
                    "status": response.status,
                    "data": await response.text(),
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    async def fetch_all(self):
        """Envia requisições para todos os URLs simultaneamente."""
        async with aiohttp.ClientSession() as session:
            tasks = {url: self.fetch(session, url) for url in self.urls}
            responses = await asyncio.gather(*tasks.values())
            # Organiza os resultados em um dicionário estruturado
            return {url: result for url, result in zip(tasks.keys(), responses)}

    def request(self):
        """Executa o loop de eventos e retorna as respostas."""
        return asyncio.run(self.fetch_all())
