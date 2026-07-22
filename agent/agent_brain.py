import json
import os
import subprocess
from duckduckgo_search import DDGS

class HybridAgent:
    def __init__(self, mind_file="mind.json"):
        self.mind_file = mind_file
        self.memory = self.load_mind()
        self.ddg = DDGS()
        # Path to your compiled Rust executable
        self.rust_binary = "./target/release/agent_engine.exe"

    def load_mind(self):
        if os.path.exists(self.mind_file):
            with open(self.mind_file, "r") as f:
                return json.load(f)
        return {"facts": {}, "history": []}

    def save_mind(self):
        with open(self.mind_file, "w") as f:
            json.dump(self.memory, f, indent=4)

    def call_rust_engine(self, operation: str, payload: str):
        """Executes the compiled Rust binary via system shell command."""
        if not os.path.exists(self.rust_binary):
            return "⚠️ Rust binary not found! Run 'cargo build --release' first."
        
        try:
            cmd = [self.rust_binary, operation, payload]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Rust Execution Error: {e.stderr.strip()}"
        except Exception as ex:
            return f"Failed to bridge with Rust: {str(ex)}"

    def execute(self, user_input: str):
        inp = user_input.strip()
        lower_inp = inp.lower()

        if lower_inp.startswith("rust "):
            # Example: rust secure_eval 45
            parts = inp.split(" ", 2)
            if len(parts) >= 3:
                op, payload = parts[1], parts[2]
                return self.call_rust_engine(op, payload)
            return "Usage: rust [operation] [payload]"

        elif lower_inp.startswith("search "):
            query = inp.split(" ", 1)[1]
            results = list(self.ddg.text(query, max_results=1))
            return results[0]['body'] if results else "No data found."

        elif lower_inp.startswith("learn "):
            _, key, val = inp.split(" ", 2)
            self.memory["facts"][key] = val
            self.save_mind()
            return f"Learned fact: {key} -> {val}"

        if lower_inp in self.memory["facts"]:
            return f"Memory: {self.memory['facts'][lower_inp]}"

        return "Commands: search [query], learn [key] [val], rust [op] [payload]"

if __name__ == "__main__":
    agent = HybridAgent()
    print("--- Hybrid Python + Rust Agent Active ---")
    while True:
        ui = input("\nAgent > ")
        if ui.lower() == "exit":
            break
        print(agent.execute(ui))