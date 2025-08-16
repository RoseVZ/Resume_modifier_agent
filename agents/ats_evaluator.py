from langchain_openai import ChatOpenAI
import os
from pydantic import BaseModel
from typing import List

def run(state):
    # Ensure API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")

    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0)

    # Define Pydantic models
    class Experience(BaseModel):
        title: str
        company: str
        skills: List[str]
        description: List[str]

    class Project(BaseModel):
        name: str
        skills: List[str]
        description: List[str]

    # Load experiences and projects
    selected_exp = [
        Experience(**exp) if isinstance(exp, dict) else exp
        for exp in state.get("selected_experiences", [])
    ]
    selected_proj = [
        Project(**proj) if isinstance(proj, dict) else proj
        for proj in state.get("selected_projects", [])
    ]

    jd_text = state.get("job_description", "")

    # Build prompt
    prompt = f"""
You are a recruiter reviewing a candidate's experiences and projects.
Here is the job description:
{jd_text}

Selected experiences:
"""
    for exp in selected_exp:
        prompt += f"- {exp.title} at {exp.company}, Skills: {', '.join(exp.skills)}\n"
        for d in exp.description:
            prompt += f"  * {d}\n"

    prompt += "\nSelected projects:\n"
    for proj in selected_proj:
        prompt += f"- {proj.name}, Skills: {', '.join(proj.skills)}\n"
        for d in proj.description:
            prompt += f"  * {d}\n"

    prompt += """
Rate how well these experiences and projects match the job description on a scale from 0 to 100.
Even if not all keywords match, if the experience/project is relevant or impactful, give at least 50.
Return ONLY the number. Act like a strict ATS system, who is stingy with scores. 
Try to be as strict as possible, but also fair.
"""

    # Call LLM
    response = llm.invoke(prompt)

    # Clean response and convert to integer
    try:
        score = int(response.content.strip())
    except:
        score = 70  # default minimum if LLM returns invalid output

    print(f"ATS Score: {score}")
    state["ats_score"] = score
    return state
