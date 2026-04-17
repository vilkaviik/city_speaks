import numpy as np
import requests
import os

class TextEmbedder:
    def __init__(self, folder_id: str, api_key: str):
        self.folder_id = folder_id
        self.api_key = api_key
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"


    def get_embeddings(self, texts: list[str]) -> np.ndarray:
        """Превращает список текстов в матрицу векторов"""
        if not texts:
            return np.array([])
    
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id
        }

        embeddings = []
        print(f"Пытаюсь отправить {len(texts)} текстов. Первый текст: {texts[0][:50]}")
        for text in texts:

            if not text or not str(text).strip():
                continue

            payload = {
                "modelUri": f"emb://{self.folder_id}/text-search-doc/latest",
                "text": text
            }
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status() # Выдаст ошибку, если API ответит не 200

            if response.status_code == 200:
                print(f"Векторизация выполнена успешно")
                response.raise_for_status()

            vector = response.json().get("embedding")
            embeddings.append(vector)

        return np.array(embeddings)


