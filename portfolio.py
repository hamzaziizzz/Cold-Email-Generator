import pandas as pd
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class Portfolio:
    def __init__(self, file_path="resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.vectorizer = TfidfVectorizer()
        self.index = None
        self.embeddings = None

    def load_portfolio(self):
        # Convert tech stack to embeddings
        tech_stack = self.data["Tech stack"].astype(str).tolist()  # Ensure all entries are strings
        self.embeddings = self.vectorizer.fit_transform(tech_stack).toarray()

        # Build FAISS index
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(np.array(self.embeddings, dtype=np.float32))

    def query_links(self, skills):
        # Ensure skills input is a string
        query_vector = self.vectorizer.transform([str(skills)]).toarray().astype(np.float32)

        # Perform search
        distances, indices = self.index.search(query_vector, k=2)
        links = [self.data.iloc[i]["Links"] for i in indices[0]]
        return links
