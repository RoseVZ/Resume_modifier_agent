import gradio as gr
import json
from langgraph.graph import StateGraph
from agents.jd_parser import run as jd_parser
from agents.resume_selector import run as resume_selector
from agents.ats_evaluator import run as ats_evaluator
from agents.refiner import run as refiner
from agents.latex_updater import latex_updater
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
graph.add_node("LaTeX Updater", latex_updater)

# Set entry point
graph.set_entry_point("JD Parser")

# Standard edges
graph.add_edge("JD Parser", "Resume Selector")
graph.add_edge("Resume Selector", "ATS Evaluator")

MAX_RETRIES = 3

def ats_decision(state):
    retries = state.get("refine_attempts", 0)
    if retries < MAX_RETRIES and state.get("ats_score", 0) < 70:
        state["refine_attempts"] = retries + 1
        return "Refiner"
    return "LaTeX Updater"

graph.add_conditional_edges(
    "ATS Evaluator",
    ats_decision,
    {"Refiner": "Refiner", "LaTeX Updater": "LaTeX Updater"}
)

graph.add_edge("Refiner", "ATS Evaluator")

# Compile graph
app = graph.compile()

# Load a default resume
with open("resume.json") as f:
    default_resume = json.load(f)

# Gradio function
def run_pipeline(jd_text):
    state = {"resume": default_resume, "job_description": jd_text}
    final_state = app.invoke(state)
    # Pick relevant serializable fields
    result = {
        "ats_score": final_state.get("ats_score"),
        "latex": final_state.get("latex_update"),
        "git_status": final_state.get("git_status"),
    }
    return json.dumps(result, indent=2)


# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## Resume Tailoring and LaTeX Update Pipeline")
    jd_input = gr.Textbox(label="Job Description", lines=10, placeholder="Paste your job description here...")
    output = gr.Textbox(label="Final State", lines=20)
    run_btn = gr.Button("Run Pipeline")
    run_btn.click(run_pipeline, inputs=[jd_input], outputs=[output])

if __name__ == "__main__":
    demo.launch(share=True)
