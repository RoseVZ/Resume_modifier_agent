def run(state):
    from pydantic import BaseModel
    from typing import List

    class Experience(BaseModel):
        title: str
        company: str
        skills: List[str]
        description: List[str]

    selected = [
        Experience(**exp) if isinstance(exp, dict) else exp
        for exp in state.get("selected_experiences", [])
    ]
    jd_keywords = state.get("jd_keywords", [])

    # Join all description bullets into one string
    text = " ".join(" ".join(point for point in exp.description) for exp in selected)

    match_count = sum(1 for kw in jd_keywords if kw.lower() in text.lower())
    score = (match_count / len(jd_keywords)) * 100 if jd_keywords else 0

    state["ats_score"] = round(score, 2)
    return state
