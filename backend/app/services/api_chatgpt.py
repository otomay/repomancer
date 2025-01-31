from openai import OpenAI
import os

API_KEY = os.getenv("OPENAI_API_KEY", None)
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
API_PARAMS = os.getenv("OPENAI_API_PARAMS", None)

extra_params = {}

if API_PARAMS:
    API_PARAMS = API_PARAMS.split(",")
    for param in API_PARAMS:
        key, value = param.split('=')
        extra_params[key] = value
client = OpenAI(api_key=API_KEY, **extra_params)

def analyze_with_chatgpt(code: str, context: dict, structure: str) -> dict:
    prompt = f"Repository structure: {structure}\n\nRepository context: {context}\n\nCode to be analyzed:\n{code}\n\nCheck if there is any malicious code and explain your findings.\n\nIf there is malicious code, tag [MALICIOUS] at the beginning of the analysis, otherwise, tag [SAFE] at the beginning of the analysis."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a software security expert, and you will receive files in a loop from a GitHub repository to look for threats."},
            {"role": "system", "content": "You should analyze the following code and determine if it is safe or not, according to the user's instructions. Limit your comments to the context of the code. Do not give additional security tips if the code is considered safe."},
            {"role": "system", "content": "Malicious code includes: RAT, TROJAN, MINERS, SENDING INFORMATION TO UNKNOWN APIS OR SERVERS, OBFUSCATED CODE, ETC."},
            {"role": "system", "content": "DO NOT search for vulnerabilities in the code. Exposed private keys, variable names, and configuration files (.env, .conf, .json, .xml) SHOULD NOT be considered malicious code. THIS IS VERY IMPORTANT!"},
            {"role": "system", "content": 'If you need more context to analyze the current code (like functions that are in other files), reply only with the tag [MORE INFORMATION] followed by the names of the files you need separated by ";". I will provide you with the repository structure so you can get an idea of the directories and file names.'},
            {"role": "system", "content": "If you find malicious code, try to figure out specifically what it does. You can ask for more context by using the [MORE INFORMATION] tag I mentioned earlier. Try to be as specific as possible about why the code is considered malicious."},
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content

def generate_context_with_chatgpt(context: str) -> dict:
    prompt = f"Repository context: {context}\n\nGenerate a summary of the repository's purpose and content."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a specialist in generating descriptions and summaries of GitHub repositories."},
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content

def generate_final_conclusion(results: dict) -> dict:
    prompt = f"Complete analysis: {results}."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a software security expert, and you will receive a summary of a malicious analysis of a GitHub repository done by another agent. Summarize their report and generate conclusions about the reliability the user should have regarding the repository. If there is a malicious file, mention its path and the reason for the threat, but not the full path, starting from the repo name is enough."},
            {"role": "system", "content": "Not all files may be readable, as some repositories contain non-text files. I will provide you with the repository structure, and you should also evaluate it for files that cannot be read. If you notice that the repository contains .exe, .dll, and other types of executable files, consider it malicious."},
            {"role": "system", "content": "If the repository is safe, always remind the user to use virtual environments to test unfamiliar code, and to use good judgment when assessing the trustworthiness of a repository. Be cautious of repositories that seem too good to be true, repositories with many forks but few stars, and repositories without clear documentation, issues, or PRs."},
            {"role": "system", "content": "If there is malicious code, tag [MALICIOUS] at the beginning of the conclusion, otherwise, tag [SAFE] at the beginning of the conclusion."},
            {"role": "user", "content": prompt}
        ],
    )

    return {"results": response.choices[0].message.content}
