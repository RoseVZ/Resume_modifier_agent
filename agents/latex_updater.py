import os
from pathlib import Path
import subprocess

def latex_updater(state):
    """
    Updates the LaTeX resume with selected experiences and projects,
    then pushes the changes to Overleaf via Git.
    """
    # 1️⃣ Paths
    latex_template_path = Path("overleaf_resume/main.tex")  # Path to your Overleaf repo LaTeX file
    backup_path = latex_template_path.with_suffix(".bak.tex")

    # Backup original template
    if not backup_path.exists():
        latex_template_path.rename(backup_path)
    template_text = backup_path.read_text()

    # 2️⃣ Generate LaTeX blocks for experiences
    exp_latex_list = []
    for exp in state.get("selected_experiences", []):
        exp_block = f"""\\resumeSubheading
  {{{exp.title}}}{{{exp.company}, {exp.location}}}
  {{{exp.title}}}{{{exp.start_date} -- {exp.end_date}}}
  \\resumeItemListStart
"""
        for item in exp.description:
            exp_block += f"    \\resumeItem{{{item}}}\n"
        exp_block += "  \\resumeItemListEnd\n  \\vspace{{2pt}}\n"
        exp_latex_list.append(exp_block)
    experiences_tex = "\n".join(exp_latex_list)

    # 3️⃣ Generate LaTeX blocks for projects
    proj_latex_list = []
    for proj in state.get("selected_projects", []):
        proj_block = f"""\\resumeProjectHeading
  {{\\textbf{{{proj.name}}} $|$ \\emph{{{', '.join(proj.skills)}}}}}{{}}
  \\resumeItemListStart
"""
        for item in proj.description:
            proj_block += f"    \\resumeItem{{{item}}}\n"
        proj_block += "  \\resumeItemListEnd\n  \\vspace{{-10pt}}\n"
        proj_latex_list.append(proj_block)
    projects_tex = "\n".join(proj_latex_list)

    # 4️⃣ Replace placeholders in LaTeX template
    # Use special markers in your template like: %<<EXPERIENCES>>% and %<<PROJECTS>>%
    updated_text = template_text
    updated_text = updated_text.replace("%<<EXPERIENCES>>%", experiences_tex)
    updated_text = updated_text.replace("%<<PROJECTS>>%", projects_tex)

    # 5️⃣ Write updated LaTeX back
    latex_template_path.write_text(updated_text)
    print("LaTeX updated successfully!")

    # 6️⃣ Optional: Push to Overleaf via Git
    overleaf_token = os.getenv("OVERLEAF_TOKEN")
    overleaf_project_id = os.getenv("OVERLEAF_PROJECT_ID")
    if overleaf_token and overleaf_project_id:
        repo_url = f"https://git:{overleaf_token}@git.overleaf.com/{overleaf_project_id}"
        try:
            subprocess.run(["git", "-C", str(latex_template_path.parent), "add", "."], check=True)
            subprocess.run(["git", "-C", str(latex_template_path.parent), "commit", "-m", "Update resume LaTeX automatically"], check=True)
            subprocess.run(["git", "-C", str(latex_template_path.parent), "push", repo_url, "main"], check=True)
            print("Pushed updates to Overleaf successfully!")
        except subprocess.CalledProcessError as e:
            print("Git push failed:", e)
    else:
        print("OVERLEAF_TOKEN or OVERLEAF_PROJECT_ID not set; skipping push.")

    return state
