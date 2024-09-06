import json
import hashlib
from neo4j import GraphDatabase
from typing import List
from sentence_transformers import SentenceTransformer

def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()

def determine_appliance_type(category):
    if 'refrigerator' in category.lower():
        return 'Refrigerator'
    elif 'dishwasher' in category.lower():
        return 'Dishwasher'
    else:
        return 'Unknown'

class Neo4jLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def close(self):
        self.driver.close()

    def load_data(self, parts_data):
        with self.driver.session() as session:
            for part_data in parts_data:
                session.write_transaction(self._create_and_return_graph, part_data)
            session.write_transaction(self._create_vector_index)

    def _create_and_return_graph(self, tx, data):
        appliance_type = determine_appliance_type(data['category'])
        
        # Generate embedding for the part
        embedding_text = f"{data['ps_number']}{data['name']} {data['mfg_number']}{data['description']}"
        embedding = self.model.encode(embedding_text).tolist()

        # Create Part node with embedding
        tx.run("""
            CREATE (p:Part {name: $name, ps_number: $ps_number, description: $description, mfg_number: $mfg_number, url: $product_url, appliance_type: $appliance_type, embedding: $embedding})
            SET p.embedding_size = size(p.embedding)
            SET p.embedding_q_size = size(p.embedding_q)
        """, name=data['name'], ps_number=data['ps_number'], description=data['description'], mfg_number=data['mfg_number'], product_url=data['product_url'], appliance_type=appliance_type, embedding=embedding)

        # Create Model and Brand nodes, and relationships
        for model_data in data['compatible_models']:
            tx.run("""
                MATCH (p:Part {name: $part_name})
                MERGE (b:Brand {name: $brand})
                MERGE (m:Model {name: $model, appliance_type: $appliance_type})
                MERGE (m)-[:BELONGS_TO]->(b)
                MERGE (p)-[:COMPATIBLE_WITH]->(m)
            """, part_name=data['name'], brand=model_data['Brand'], 
                 model=model_data['Model'], appliance_type=appliance_type)
            
        # Create Symptom nodes and relationships
        for symptom in data['Symptoms fixed']:
            tx.run("""
                MATCH (p:Part {name: $part_name})
                MERGE (s:Symptom {name: $symptom})
                MERGE (p)-[:FIXES]->(s)
                WITH p, s
                MATCH (p)-[:COMPATIBLE_WITH]->(m: Model)
                MERGE (m)-[:HAS_ISSUE]->(s)
            """, part_name=data['name'], symptom=symptom)

        # Create QnA nodes and relationships
        for qa in data['qna_list']:
            question_id = f"Q_{generate_id(qa['question'])}"
            answer_id = f"A_{generate_id(qa['answer'])}"
            embedding_q = self.model.encode(qa['question']).tolist()
            tx.run("""
                MATCH (p:Part {name: $part_name})
                CREATE (q:Question {id: $question_id, text: $question, embedding_q: $embedding_q})
                CREATE (a:Answer {id: $answer_id, text: $answer})
                CREATE (q)-[:HAS_ANSWER]->(a)
                CREATE (p)-[:HAS_QUESTION]->(q)
            """, part_name=data['name'], question_id=question_id, question=qa['question'],
                 answer_id=answer_id, answer=qa['answer'], embedding_q=embedding_q)

    @staticmethod
    def _create_vector_index(tx):
        query = (
            "CALL db.index.vector.createNodeIndex("
            "   'part_embeddings',"
            "   'Part',"
            "   'embedding',"
            "   384,"  # all-MiniLM-L6-v2 produces 384-dimensional embeddings
            "   'cosine'"
            ")"
        )
        tx.run(query)

        query = (
            "CALL db.index.vector.createNodeIndex("
            "   'question_embedding',"
            "   'Question',"
            "   'embedding_qs',"
            "   384,"  # all-MiniLM-L6-v2 produces 384-dimensional embeddings
            "   'cosine'"
            ")"
        )
        tx.run(query)