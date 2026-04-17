import re
import nltk
from nltk.corpus import stopwords
import pymorphy3

## Cleaning text - stop words, tolower() and etc

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextCleaner:
    def __init__(self, additional_stop_words: set = None):
        self.stop_words = set(stopwords.words('russian'))

        # Список "мусорных" слов, специфичных для Telegram
        telegram_noise = {
            'это', 'который', 'свой', 'наш', 'ваш', 'весь', 'мочь', 
            'подписываться', 'ссылка', 'канал', 'чат', 'группа', 
            'читать', 'пост', 'телеграм', 'telegram', 'tme'
        }
        self.stop_words.update(telegram_noise)
        
        if additional_stop_words:
            self.stop_words.update(additional_stop_words)

    def clean(self, text: str) -> str:
        if not text:
            return ""

        # 1. Приводим к нижнему регистру
        text = text.lower()

        # 2. Удаляем URL-ссылки (http, https, t.me)
        text = re.sub(r'https?://\S+|www\.\S+|t\.me/\S+', '', text)

        # 3. Удаляем упоминания (@username)
        text = re.sub(r'@\w+', '', text)

        # 4. Удаляем эмодзи и спецсимволы
        # Регулярка [^а-яёa-z\s] удалит всё, что не является русской/английской буквой
        text = re.sub(r'[^а-яёa-z\s]', ' ', text)

        # 5. Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()

        # 6. Фильтруем стоп-слова и слишком короткие слова (меньше 3 символов)
        words = text.split()
        filtered_words = [
            word for word in words 
            if word not in self.stop_words
        ]

        return " ".join(filtered_words)

## Normalization

class TextProcessor:
    def __init__(self):
        # Инициализируем морфологический анализатор
        self.morph = pymorphy3.MorphAnalyzer()

    def lemmatize(self, cleaned_text: str) -> str:
        
        if not cleaned_text:
            return ""

        words = cleaned_text.split()
        lemmatized_words = []

        for word in words:
            # Анализируем слово и берем первый (самый вероятный) вариант разбора
            parsed = self.morph.parse(word)[0]
            # .normal_form возвращает начальную форму слова
            lemmatized_words.append(parsed.normal_form)

        return " ".join(lemmatized_words)