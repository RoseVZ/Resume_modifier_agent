from langchain_openai import ChatOpenAI
import os
import json

def run(state):
    jd_text = state["job_description"]

    # Make sure API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")

    llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0.1)

    # Prompt the LLM to extract key skills and requirements
    prompt = f"""
    Pick out technical phrases that are likely keywords for an ATS system from the following job description.
    List them as a JSON array of lowercase words/phrases, without any explanation. 
    Return ONLY a JSON array of strings. Do not include explanations, greetings, or markdown formatting.
    Do not pick non-technical skills like "communication" or "team player" or irrelevant buzzwords.
    Job Description:
    {jd_text}
    """

    # Call the LLM
    response = llm.invoke(prompt)

    try:
        # Parse JSON output from the model
        keywords = json.loads(response.content)
    except:
        # fallback: split by space if JSON parsing fails
        keywords = [word.lower() for word in jd_text.split() if len(word) > 3]

    state["jd_keywords"] = keywords

    return state
