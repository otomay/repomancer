import subprocess
import os
import tempfile
import shutil


def clone_repository(repo_url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(temp_dir, repo_name)

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    subprocess.run(["git", "clone", repo_url, repo_path], check=True)
    return repo_path