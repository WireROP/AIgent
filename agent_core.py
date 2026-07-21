import json
import os
import datetime
import math
import subprocess
from duckduckgo_search import DDGS

class AgentCore:
    def __init__(self, storage_file="agent_mind.json"):
        self.storage_file = storage_file
        self.mind = self._load_mind()
        self.ddg = DDGS()
        
        # Register available tools dynamically
        self.tools = {
            "calc": self.tool_calculator,
            "search": self.tool_web_search,
            "learn": self.tool_learn_fact,
            "recall": self.tool_recall_fact,
            "sys": self.tool_system_command
        }

    def _load_mind(self):
        """Loads persistent memory, facts, lessons, and history from disk."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass # Fallback if file is corrupted
        
        return {
            "facts": {},
            "lessons": [],
            "history": [],
            "metrics": {"total_actions": 0, "errors_handled": 0}
        }

    def _save_mind(self):
        """Persists the agent's mind state to disk safely."""
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(self.mind, f, indent=4)

    def log_event(self, role, content):
        """Records telemetry and conversation history."""
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "role": role,
            "content": content
        }
        self.mind["history"].append(entry)
        self._save_mind()

    # --- CORE TOOL DEFINITIONS ---

    def tool_calculator(self, expression: str) -> str:
        """Safely evaluates advanced mathematical expressions."""
        try:
            # Provide safe builtins for math evaluation
            allowed_names = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
            
            result = eval(expression, {"__builtins__": None}, allowed_names)
            return f"Calculation Result: {result}"
        except Exception as e:
            raise ValueError(f"Invalid math syntax: {e}")

    def tool_web_search(self, query: str) -> str:
        """Performs a live web lookup via DuckDuckGo."""
        try:
            results = list(self.ddg.text(query, max_results=2))
            if not results:
                return "No relevant public web data found."
            
            summaries = []
            for r in results:
                title = r.get("title", "No Title")
                body = r.get("body", "No Body")
                summaries.append(f"- **{title}**: {body}")
            
            return "\n".join(summaries)
        except Exception as e:
            raise ConnectionError(f"Network error during search execution: {e}")

    def tool_learn_fact(self, key_value_str: str) -> str:
        """Saves a permanent fact into long-term semantic storage."""
        parts = key_value_str.split(" ", 1)
        if len(parts) < 2:
            return "Error: Use format 'learn [key] [statement]'"
        
        key, val = parts[0].lower(), parts[1]
        self.mind["facts"][key] = val
        self._save_mind()
        return f"Long-term memory updated. I will remember that '{key}' means: {val}"

    def tool_recall_fact(self, key: str) -> str:
        """Retrieves a stored fact from semantic memory."""
        key = key.lower().strip()
        if key in self.mind["facts"]:
            return f"Memory Recall [{key}]: {self.mind['facts'][key]}"
        return f"I have no record of '{key}' in my long-term memory."

    def tool_system_command(self, command: str) -> str:
        """Executes terminal commands (sandboxed wrapper)."""
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=5)
            return f"System Output:\n{output.strip()}"
        except Exception as e:
            raise RuntimeError(f"System execution failed: {e}")

    # --- THE REASONING & REFLECTION ENGINE ---

    def evaluate_intent(self, user_input: str):
        """
        Parses text, checks learned lessons for error prevention, 
        and maps inputs to appropriate tool executions.
        """
        cleaned = user_input.strip()
        lower_input = cleaned.lower()
        
        # 1. Self-Correction / Lesson Guard Check
        for lesson in self.mind["lessons"]:
            if any(word in lower_input for word in lesson.get("triggers", [])):
                print(f"[Agent Reflection Warning]: Past experience dictates caution here -> {lesson['advice']}")

        # 2. Direct Query Matching or Intent Routing
        parts = cleaned.split(" ", 1)
        command = parts[0].lower()
        payload = parts[1] if len(parts) > 1 else ""

        # Check internal long-term memory lookup first
        if command in self.mind["facts"]:
            return f"From Memory: {self.mind['facts'][command]}"

        # Route to explicit tool if matched
        if command in self.tools:
            return self.execute_tool(command, payload)

        # Conversational fallback / Contextual analysis
        if "status" in lower_input or "brain" in lower_input:
            return (
                f"🧠 **Agent Status Report**:\n"
                f"- Stored Facts: {len(self.mind['facts'])}\n"
                f"- Lessons Learned from Errors: {len(self.mind['lessons'])}\n"
                f"- Total Actions Processed: {self.mind['metrics']['total_actions']}\n"
                f"- Handled Exceptions: {self.mind['metrics']['errors_handled']}"
            )

        if any(greet in lower_input for greet in ["hi", "hello", "hey"]):
            return "Hello! I am your advanced local python agent core. Type a command like 'search [query]', 'calc [math]', 'learn [key] [fact]', or 'status'."

        # Default fallback: Try a lightweight web search if it looks like a question
        if "?" in cleaned or len(cleaned.split()) > 3:
            print("[Agent Note]: Triggering automatic fallback search...")
            return self.execute_tool("search", cleaned)

        return f"Command not recognized ('{command}'). Try 'search', 'calc', 'learn', or check 'status'."

    def execute_tool(self, tool_name: str, payload: str):
        """Executes a tool within a safe try/except boundary to self-heal."""
        self.mind["metrics"]["total_actions"] += 1
        try:
            result = self.tools[tool_name](payload)
            self._save_mind()
            return result
        except Exception as error:
            self.mind["metrics"]["errors_handled"] += 1
            
            # Log failure mechanism for self-correction feedback loop
            error_lesson = {
                "tool": tool_name,
                "payload": payload,
                "error": str(error),
                "triggers": [word for word in payload.lower().split() if len(word) > 3],
                "advice": f"Tool '{tool_name}' failed with payload '{payload}'. Avoid repeating this exact signature."
            }
            self.mind["lessons"].append(error_lesson)
            self._save_mind()
            
            return f"⚠️ [Self-Correction Triggered]: Tool execution failed: {error}. I have recorded a failure lesson to optimize future decisions."