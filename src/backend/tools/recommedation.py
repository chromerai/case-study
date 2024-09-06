from typing import List, Dict
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from ..config import config

class RecommendationTool:
    def __init__(self, uri: str, user: str, password: str, model_name: str = 'all-MiniLM-L6-v2'):
        self.driver = GraphDatabase.driver(config.NEO44J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
        self.model = SentenceTransformer(model_name)

    def recommend(self, query: str, top_k: int = 5) -> List[Dict]:
        # Convert query to embedding
        embedding = self.model.encode(query).tolist()

        with self.driver.session() as session:
            return session.read_transaction(self._similarity_search, embedding, top_k)

    def _similarity_search(self, tx, embedding: List[float], top_k: int) -> List[Dict]:
        query = """
        CALL db.index.vector.queryNodes('part_embeddings', $top_k, $embedding) 
        YIELD node, score
        RETURN node.name AS name, node.description AS description, score
        """
        result = tx.run(query, top_k=top_k, embedding=embedding)
        return [dict(record) for record in result]

    def close(self):
        self.driver.close()