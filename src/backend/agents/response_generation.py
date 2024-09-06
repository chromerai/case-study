from typing import Dict, Any
from ..utils.openai_client import get_openai_client

class response_generation:
    def __init__(self):
        self.client = get_openai_client()

    def __call__(self, state) -> Dict[str, Any]:
        conversation = ' '.join(state["conversation_history"][-5:])
        tool_output = state["tool_output"]

        prompt = f"""
        Based on the following conversation and tool output, generate a helpful response for the user:

        Conversation:
        {conversation}

        Tool Output:
        {tool_output}

        One point of advice, sometimes user might express his frustration. In such cases, you can respond with empathy and understanding. For example, you can say: "I understand how frustrating it can be when your appliance is not working properly. I'm here to help you find a solution."

        If the user expresses gratitude, you can respond with: "You're welcome! I'm glad I could help. If you have any more questions, feel free to ask."

        Always maintain a polite and helpful tone in your responses.
        Provide a detailed and helpful response addressing the user's query:
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )
        print("response_generation response:", response.choices[0].message.content)
        state["generated_response"].append(response.choices[0].message.content)
        state["next_step"].append("judge_agent")
        return state