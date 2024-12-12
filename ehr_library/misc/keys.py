import time
import random
import threading


class APIKeyManager:
    def __init__(self, keys_with_limits, rotation_interval=None):
        """
        Inicializa o gerenciador de chaves de API.

        :param keys_with_limits: Dicionário {chave: limite} onde 'limite' é o número máximo de usos por chave.
        :param rotation_interval: (Opcional) Intervalo em segundos para rotacionar as chaves periodicamente.
        """
        self.keys_with_limits = keys_with_limits
        self.usage_count = {key: 0 for key in keys_with_limits}
        self.last_used_key = None

        # Inicia a rotação periódica das chaves, se o intervalo for fornecido
        if rotation_interval:
            thread = threading.Thread(target=self.rotate_keys_periodically, args=(rotation_interval,))
            thread.daemon = True
            thread.start()

    def get_next_key(self):
        """
        Retorna a próxima chave de API disponível com base nos limites.

        :return: Uma chave de API disponível.
        :raises: RuntimeError se nenhuma chave estiver disponível.
        """
        for key, data in self.keys_with_limits.items():
            if self.usage_count[key] < data["limit"]:
                self.usage_count[key] += 1
                self.last_used_key = key
                print(f'VALOR CHAVE::: {data["value"]}')
                return data["value"]

        raise RuntimeError("Todas as chaves atingiram o limite de uso.")

    def reset_usage(self):
        """
        Reseta os contadores de uso para todas as chaves.
        """
        self.usage_count = {key: 0 for key in self.keys_with_limits}

    def rotate_keys_periodically(self, interval_seconds):
        """
        Rotaciona as chaves periodicamente, resetando os contadores de uso.

        :param interval_seconds: Intervalo em segundos para a rotação.
        """
        while True:
            print("Resetando uso de chaves...")
            self.reset_usage()
            time.sleep(interval_seconds)

    def get_next_key_random(self):
        """
        Retorna uma chave de API disponível aleatoriamente.
        """
        available_keys = [key for key, count in self.usage_count.items() if count < self.keys_with_limits[key]]
        if not available_keys:
            raise RuntimeError("Todas as chaves atingiram o limite de uso.")
        selected_key = random.choice(available_keys)
        self.usage_count[selected_key] += 1
        return selected_key
