import json, os
from duckduckgo_search import DDGS

class AdvancedAgent:
    def __init__(self, db="brain.json"):
        self.db = db
        self.memory = self.load()
        self.search_engine = DDGS() # Initialize search engine
        self.tools = {"calc": self.calc, "fact": self.learn, "search": self.web_search}

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
            return str(eval(expr, {"__builtins__": None}, {}))
        except Exception as e:
            return f"Error: {e}"

    def web_search(self, query):
        """Searches the live web and returns the first result."""
        try:
            # We use text() to get the content of the top result
            results = list(self.search_engine.text(query, max_results=1))
            if results:
                return f"Found: {results[0]['body']}"
            return "No results found."
        except Exception as e:
            return f"Search failed: {e}"

    def execute(self, inp):
        cmd = inp.lower().split()
        if not cmd: return "Speak to me!"
        
        # Router logic
        if cmd[0] == "learn": return self.learn(cmd[1], " ".join(cmd[2:]))
        if cmd[0] == "calc": return self.calc(" ".join(cmd[1:]))
        
        # NEW: Web search command
        if cmd[0] == "search": return self.web_search(" ".join(cmd[1:]))
        
        if cmd[0] in self.memory["facts"]: return self.memory["facts"][cmd[0]]
        
        return "Unknown command. Try 'learn [key] [val]', 'calc [expr]', or 'search [query]'."

if __name__ == "__main__":
    agent = AdvancedAgent()
    print("--- Agent with Web Search Active ---")
    while True:
        ui = input("\nAgent > ")
        if ui == "exit": break
        print(agent.execute(ui))