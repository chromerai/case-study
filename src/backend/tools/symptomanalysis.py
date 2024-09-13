from typing import Any, Dict, List
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from ..config import config

class SymptomAnalysisTool:
    def __init__(self):
        self.driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def __call__(self, extracted_info) -> Dict[str, Any]:
        parts = self._find_relevant_parts(extracted_info['model'], extracted_info['symptom'])
        relevant_qas = self._find_relevant_qas(parts, extracted_info['symptom'])
        return {
            "model": extracted_info['model'],
            "symptom": extracted_info['symptom'],
            "relevant_parts": parts,
            "relevant_qas": relevant_qas
        }

    def _find_relevant_parts(self, model: str, symptom: str) -> List[Dict[str, Any]]:
        print(" in find relevant parts")
        with self.driver.session() as session:
            return session.read_transaction(self._find_relevant_parts_tx, model, symptom)

    @staticmethod
    def _find_relevant_parts_tx(tx, model: str, symptom: str):
        result = tx.run("""
            MATCH (m:Model {name: $model})-[:HAS_ISSUE]->(s:Symptom)<-[:FIXES]-(p:Part)
            WHERE toLower(s.name) CONTAINS toLower($symptom)
            RETURN {
                name: p.name,
                ps_number: p.ps_number,
                description: p.description
            } AS parts
            LIMIT 2
        """, 
        model=model, symptom=symptom)

        records = list(result)

        if len(records) == 0:
            print("No records found. Checking if the Model and Symptom nodes exist:")
            model_check = tx.run("MATCH (m:Model {name: $model}) RETURN m", model=model)
            symptom_check = tx.run("MATCH (s:Symptom) WHERE toLower(s.name) CONTAINS toLower($symptom) RETURN s", symptom=symptom)
            print(f"Model node exists: {len(list(model_check)) > 0}")
            print(f"Matching Symptom nodes exist: {len(list(symptom_check)) > 0}")

        print(f"Number of records returned: {len(records)}")
        return [record['parts'] for record in records]

    def _find_relevant_qas(self, parts: List[Dict[str, Any]], symptom: str) -> List[Dict[str, Any]]:
        print(" in find relevant qas")
        if len(parts) == 0:
            return []
        combined_embedding = self.model.encode(symptom + " ".join([p['name'] + " " + p['ps_number'] for p in parts])).tolist()
        with self.driver.session() as session:
            return session.read_transaction(self._find_relevant_qas_tx, combined_embedding)

    @staticmethod
    def _find_relevant_qas_tx(tx, combined_embedding):
        result = tx.run("""
            CALL db.index.vector.queryNodes('question_embedding', 5, $embedding) 
            YIELD node as question, score
            MATCH (question)-[:HAS_ANSWER]->(answer:Answer)
            RETURN question.text AS question, answer.text AS answer, score
            ORDER BY score DESC
        """, embedding=combined_embedding)

        print("qa records: ", list(result))
        
        return [dict(record) for record in result]

    def close(self):
        self.driver.close()