import os
from typing import Any, Dict
from neo4j import GraphDatabase
from ..config import config

class InfoRetrievalTool:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri=config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))

    def __call__(self, extracted_info: Dict[str, str]) -> Dict[str, Any]:
        with self.driver.session() as session:
            return session.read_transaction(self._get_part_info, extracted_info)

    def _get_part_info(self, tx, extracted_info: Dict[str, str]) -> Dict[str, Any]:
        query = """
        MATCH (p:Part)
    WHERE 
    ($ps_number <> '' AND p.ps_number = $ps_number) OR
    ($mfg_number <> '' AND p.mfg_number = $mfg_number)

OPTIONAL MATCH (p)-[:COMPATIBLE_WITH]->(m:Model)
WHERE $model_number = '' OR m.number = $model_number

OPTIONAL MATCH (p)-[:FIXES]->(s:Symptom)
WHERE $symptom = '' OR s.name = $symptom

WITH p, 
     CASE WHEN $model_number <> '' AND $symptom <> '' 
          THEN collect(DISTINCT m) ELSE [] END as models,
     CASE WHEN $model_number <> '' AND $symptom <> '' 
          THEN collect(DISTINCT s) ELSE [] END as symptoms

RETURN {
    name: p.name,
    description: p.description,
    ps_number: p.ps_number,
    mfg_number: p.mfg_number,
    models: CASE WHEN $model_number <> '' AND $symptom <> '' 
                 THEN [m IN models | m.number] ELSE [] END,
    symptoms_fixed: CASE WHEN $model_number <> '' AND $symptom <> '' 
                         THEN [s IN symptoms | s.name] ELSE [] END,
    part_url: p.url
} as part_info
        """
        
        result = tx.run(query, 
                        ps_number=extracted_info.get('ps_number', ''),
                        model_number=extracted_info.get('model', ''),
                        mfg_number=extracted_info.get('mfg_number', ''),
                        symptom=extracted_info.get('symptom', ''))
        
        records = list(result)
        if not records:
            return {"message": "No matching part found."}
        
        return records[0]['part_info']

    def close(self):
        self.driver.close()