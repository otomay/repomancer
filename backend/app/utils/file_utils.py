import os

def list_code_files(repo_path: str, extensions=(".py", ".js", ".java")) -> list:
    code_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(extensions):
                code_files.append(os.path.join(root, file))
    return code_files