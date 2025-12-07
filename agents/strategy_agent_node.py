

import pandas as pd
import os
from google.genai import Client  # pip install google-genai, 예시 import
from typing import Optional
from typing import Dict, List, Any
import os
import json
from app.utils import load_yaml_prompt,genai_client
from schemas.state_schema import GraphState
import re
from app.utils import load_yaml_prompt

def build_strategy_agent_prompt(rq_list: List[Dict[str, Any]], data: Dict[str, Any] ) -> str:
    
    research_questions_json = rq_list
    internal_data_list=data.get('internal_data_list')
    yaml_path = "prompts/strategy_prompts.yaml"
    st_yaml = load_yaml_prompt(yaml_path)

    prompt_template = st_yaml['strategy_prompt']
    st_prompt=prompt_template.format(research_questions_json=research_questions_json, internal_data_list=internal_data_list)

    return st_prompt 


def strategy_agent_node(state: GraphState) -> GraphState:
    rq_list = state["research_questions"]
    input_data = state["input_data"]

    prompt = build_strategy_agent_prompt(
        rq_list=rq_list, data = input_data
    )

    raw_response = genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    try:
        text_response = raw_response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError):
        raise ValueError("Strategy Agent returned empty output")

    cleaned_text = re.sub(r"^```json\s*|\s*```$", "", text_response.strip(), flags=re.MULTILINE)

    try:
        strategy_result = json.loads(cleaned_text)
    except json.JSONDecodeError:
        raise ValueError(f"Strategy Agent output is not valid JSON:\n{cleaned_text}")
    
    print(strategy_result)
    return {
        **state,
        "strategy_result": strategy_result
    }