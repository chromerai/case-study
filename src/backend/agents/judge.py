from typing import List, Dict, Any, Tuple
from ..utils.openai_client import get_openai_client

class judge_agent:
    def __init__(self):
        self.client = get_openai_client()
    
    def __call__(self, state) -> Dict[str, Any]:
        conversation = ' '.join(state["conversation_history"][-5:])
        generated_response = state["generated_response"][-1]

        prompt = f"""
        Review the following conversation and generated response:

        Conversation:
        {conversation}

        Generated Response:
        {generated_response}

        Evaluate if the response adequately addresses the user's query. If it does, respond with "APPROVED". 
        If not, then say "DISAPPROVED" and provide feedback on how the response can be improved..

        Your evaluation:
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )

        evaluation = response.choices[0].message.content
        if "APPROVED" in evaluation:
            state["final_response"] = generated_response
            state["next_step"].append("end")
        else:
            state["feedback"] = evaluation
            state["next_step"] = "central_agent"
            state["user_input"].append(f"Please improve the response. Feedback: {evaluation}")

        return state