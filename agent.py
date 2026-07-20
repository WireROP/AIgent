import os
import datetime
import json  # Import the json module

class SimpleAgent:
    def __init__(self, memory_file="agent_memory.json"):
        self.memory_file = memory_file
        self.memory = self.load_memory()  # Load memory from disk on startup
        self.tools = {
            "calculate": self.calculate,
            "read_file": self.read_file,
            "log": self.log_action
        }

    def load_memory(self):
        """Loads memory from a JSON file if it exists."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_memory(self):
        """Saves current memory to a JSON file."""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def log_action(self, action: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {action}"
        self.memory.append(entry)
        self.save_memory()  # Save every time we log something
        return entry

    def calculate(self, expression: str):
        try:
            result = eval(expression, {"__builtins__": None}, {})
            self.log_action(f"Calculated {expression} = {result}")
            return f"Result: {result}"
        except Exception:
            return "Error: Invalid math expression."

    def read_file(self, filename: str):
        try:
            with open(filename, 'r') as f:
                content = f.read()
                self.log_action(f"Read file: {filename}")
                return f"Content: {content}"
        except FileNotFoundError:
            return f"Error: File '{filename}' not found."

    def execute(self, user_input: str):
        inp = user_input.lower().strip()
        if "calculate" in inp or any(op in inp for op in ["+", "-", "*", "/"]):
            expr = inp.replace("calculate:", "").strip()
            return self.tools["calculate"](expr)
        elif "read" in inp:
            filename = inp.replace("read", "").strip()
            return self.tools["read_file"](filename)
        elif "history" in inp:
            return f"Agent Memory: {self.memory}"
        elif "hello" in inp or "hi" in inp:
            return "Agent: Hello! I'm ready. I remember our history!"
        else:
            return "Agent: I'm not sure what you mean."

# --- Interactive Mode ---
if __name__ == "__main__":
    agent = SimpleAgent()
    print("--- AI Agent Started (Type 'exit' to quit) ---")
    
    while True:
        user_in = input("\nYou: ")
        if user_in.lower() == "exit":
            print("Agent: Saving memory and shutting down...")
            break
        
        response = agent.execute(user_in)
        print(f"Agent: {response}")