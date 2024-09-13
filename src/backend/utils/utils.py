from sentence_transformers import SentenceTransformer
from typing import List
from typing import Any, Dict
import tiktoken

def embed_text(text: str) -> List[float]:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    response = embedder.encode([text])
    return response.data[0].embedding

def format_conversation(conversation_history: List[Dict[str, str]]) -> str:
    formatted_conversation = []
    for message in conversation_history:
        role = message["role"].capitalize()
        content = message["content"]
        formatted_conversation.append(f"{role}: {content}")
    return "\n".join(formatted_conversation)

def count_tokens(messages: List[Dict[str, str]], model: str = "gpt-4o") -> int:
    """
    Count the number of tokens in a list of messages.

    Args:
    messages (List[Dict[str, str]]): A list of message dictionaries.
    model (str): The name of the model to use for encoding. Defaults to "gpt-4".

    Returns:
    int: The total number of tokens in the messages.
    """
    encoding = tiktoken.encoding_for_model(model)
    
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens -= 1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens