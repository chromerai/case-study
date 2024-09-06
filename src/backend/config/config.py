from dotenv import load_dotenv
import os
load_dotenv()

class config:
    NEO4J_URI = os.getenv('NEO4J_URI')
    NEO4J_USER = os.getenv('NEO4J_USER')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')