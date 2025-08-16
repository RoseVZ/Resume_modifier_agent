from langgraph.graph import StateGraph, END
import json

# Import agents
from agents.jd_parser import run as jd_parser
from agents.resume_selector import run as resume_selector
from agents.ats_evaluator import run as ats_evaluator
from agents.refiner import run as refiner
from agents.latex_updater import latex_updater  # New node
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Build graph
graph = StateGraph(dict)

# Add nodes
graph.add_node("JD Parser", jd_parser)
graph.add_node("Resume Selector", resume_selector)
graph.add_node("ATS Evaluator", ats_evaluator)
graph.add_node("Refiner", refiner)
graph.add_node("LaTeX Updater", latex_updater)  # Add LaTeX node

# Set entry point
graph.set_entry_point("JD Parser")

# Standard edges
graph.add_edge("JD Parser", "Resume Selector")
graph.add_edge("Resume Selector", "ATS Evaluator")

MAX_RETRIES = 3  # Maximum number of refinement attempts

def ats_decision(state):
    retries = state.get("refine_attempts", 0)
    if retries < MAX_RETRIES and state.get("ats_score", 0) < 70:
        state["refine_attempts"] = retries + 1
        return "Refiner"  # Retry refinement
    return "LaTeX Updater"  # Proceed to LaTeX if max retries reached or score sufficient


graph.add_conditional_edges(
    "ATS Evaluator",
    ats_decision,
    {"Refiner": "Refiner", "LaTeX Updater": "LaTeX Updater"}
)


# Refiner always loops back to ATS Evaluator
graph.add_edge("Refiner", "ATS Evaluator")

# Compile graph
app = graph.compile()

if __name__ == "__main__":
    # Load inputs
    with open("resume.json") as f:
        resume = json.load(f)

    with open("jd.txt") as f:
        jd_text = f.read()

    state = {"resume": resume, "job_description": jd_text}

    # Invoke graph
    final_state = app.invoke(state)

    print("✅ LaTeX updated successfully and final state returned!")
