import re
import nltk
from nltk.corpus import stopwords
import pymorphy3

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextCleaner:
    def __init__(self, additional_stop_words: set = None):
        self.stop_words = set(stopwords.words('russian'))

        # Список "мусорных" слов
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

        text = text.lower()

        text = re.sub(r'https?://\S+|www\.\S+|t\.me/\S+', '', text)

        text = re.sub(r'@\w+', '', text)

        text = re.sub(r'[^а-яёa-z\s]', ' ', text)

        text = re.sub(r'\s+', ' ', text).strip()

        words = text.split()
        filtered_words = [
            word for word in words 
            if word not in self.stop_words
        ]

        return " ".join(filtered_words)

## Normalization

class TextProcessor:
    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer()

    def lemmatize(self, cleaned_text: str) -> str:
        
        if not cleaned_text:
            return ""

        words = cleaned_text.split()
        lemmatized_words = []

        for word in words:
            parsed = self.morph.parse(word)[0]
            lemmatized_words.append(parsed.normal_form)

        return " ".join(lemmatized_words)