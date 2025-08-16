import os
from pathlib import Path
import subprocess

def escape_latex(text: str) -> str:
    replacements = {
        '//': r'/',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def latex_updater(state):
    latex_template_path = Path("overleaf_resume/main.tex")
    backup_path = latex_template_path.with_suffix(".bak.tex")

    # Backup original template
    if not backup_path.exists():
        latex_template_path.rename(backup_path)
    template_text = backup_path.read_text()

    # --- Experiences ---
    exp_tex = []
    for exp in state.get("selected_experiences", []):
        block = f"\\resumeSubheading\n" \
                f"  {{{escape_latex(exp.company)}}}{{{escape_latex(exp.location)}}}\n" \
                f"  {{{escape_latex(exp.title)}}}{{{escape_latex(exp.start_date)} -- {escape_latex(exp.end_date)}}}\n" \
                f"  \\resumeItemListStart\n"
        for item in exp.description:
            block += f"    \\resumeItem{{{escape_latex(item)}}}\n"
        block += "  \\resumeItemListEnd\n  \\vspace{2pt}\n"
        exp_tex.append(block)

    # --- Projects ---
    proj_tex = []
    for proj in state.get("selected_projects", []):
        skills_tex = ', '.join(map(escape_latex, proj.skills))
        block = f"\\resumeProjectHeading\n" \
                f"  {{\\textbf{{{escape_latex(proj.name)}}} $|$ \\emph{{{skills_tex}}}}}{{}}\n" \
                f"  \\resumeItemListStart\n"
        for item in proj.description:
            block += f"    \\resumeItem{{{escape_latex(item)}}}\n"
        block += "  \\resumeItemListEnd\n  \\vspace{-10pt}\n"
        proj_tex.append(block)

    # Replace placeholders
    updated_text = template_text
    updated_text = updated_text.replace("%<<EXPERIENCES>>%", "\n".join(exp_tex))
    updated_text = updated_text.replace("%<<PROJECTS>>%", "\n".join(proj_tex))

    latex_template_path.write_text(updated_text)
    print("LaTeX updated successfully!")

    # Optional: push to Overleaf
    overleaf_token = os.getenv("OVERLEAF_TOKEN")
    overleaf_project_id = os.getenv("OVERLEAF_PROJECT_ID")
    if overleaf_token and overleaf_project_id:
        repo_url = f"https://git:{overleaf_token}@git.overleaf.com/{overleaf_project_id}"
        try:
            subprocess.run(["git", "-C", str(latex_template_path.parent), "add", "."], check=True)
            subprocess.run(["git", "-C", str(latex_template_path.parent), "commit", "-m", "Update resume LaTeX automatically"], check=True)
            subprocess.run(["git", "-C", str(latex_template_path.parent), "push", repo_url, "master"], check=True)
            print("Pushed updates to Overleaf successfully!")
        except subprocess.CalledProcessError as e:
            print("Git push failed:", e)
    else:
        print("OVERLEAF_TOKEN or OVERLEAF_PROJECT_ID not set; skipping push.")

    return state
