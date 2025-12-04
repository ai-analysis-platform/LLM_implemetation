
import pandas as pd
import os
from google.genai import Client  # pip install google-genai, 예시 import
from typing import Optional
from typing import Dict, List, Any
import os
import json
from app.utils import load_yaml_prompt
from schemas.state_schema import GraphState
import re
genai_client = Client(api_key="")


def build_rq_agent_prompt(data: Dict[str, Any]) -> str:
    industry = data.get("industry")
    report_type = data.get("report_type")

    yaml_path = "prompts/rq_prompts.yaml"
    rq_yaml = load_yaml_prompt(yaml_path)

    prompt_template = rq_yaml[industry][report_type]
    rq_prompt=prompt_template.format(companyName={data.get('companyName')},
        industry={data.get('industry')},
        reportingPeriod={data.get('reportingPeriod')},
        report_type={data.get('report_type')}, 
        user_request={data.get('additionalRequests', 'None')})

    return rq_prompt 

def rq_agent_node(state: GraphState) -> GraphState:
    data = state["input_data"]
    prompt = build_rq_agent_prompt(data)
    raw_response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
    try:
        text_response = raw_response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError):
        raise ValueError("RQ Agent returned empty or invalid output")

    # 2️⃣ Markdown 코드 블록 제거
    cleaned_text = re.sub(r"^```json\s*|\s*```$", "", text_response.strip(), flags=re.MULTILINE)

    # 3️⃣ JSON 문자열 파싱
    try:
        rq_list = json.loads(cleaned_text)
    except json.JSONDecodeError:
        raise ValueError(f"RQ Agent output is not valid JSON:\n{cleaned_text}")

    return rq_list