from langchain_openai import ChatOpenAI
import os
import json
import re
import copy
from pydantic import BaseModel, parse_obj_as
from typing import List, Dict


class Experience(BaseModel):
    title: str
    company: str
    location: str
    start_date: str 
    end_date: str 
    skills: List[str]
    description: List[str] 

class Project(BaseModel):
    name: str
    skills: List[str]
    description: List[str]  


def run(state: Dict) -> Dict:
    resume = state.get("resume", {})
    jd_keywords = state.get("jd_keywords", [])

    # Make sure API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")

    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0.3)

    # Fresh copy to avoid mutating state
    resume_copy = copy.deepcopy(resume)

    # ---------------- Prompt ----------------
    prompt = f"""
You are an expert career assistant.

Task: From the provided master resume, select the **four work experiences** and **up to three projects** most relevant to the given job keywords.
Do not include anything that is not in the master resume. Stick strictly to the facts.

For each experience, return an object with:
- title
- company
- location
- start_date
- end_date
- skills
- description (rephrase using Context + Action + Result to maximize impact) Two to three bullet points per experience
Be truthful to the original content, but enhance clarity and impact.


For each project, Order them according to relevance to the job description and return an object with:
- name
- skills
- description (rephrase using Context + Action + Result to maximize impact), one to two bullet points per project.
Remember for both experiences and projects descriptions:
wrap the keywords in \\textbf{{}} (with a leading backslash) to make them bold in the LaTeX output. For keywords in Paranthesis only wrap the text inside(not the '(' or ')')
- Escape all LaTeX symbols like \\%, &, #, $, _,  with a backslash.

Return ONLY a JSON object with two keys: 
- "experiences": [array of experiences]
- "projects": [array of projects]

Do NOT include explanations, greetings, or extra text.

Job Keywords: {jd_keywords}
Master Resume: {json.dumps(resume_copy, indent=2)}
"""

    response = llm.invoke(prompt)

    # ---------------- Clean response ----------------
    response_text = response.content.strip()
    response_text = re.sub(r"^```json|```$", "", response_text).strip()
    response_text = response_text.replace("\\", "\\\\")

    try:
        # Parse JSON from LLM
        llm_output = json.loads(response_text)

        # Validate and structure using Pydantic
        validated_experiences = parse_obj_as(List[Experience], llm_output.get("experiences", []))
        validated_projects = parse_obj_as(List[Project], llm_output.get("projects", []))

    except Exception as e:
        print("LLM JSON parsing/validation failed:", e)

        # Fallback with Pydantic enforcement
        validated_experiences = [
            Experience(**exp)
            for exp in resume_copy.get("work_experiences", [])
            if any(kw.lower() in " ".join(exp.get("skills", [])).lower() for kw in jd_keywords)
        ]

        validated_projects = [
            Project(**proj)
            for proj in resume_copy.get("projects", [])
            if any(kw.lower() in " ".join(proj.get("skills", [])).lower() for kw in jd_keywords)
        ]


    # print(f"Selected {len(validated_experiences)} experiences and {len(validated_projects)} projects.")
    # print("Experiences:", validated_experiences)
    # print("Projects:", validated_projects)
    state["selected_experiences"] = validated_experiences
    state["selected_projects"] = validated_projects

    return state
