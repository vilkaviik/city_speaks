import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class TextClustering:
    def __init__(self, n_clusters: int = 5):
        """
        :param n_clusters: Примерное количество тем (кластеров), которые мы ищем.
        """
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            max_df=0.8,       # Игнорировать слова, которые есть в 80% документов (слишком общие)
            min_df=2,         # Игнорировать слова, которые встретились только в одном посте
            ngram_range=(1, 2) # Учитывать одиночные слова и словосочетания (напр. "криптовалютный рынок")
        )
        self.model = KMeans(
            n_clusters=self.n_clusters, 
            random_state=42, 
            n_init=10
        )

    def fit_predict(self, texts: list[str]) -> list[int]:
        """
        Обучает модель на текстах и возвращает номера кластеров для каждого текста.
        """
        if not texts or len(texts) < self.n_clusters:
            # Если текстов меньше, чем кластеров, K-Means выдаст ошибку
            return [0] * len(texts)

        # 1. Превращаем тексты в матрицу признаков (числа)
        tfidf_matrix = self.vectorizer.fit_transform(texts)

        # 2. Запускаем кластеризацию
        self.model.fit(tfidf_matrix)

        # 3. Возвращаем метки (список ID кластеров: 0, 1, 2...)
        return self.model.labels_.tolist()

    def get_top_keywords(self, n_words: int = 10) -> dict:
        """
        Возвращает ключевые слова для каждого кластера, чтобы понять, о чем они.
        """
        common_words = {}
        feature_names = self.vectorizer.get_feature_names_out()
        centroids = self.model.cluster_centers_.argsort()[:, ::-1]

        for cluster_num in range(self.n_clusters):
            words = [feature_names[i] for i in centroids[cluster_num, :n_words]]
            common_words[cluster_num] = words
            
        return common_words
