from typing import Any, Dict, List
import json
from ..utils.openai_client import get_openai_client
from ..utils.utils import count_tokens
import tiktoken

class central_agent:
    def __init__(self):
        self.client = get_openai_client()
        self.encoding = tiktoken.encoding_for_model("gpt-4o")

    def __call__(self, state) -> Dict[str, Any]:
        if "conversation_history" not in state:
            state["conversation_history"] = []

        user_input = state["user_input"][-1]
        state["conversation_history"].append({"role": "user", "content": user_input})

        prompt = f"""
        You are a helpful assistant for the refrigerator and dishwasher appliances/parts of PartSelect: an e-commerce website. 
        ** Important: Any type of questions related to other appliances should be politely declined! **
        Your task is to gather all necessary information from the user to assist them effectively.
        If the user hasn't provided enough information, ask follow-up questions. For example, you can ask: 
        "What is the model number of your appliance?" or mfg number of the part you are looking for?"

        However, it is also possible that user might be looking for only some general information about a part. So, based on your judgement decide if you need more information or if you can proceed to use tools.

        Sometimes, user will just ask for some part recommendations! by providing a use case or just simply give you a product information. In that case, you can directly proceed to tools.

        Thinks step by step and decide if you need more information or if you can proceed to tools.
        
        After you have all the information, extract the following details based on the query asked by the user, conversation history, and additional information provided:
        - mfg number of the part ( if applicable )
        - Part Select number ( PS number ) of the part ( if applicable )
        - model number of the appliance( if applicable )
        - symptom or issue with the appliance ( if applicable)

        **CRITICAL: Your entire response content must only be a single JSON object. The JSON structure must be as follows:**
        {{
            "response": "Your response text",
            "proceed_to_tools": true/false,
            "extracted_info": {{
                "model": "extracted model number or null",
                "ps_number": "extracted part number or null",
                "mfg_number": "extracted manufacturer number or null",
                "symptom": "extracted symptom/issue or null"
            }}
        }}

        Notes:
        - Any "response" text must always be within the JSON object in the response key.
        - Do not provide any text before or after the JSON object.
        - Set the value of "proceed_to_tools" to true if you can proceed to tools, false if you need more information.
        - model will always be for an appliance referring to the model number of the appliance.
        - ps_number will always start with 'PS' followed by a some digits; ps_number is the PartSelect number of the part
        - mfg_number is the manufacturer number of the part
        - If the information is not available or not applicable, set the value to null.
        - Ensure that your response is in VALID JSON format as given above. Do not output any markdown or enclose the JSON in triple backticks.
        

        Your response:
        """

        messages = [
            {"role": "system", "content": prompt},
            *self.get_conversation_history(state["conversation_history"])
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        token_count = count_tokens(messages)
        print(f"Total tokens in messages: {token_count}")
        ai_response = response.choices[0].message.content
        print(f"response: `{response}`")
        print("AI response:", ai_response)
        parsed_response = json.loads(ai_response)
        state["conversation_history"].append({"role": "assistant", "content": parsed_response['response']})
        

        if parsed_response["proceed_to_tools"]:
            state["next_step"].append("tool_manager")
            state['extracted_info'] = parsed_response["extracted_info"]
            state['generated_response'].append(" Got it! Let me gather the information for you.")
        else:
            state["next_step"].append("central_agent")
            state['generated_response'].append(parsed_response['response'])

            #for debugging purposes
            print("Central agent response:", parsed_response['response'])
        
        return state

    def get_conversation_history(self, conversation_history: List[Dict[str, str]], max_tokens: int = 2000) -> List[Dict[str, str]]:
        recent_history = []
        total_tokens = 0
        
        for message in reversed(conversation_history):
            message_tokens = len(self.encoding.encode(message['content']))
            if total_tokens + message_tokens > max_tokens:
                return recent_history
            recent_history.insert(0, message)
            total_tokens += message_tokens
        
        return recent_history
