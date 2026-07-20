import json, os, datetime

class AdvancedAgent:
    def __init__(self, db="brain.json"):
        self.db = db
        self.memory = self.load()
        self.tools = {"calc": self.calc, "fact": self.learn}

    def load(self):
        if os.path.exists(self.db):
            with open(self.db, "r") as f: return json.load(f)
        return {"facts": {}, "errors": []}

    def save(self):
        with open(self.db, "w") as f: json.dump(self.memory, f, indent=2)

    def learn(self, key, val):
        self.memory["facts"][key] = val
        self.save()
        return f"Stored: {key} = {val}"

    def calc(self, expr):
        try:
            res = eval(expr, {"__builtins__": None}, {})
            return str(res)
        except Exception as e:
            self.memory["errors"].append(f"Failed {expr}: {str(e)}")
            self.save()
            return f"Error: {e}. Lesson recorded."

    def reflect(self):
        return f"Brain State: {len(self.memory['facts'])} facts known. {len(self.memory['errors'])} mistakes learned from."

    def execute(self, inp):
        cmd = inp.lower().split()
        if not cmd: return "Speak to me!"
        
        # Router logic
        if cmd[0] == "learn": return self.learn(cmd[1], " ".join(cmd[2:]))
        if cmd[0] == "calc": return self.calc(" ".join(cmd[1:]))
        if cmd[0] == "state": return self.reflect()
        if cmd[0] in self.memory["facts"]: return self.memory["facts"][cmd[0]]
        
        return "I don't know that. Try 'learn [key] [value]', 'calc [math]', or 'state'."

if __name__ == "__main__":
    agent = AdvancedAgent()
    print("--- Advanced Agent Active ---")
    while True:
        try:
            ui = input("\nAgent > ")
            if ui == "exit": break
            print(agent.execute(ui))
        except KeyboardInterrupt: break