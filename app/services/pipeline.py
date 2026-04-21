import httpx
from typing import List

from requests import Session

from app.services.data_analysis.preprocessing import TextCleaner
from app.services.data_analysis.preprocessing import TextProcessor
from app.services.data_analysis.embedder import TextEmbedder
from app.services.trend_discover import TrendDiscover
from app.services.metrics_counter import get_post_metrics

from sqlalchemy.orm import Session
from app.db.models import Post
from app.db.models import Industry
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from app.db.session import SessionLocal

from app.core.config import settings

class AnalysisPipeline:
    def __init__(self, folder_id: str, api_key: str):
        self.folder_id = folder_id
        self.api_key = api_key
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

        self.cleaner = TextCleaner()
        self.processor = TextProcessor()
        self.embedder = TextEmbedder(folder_id, api_key)
        
    async def process_new_posts(self):
        db = SessionLocal() 

        posts = db.query(Post).options(selectinload(Post.industry))\
                  .all()

        all_industries = db.query(Industry).all()
        industry_names = [ind.name for ind in all_industries]

        if not industry_names:
            print("Список индустрий пуст. Невозможно выполнить классификацию.")
            return

        for post in posts:
            print(f"DEBUG: Пост {post.id}, индустрии в объекте: {post.industry}")
            if post.normalized_text:
                normalized = post.normalized_text
                print(f"Пост {post.id}: используем существующую нормализацию")
            else:
                cleaned = self.cleaner.clean(post.text)
                normalized = self.processor.lemmatize(cleaned)
                post.cleaned_text = cleaned
                post.normalized_text = normalized
                print(f"Пост {post.id}: нормализация выполнена")

            if post.embedding is None:
                vector = self.embedder.get_embeddings([normalized])[0]
                post.embedding = vector.tolist()  # Сохраняем в базу как список чисел
                print(f"Пост {post.id}: эмбеддинг создан")

            if not post.industry:
                print(f"Определяю категорию поста")
                predicted_name = await self._classify_industry(post.text, industry_names)
                
                print(f"DEBUG: LLM вернула '{predicted_name}'. Доступные в базе: {industry_names}")

                industry_obj = next((i for i in all_industries if i.name == predicted_name), None)

                if industry_obj:
                    post.industry.append(industry_obj)
                    print(f"Присваиваю категорию {predicted_name} посту {post.id}")
                else:
                    print(f"Не удалось сопоставить ответ LLM '{predicted_name}' ни с одной индустрией из базы")

            else:
                print(f"Пост {post.id}: уже имеет категорию, пропускаю классификацию")
             
        db.commit()

        trend_service = TrendDiscover(self.api_key, self.folder_id)
        await trend_service.discover_trends(db)

    async def _classify_industry(self, text: str, industries: List[str]) -> str:
        # Список индустрий
        industry_list = ", ".join(industries)

        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id
        }

        payload = {
        "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
        "taskDescription": "Определи категорию новостного поста",
        "labels": industry_list,
        "completionOptions": {"temperature": 0, "maxTokens": 50},
        "messages": [
            {
                "role": "system",
                "text": f"Ты — эксперт по анализу городских новостей Красноярска. Твоя задача — отнести текст поста к ОДНОЙ из категорий: {industry_list}. Отвечай строго одним словом из предложенного списка, без лишних знаков препинания. ЗАПРЕЩЕНО: писать пояснения, вводить свои категории, рассуждать или дублировать вопрос"
            },
            {
                "role": "user",
                "text": f"Текст поста: {text[:500]}" # Берем начало для экономии токенов
            }
        ]
        }   
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, headers=headers, json=payload)

            if response.status_code != 200:
                print(f"HTTP-ошибка {response.status_code} при классификации:")

            result = response.json()

            try:
                alternatives = result.get('result', {}).get('alternatives', [])
                if not alternatives:
                    print("Некорректный формат ответа от API: отсутствуют alternatives")
                    return "Общество"
                    
                raw_text = alternatives[0]['message']['text']
                predicted_name = raw_text.split('\n')[0].strip().strip(".").strip('"')
                
                print(f"DEBUG: LLM выдала оригинальный текст: '{raw_text[:50]}...'")
                print(f"DEBUG: Очищенное имя: '{predicted_name}'")

                return predicted_name
            
            except (KeyError, IndexError) as e:
                print(f"Ошибка при парсинге JSON: {e}")
                return "Общество"





    
    


 





