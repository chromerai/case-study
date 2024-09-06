from typing import Dict, Any, List
from neo4j import GraphDatabase
from ..config import config

class CompatibilityCheckerTool:
    def __init__(self):
        self.driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))

    def query_neo4j(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]

    def __call__(self, part: str, model: str) -> Dict[str, Any]:
        query = """
        MATCH (p:Part)
        WHERE p.ps_number = $part OR p.mfg_number = $part
        MATCH (p)-[:COMPATIBLE_WITH]->(m:Model {name: $model})
        RETURN COUNT(*) > 0 AS is_compatible
        """
        result = self.query_neo4j(query, {"part": part, "model": model})
        return {"is_compatible": result[0]["is_compatible"] if result else False}

    def __del__(self):
        self.driver.close()
    
    

