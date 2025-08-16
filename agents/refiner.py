from langchain_openai import ChatOpenAI

def run(state):
    jd_keywords = state.get("jd_keywords", [])
    selected_experiences = state.get("selected_experiences", [])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    refined = []
    for exp in selected_experiences:
        bullets = "\n".join(exp.description)
        prompt = f"""
You are a resume expert. 
Rewrite the following bullet points so they naturally include the job keywords.
Use Context + Action + Result format. 
Preserve truth. Keep each bullet separate.
wrap the keywords in \\textbf{{}} to make them bold in the LaTeX output. and always put a \\ before symbols like \\%
Job keywords: {jd_keywords}

Bullets:
{bullets}

Return ONLY a JSON array of strings representing the refined bullet points.
"""
        response = llm.invoke(prompt)
        # Strip markdown and parse JSON
        import json, re
        text = re.sub(r"^```json|```$", "", response.content.strip())
        try:
            refined_bullets = json.loads(text)
        except:
            refined_bullets = exp.description  # fallback
        exp.description = refined_bullets
        refined.append(exp)
    print(f"Refined {len(refined)} experiences with updated descriptions.")

    state["selected_experiences"] = refined
    state["refined"] = True
    return state
