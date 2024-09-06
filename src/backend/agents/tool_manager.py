from typing import Dict, Any
from ..tools.inforetrieving import InfoRetrievalTool
from ..tools.symptomanalysis import SymptomAnalysisTool
from ..tools.compatibilitycheck import CompatibilityCheckerTool
from ..utils.openai_client import get_openai_client

class tool_manager:
    def __init__(self):
        self.info_retrieval_tool = InfoRetrievalTool()
        self.symptom_analysis_tool = SymptomAnalysisTool()
        self.compatibility_checker_tool = CompatibilityCheckerTool()
        self.client = get_openai_client()

    def __call__(self, state) -> Dict[str, Any]:
        conversation = ' '.join(state["conversation_history"][-5:])
        extracted_info = state["extracted_info"]
        prompt = f"""
        You are the tools manager for agentic architecture. Based on the following conversation, determine which tool(s) to use:
        {conversation}

        Available tools:
        1. Info Retrieval Tool: Use GraphRAG to get information about parts, models, and their relationships.
        2. Symptom Analysis Tool: Find the relevant parts that can fix the symptom provided the model. Also finds relevant Q&A to figure out the problem and solution.
        3. Compatibility Checker Tool: Check compatibility between parts and models.
        4. Part recommendations Tool: Recommend parts based on the user's query.

        Think step by step. 
        Select the most appropriate tool(s). Format your response as follows:
        Selected Tools: [1, 2, 3]
        Explanation: [Your explanation]
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )

        tool_selection = response.choices[0].message.content
        print("tool_manager tool_selection:", tool_selection)
        for line in tool_selection.split("\n"):
            if "Selected Tools:" in line:
                selected_tools = line.split(":")[1].strip().strip("[]").split(",")
            if "Explanation:" in line:
                state["tool_explanation"] = line.split(":")[1].strip()

        # Parse tool selection and use appropriate tools
        tool_outputs = {}

        if '1' in selected_tools:
            tool_outputs["info_retrieval"] = self.info_retrieval_tool(extracted_info)
        if '2' in selected_tools:
            model = extracted_info["model"]
            symptom = extracted_info["symptom"]
            if not model or not symptom:
                state['conversation_history'].append("Assistant: Model and symptom are required for symptom analysis")
            tool_outputs["symptom_analysis"] = self.symptom_analysis_tool(symptom, model)

        if '3' in selected_tools:
            part = extracted_info["ps_number"]
            if not part:
                part = extracted_info["mfg_number"]
            model = extracted_info["model"]
            if not part or not model:
                state['conversation_history'].append("Assistant: Part and model number are required for compatibility check")
            else:
                tool_outputs["compatibility_check"] = self.compatibility_checker_tool(part, model)

        if '4' in selected_tools:
            user_query = state["user_input"][-1]
            tool_outputs["part_recommendations"] = self.recommendation_tool.recommend(user_query)
            tool_outputs["part_recommendations"] = "Recommendations based on user query"

        state["tool_output"] = tool_outputs
        state["next_step"].append("response_generation")

        return state