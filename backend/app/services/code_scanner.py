import os
from app.services.api_chatgpt import analyze_with_chatgpt, generate_final_conclusion
import shutil

async def scan_code(repo_path: str, context: dict, progress_callback=None) -> list:
    results = []
    total_files = sum(
        len(files)
        for root, _, files in os.walk(repo_path)
        if ".git" not in root
    )
    processed_files = 0

    code_store = {}
    repo_structure = ""
    for root, _, files in os.walk(repo_path):
        if ".git" in root:
            continue
        level = root.replace(repo_path, '').count(os.sep)
        indent = ' ' * 4 * level
        repo_structure += f"{indent}{os.path.basename(root)}/\n"
        for file in files:
            file_path = os.path.join(root, file)
            file_indent = ' ' * 4 * (level + 1)
            repo_structure += f"{file_indent}{file}\n"
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                    code_store[file_path] = code
            except Exception as e:
                continue

    for root, _, files in os.walk(repo_path):
        if ".git" in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            try:
                code = code_store.get(file_path)
                if code:
                    while True:
                        analysis = analyze_with_chatgpt(code, context, repo_structure)
                        if '[MORE INFORMATION]' in analysis:
                            analysis = analysis.replace('[MORE INFORMATION]', '').strip()
                            additional_info_files = analysis.split(';')
                            for file_name in additional_info_files:
                                additional_code = find_file_code_store(file_name, code_store)
                                if additional_code:
                                    code += f"\n# Code from file {file_name}:\n{additional_code}\n"
                        else:
                            break
                    results.append({"file": file_path, "analysis": analysis})

            except Exception as e:
                pass

            processed_files += 1
            if progress_callback:
                await progress_callback(processed_files / total_files * 100)

    conclusion = generate_final_conclusion(results)
    try:
        shutil.rmtree(repo_path)
    except: pass
    return conclusion

def find_file_code_store(file_name: str, code_store: dict) -> str:
    for file, code in code_store.items():
        if file_name in file:
            return code
    return ""
