from typing import Any, Dict, List
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from ..config import config

class SymptomAnalysisTool:
    def __init__(self):
        self.driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_URI))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def __call__(self, model: str, symptom: str) -> Dict[str, Any]:
        parts = self._find_relevant_parts(model, symptom)
        relevant_qas = self._find_relevant_qas(parts, symptom)
        return {
            "model": model,
            "symptom": symptom,
            "relevant_parts": parts,
            "relevant_qas": relevant_qas
        }

    def _find_relevant_parts(self, model: str, symptom: str) -> List[Dict[str, Any]]:
        print(" in find relevant parts")
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Model {name: $model})-[:HAS_ISSUE]->(s:Symptom {name: $symptom})<-[:FIXES]-(p:Part)
                RETURN p.name AS name, p.ps_number AS ps_number, p.mfg_number AS mfg_number,
                       p.description AS description
                LIMIT 2
            """, model=model, symptom=symptom)
            return [dict(record) for record in result]

    def _find_relevant_qas(self, parts: List[Dict[str, Any]], symptom: str) -> List[Dict[str, Any]]:
        combined_embedding = self.model.encode(symptom + " " + " ".join([p['name'] + p['ps_number'] for p in parts])).tolist()
        
        with self.driver.session() as session:
            result = session.run("""
            CALL db.index.vector.queryNodes('question_embedding', 10, $embedding) 
            YIELD node as question, score
            MATCH (question)-[:HAS_ANSWER]->(answer:Answer)
            RETURN question.text AS question, answer.text AS answer, score
            ORDER BY score DESC
            LIMIT 5
        """, embedding=combined_embedding)
            
            return [dict(record) for record in result]

    def close(self):
        self.driver.close()