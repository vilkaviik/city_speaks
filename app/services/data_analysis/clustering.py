import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class TextClustering:
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            max_df=0.8,
            min_df=2,         
            ngram_range=(1, 2) 
        )
        self.model = KMeans(
            n_clusters=self.n_clusters, 
            random_state=42, 
            n_init=10
        )

    def fit_predict(self, texts: list[str]) -> list[int]:

        if not texts or len(texts) < self.n_clusters:
            return [0] * len(texts)

        tfidf_matrix = self.vectorizer.fit_transform(texts)

        self.model.fit(tfidf_matrix)

        return self.model.labels_.tolist()

    def get_top_keywords(self, n_words: int = 10) -> dict:

        common_words = {}
        feature_names = self.vectorizer.get_feature_names_out()
        centroids = self.model.cluster_centers_.argsort()[:, ::-1]

        for cluster_num in range(self.n_clusters):
            words = [feature_names[i] for i in centroids[cluster_num, :n_words]]
            common_words[cluster_num] = words
            
        return common_words
