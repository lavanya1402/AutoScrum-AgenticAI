# prompts/prompt_loader.py
import os

def load_prompt(filename):
    prompt_dir = os.path.join(os.path.dirname(__file__), "")
    with open(os.path.join(prompt_dir, filename), encoding="utf-8") as f:
        return f.read()
