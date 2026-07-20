import json
import os

class SmartAgent:
    def __init__(self, kb_file="knowledge.json"):
        self.kb_file = kb_file
        self.knowledge = self.load_knowledge()

    def load_knowledge(self):
        if os.path.exists(self.kb_file):
            with open(self.kb_file, "r") as f:
                return json.load(f)
        return {"facts": [], "lessons_learned": []}

    def save_knowledge(self):
        with open(self.kb_file, "w") as f:
            json.dump(self.knowledge, f, indent=2)

    def learn(self, category, item):
        """Adds a fact or lesson to our permanent memory."""
        if item not in self.knowledge[category]:
            self.knowledge[category].append(item)
            self.save_knowledge()
            return f"I've learned: {item}"
        return "I already knew that."

    def execute(self, user_input):
        inp = user_input.lower()

        # 1. Learn Mode: Allows you to manually teach the agent
        if "learn that" in inp:
            fact = user_input.split("learn that")[-1].strip()
            return self.learn("facts", fact)

        # 2. Knowledge Query
        elif "what do you know" in inp:
            return f"Facts: {self.knowledge['facts']}. Lessons: {self.knowledge['lessons_learned']}"

        # 3. Calculation with Learning from Mistakes
        elif "calculate" in inp:
            try:
                expr = inp.split("calculate")[-1].strip()
                result = eval(expr, {"__builtins__": None}, {})
                return f"Result: {result}"
            except Exception as e:
                error_msg = f"Failed to calculate '{inp}'. Reason: {str(e)}"
                self.learn("lessons_learned", error_msg)
                return f"I made a mistake: {error_msg}. I have recorded this to learn for next time."

        # 4. Basic Conversational Logic
        elif "hi" in inp or "hello" in inp:
            return "Hello! I am learning. You can 'learn that [fact]' or ask me to calculate something."
        
        else:
            return "I am not sure. Try 'learn that [fact]' or 'what do you know?'"

if __name__ == "__main__":
    agent = SmartAgent()
    print("--- Learning Agent Started ---")
    while True:
        user_in = input("\nYou: ")
        if user_in.lower() == "exit": break
        print(f"Agent: {agent.execute(user_in)}")