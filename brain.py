import json, os, datetime
from duckduckgo_search import DDGS

class Brain:
    def __init__(self, db="mind.json"):
        self.db = db
        self.data = self.load()
        self.ddg = DDGS()

    def load(self):
        if os.path.exists(self.db):
            with open(self.db, "r") as f: return json.load(f)
        return {"facts": {}, "lessons": [], "history": []}

    def save(self):
        with open(self.db, "w") as f: json.dump(self.data, f, indent=2)

    def reason(self, user_input):
        """The 'Smart' part: Interprets the intent."""
        inp = user_input.lower()
        
        # Self-Correction: Check if we have a lesson for this type of failure
        for lesson in self.data["lessons"]:
            if lesson in inp:
                return f"I remember that '{lesson}' usually causes problems. Be careful!"

        if "search" in inp: return self.act("search", inp.replace("search", "").strip())
        if "calc" in inp: return self.act("calc", inp.replace("calc", "").strip())
        if "learn" in inp: return self.act("learn", inp.replace("learn", "").strip())
        
        return "I am evaluating your request... I need more specific instructions."

    def act(self, tool, payload):
        """Execution engine."""
        try:
            if tool == "calc":
                res = eval(payload, {"__builtins__": None}, {})
                return f"Result: {res}"
            
            elif tool == "search":
                results = list(self.ddg.text(payload, max_results=1))
                return results[0]['body'] if results else "No data found."
            
            elif tool == "learn":
                key, val = payload.split(" ", 1)
                self.data["facts"][key] = val
                self.save()
                return f"Fact stored: {key}"
        except Exception as e:
            self.data["lessons"].append(payload) # Learn from the mistake
            self.save()
            return f"I failed to execute '{tool}'. I've noted this as a lesson."