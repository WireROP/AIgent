import os

class SimpleAgent:
    def __init__(self):
        # Tools are organized here. 
        # Future Rust modules will be called from here.
        self.tools = {
            "calculate": self.calculate,
            "read_file": self.read_file
        }

    def calculate(self, expression: str):
        """Tool: Performs math calculations."""
        try:
            # Safely evaluate simple math
            result = eval(expression, {"__builtins__": None}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: Could not calculate '{expression}'. {e}"

    def read_file(self, filename: str):
        """Tool: Reads text from a file."""
        try:
            with open(filename, 'r') as f:
                return f"Content: {f.read()}"
        except FileNotFoundError:
            return f"Error: File '{filename}' not found."

    def execute(self, user_input: str):
        """The core Agent Loop."""
        print(f"\n[Agent] Received: '{user_input}'")
        
        user_input_lower = user_input.lower()
        
        if "calculate:" in user_input_lower:
            expr = user_input.split("calculate:")[-1].strip()
            return self.tools["calculate"](expr)
        
        elif "read " in user_input_lower:
            filename = user_input.split("read")[-1].strip()
            return self.tools["read_file"](filename)
        
        else:
            # Fixed the syntax error by using a clean string format
            return "Agent: I am not sure how to handle that. Try 'calculate: 2+2' or 'read test.txt'."

# --- Testing Section ---
if __name__ == "__main__":
    agent = SimpleAgent()
    
    # 1. Create a dummy file for testing
    with open("test.txt", "w") as f:
        f.write("Hello! This is a test file for your agent.")

    # 2. Run test commands
    tasks = [
        "calculate: 15 * 15",
        "read test.txt",
        "Hello!"
    ]
    
    for task in tasks:
        result = agent.execute(task)
        print(f"[Result] {result}")

    # Cleanup: Remove the file after testing
    if os.path.exists("test.txt"):
        os.remove("test.txt")