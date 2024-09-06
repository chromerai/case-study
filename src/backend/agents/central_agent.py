from typing import Any, Dict
import json
from ..utils.openai_client import get_openai_client

class central_agent:
    def __init__(self):
        self.client = get_openai_client()

    def __call__(self, state) -> Dict[str, Any]:
        if "conversation_history" not in state:
            state["conversation_history"] = []

        user_input = state["user_input"][-1]
        state["conversation_history"].append(f"User: {user_input}")

        prompt = f"""
        You are a helpful assistant for the refrigerator and dishwasher appliances/parts of PartSelect: an e-commerce website. 
        ** Important: Any type of questions related to other appliances should be politely declined! **
        Your task is to gather all necessary information from the user to assist them effectively.
        If the user hasn't provided enough information, ask follow-up questions. For example, you can ask: 
        "What is the model number of your appliance?" or mfg number of the part you are looking for?"

        However, it is also possible that user might be looking for only some general information about a part. So, based on your judgement decide if you need more information or if you can proceed to use tools.

        Sometimes, user will just ask for some part recommendations! by providing a use case or just simply give you a product information. In that case, you can directly proceed to tools.
        Below is the conversation history to give you context:

        Conversation history:
        {' '.join(state["conversation_history"][-5:])}

        Thinks step by step and decide if you need more information or if you can proceed to use tools.
        If you need more information, ask a question. If you have enough information, say "PROCEED TO TOOLS".
        
        Finally, after you have all the information, extract the following details based on the query asked by the user and additional information provided:
        - mfg number of the part ( if applicable )
        - Part Select number ( PS number ) of the part ( if applicable )
        - model number of the appliance( if applicable )
        - symptom or issue with the appliance ( if applicable)

        Provide your response in a VALID JSON format with the following structure:
        {{
            "response": "Your response text",
            "proceed_to_tools": true/false, # true if you can proceed to tools, false if you need more information. 
            "extracted_info": {{
                "model": "extracted model number or null", # model will always be for an appliance referring to the model number of the appliance
                "ps_number": "extracted part number or null. # ps_number will always start with 'PS' followed by a some numbers", # ps_number is the PartSelect number of the part
                "mfg_number": "extracted manufacturer number or null", # mfg_number is the manufacturer number of the part
                "symptom": "extracted symptom/issue or null"
            }}
        }}
        Ensure that your response is in VALID JSON format. Do not output any markdown or enclose the JSON in triple backticks.
        Your response:
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )

        ai_response = response.choices[0].message.content
        parsed_response = json.loads(ai_response)
        state["conversation_history"].append(f"Assistant: {parsed_response['response']}")
        

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