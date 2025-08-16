
from langgraph.graph import StateGraph, END
import json

# Import agents
from agents.jd_parser import run as jd_parser
from agents.resume_selector import run as resume_selector
from agents.ats_evaluator import run as ats_evaluator
from agents.refiner import run as refiner
from agents.latex_updater import latex_updater
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
# import os
# print("OPENAI_API_KEY loaded?", os.getenv("OPENAI_API_KEY") is not None)

# Build graph
graph = StateGraph(dict)

graph.add_node("JD Parser", jd_parser)
graph.add_node("Resume Selector", resume_selector)
graph.add_node("ATS Evaluator", ats_evaluator)
graph.add_node("Refiner", refiner)

graph.set_entry_point("JD Parser")
graph.add_edge("JD Parser", "Resume Selector")
graph.add_edge("Resume Selector", "ATS Evaluator")

# ATS Evaluator branching logic
def ats_decision(state):
    retries = state.get("refine_attempts", 0)
    if state.get("ats_score", 0) < 70 and retries < 3:
        state["refine_attempts"] = retries + 1
        return "Refiner"
    return END

graph.add_conditional_edges(
    "ATS Evaluator",
    ats_decision,
    {"Refiner": "Refiner", END: END}
)

# Refiner always loops back to ATS Evaluator
graph.add_edge("Refiner", "ATS Evaluator")

app = graph.compile()

if __name__ == "__main__":
    with open("resume.json") as f:
        resume = json.load(f)

    with open("jd.txt") as f:
        jd_text = f.read()
    job_description = jd_text
    state = {"resume": resume, "job_description": job_description}

    final_state = app.invoke(state)
    # print("Final State:", final_state)
