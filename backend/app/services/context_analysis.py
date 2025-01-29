import os
from app.services.api_chatgpt import generate_context_with_chatgpt

def analyze_context(repo_path: str) -> dict:
    context = {}

    readme_path = os.path.join(repo_path, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as file:
            context["readme"] = file.read()

    context = generate_context_with_chatgpt(context)
    return context