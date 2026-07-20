import json
import os
import datetime

class SmartAgent:
    def __init__(self, memory_file="agent_memory.json"):
        self.memory_file = memory_file
        # Load conversation history from disk
        self.history = self.load_history()
        self.tools = {
            "calculate": self.calculate,
            "read_file": self.read_file
        }

    def load_history(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def log_turn(self, role, content):
        entry = {"role": role, "content": content, "ts": str(datetime.datetime.now())}
        self.history.append(entry)
        self.save_history()

    def calculate(self, expression):
        try:
            result = eval(expression, {"__builtins__": None}, {})
            return f"The result is {result}"
        except:
            return "I couldn't calculate that."

    def read_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return f.read()
        return "File not found."

    def execute(self, user_input):
        # 1. Log the user's input to history
        self.log_turn("user", user_input)
        
        # 2. Contextual logic (The "Brain")
        inp = user_input.lower()
        
        if "calculate" in inp:
            response = self.calculate(user_input.split("calculate")[-1])
        elif "read" in inp:
            response = self.read_file(user_input.split("read")[-1].strip())
        elif "history" in inp or "what did we do" in inp:
            # Reflection: Look at our stored history
            summarized = [msg['content'] for msg in self.history[-5:]]
            response = f"Here is what we've been doing: {summarized}"
        elif any(g in inp for g in ["hi", "hello", "how are you"]):
            response = "I'm doing great and I remember our past conversations. How can I help?"
        else:
            # Fallback: Look at the last memory turn for context
            last_context = self.history[-2]['content'] if len(self.history) > 1 else "nothing"
            response = f"I'm not sure, but earlier we were talking about '{last_context}'. Did you mean to ask about that?"

        # 3. Log agent's response
        self.log_turn("assistant", response)
        return response

if __name__ == "__main__":
    agent = SmartAgent()
    print("--- Smart Agent Started (Type 'exit' to quit) ---")
    while True:
        user_in = input("\nYou: ")
        if user_in.lower() == "exit": break
        print(f"Agent: {agent.execute(user_in)}")