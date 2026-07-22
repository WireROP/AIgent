import json
import os
import datetime
import math
import urllib.request
import urllib.error
from pathlib import Path
from duckduckgo_search import DDGS

# ── Robust Cross-Platform Paths (from hackingtool design) ─────────────────────
REPO_NAME = "superagent"
USER_CONFIG_DIR = Path.home() / f".{REPO_NAME}"
USER_BRAIN_FILE = USER_CONFIG_DIR / "super_brain.json"
USER_LOG_FILE   = USER_CONFIG_DIR / f"{REPO_NAME}.log"

class SuperAgent:
    def __init__(self, workspace_file=USER_BRAIN_FILE):
        self.workspace_file = Path(workspace_file)
        self._ensure_workspace()
        self.state = self.load_state()
        self.ddg = DDGS()

    def _ensure_workspace(self):
        """Ensures user-scoped configuration and log directories exist safely."""
        self.workspace_file.parent.mkdir(parents=True, exist_ok=True)

    def load_state(self):
        """Loads structured state including semantic memory and operational metrics."""
        if self.workspace_file.exists():
            try:
                with open(self.workspace_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "semantic_memory": {},
            "episodic_logs": [],
            "error_lessons": []
        }

    def save_state(self):
        """Persists agent state safely to disk."""
        self._ensure_workspace()
        with open(self.workspace_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4)

    # --- TOOLS ---
    
    def tool_math_engine(self, expression: str) -> str:
        """Executes complex sandbox math functions."""
        try:
            safe_dict = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            safe_dict.update({"abs": abs, "round": round, "min": min, "max": max})
            res = eval(expression, {"__builtins__": None}, safe_dict)
            return f"Math Output: {res}"
        except Exception as e:
            return f"Math Execution Error: {e}"

    def tool_web_research(self, query: str) -> str:
        """Performs live context-aware web scraping via DuckDuckGo."""
        try:
            results = list(self.ddg.text(query, max_results=3))
            if not results:
                return "No public data records found."
            formatted = [f"[{r.get('title')}] - {r.get('body')}" for r in results]
            return "\n".join(formatted)
        except Exception as e:
            return f"Research Error: {e}"

    def tool_security_auditor(self, url: str) -> str:
        """
        Defensive security tool: Audits a URL's public security headers 
        and transport layer protection (HTTPS) to ensure defensive best practices.
        """
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        report = [f"🛡️ **Security Audit Report for: {url}**"]
        
        # 1. Transport Layer Check
        if url.startswith("https://"):
            report.append("✅ **Transport Layer**: Secure (Uses HTTPS encryption).")
        else:
            report.append("⚠️ **Transport Layer**: Insecure (Plain HTTP exposes traffic to interception).")

        # 2. Response Headers Security Check
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 DefensiveAuditor'})
            with urllib.request.urlopen(req, timeout=5) as response:
                headers = response.headers
                
                security_headers = {
                    "Strict-Transport-Security": "HSTS enforces secure connections (prevents downgrade attacks).",
                    "Content-Security-Policy": "CSP mitigates Cross-Site Scripting (XSS) and data injection.",
                    "X-Frame-Options": "Protects against Clickjacking attacks.",
                    "X-Content-Type-Options": "Prevents MIME-type sniffing vulnerabilities."
                }

                report.append("\n**Defensive Header Analysis:**")
                for header, description in security_headers.items():
                    if header in headers:
                        report.append(f"  • ✅ **{header}**: Present. ({description})")
                    else:
                        report.append(f"  • ❌ **{header}**: Missing. Recommended implementation: {description}")
                        
        except urllib.error.HTTPError as e:
            report.append(f"⚠️ Server responded with HTTP status code: {e.code} (Headers still indicate active defense posture).")
        except Exception as e:
            report.append(f"❌ Could not complete header audit: {e}")

        return "\n".join(report)

    def tool_memory_writer(self, statement: str) -> str:
        """Parses and stores key-value insights semantically."""
        parts = statement.split(" ", 1)
        if len(parts) < 2:
            return "Syntax error. Use: remember [key] [fact]"
        key, val = parts[0].lower(), parts[1]
        self.state["semantic_memory"][key] = val
        self.save_state()
        return f"Committed to Semantic Memory -> {key}: {val}"

    # --- AUTONOMOUS AGENTIC LOOP ---

    def plan_and_execute(self, user_prompt: str) -> str:
        cleaned = user_prompt.strip()
        lower = cleaned.lower()

        self.state["episodic_logs"].append({"timestamp": str(datetime.datetime.now()), "prompt": cleaned})
        self.save_state()

        # Command Interceptions
        if lower.startswith("calc "):
            return self.tool_math_engine(cleaned[5:].strip())
        
        elif lower.startswith("research "):
            return self.tool_web_research(cleaned[9:].strip())
        
        elif lower.startswith("audit "):
            return self.tool_security_auditor(cleaned[6:].strip())

        elif lower.startswith("remember "):
            return self.tool_memory_writer(cleaned[9:].strip())

        elif lower == "memory-dump":
            return json.dumps(self.state["semantic_memory"], indent=2)

        if lower in self.state["semantic_memory"]:
            return f"Retrieved from Memory: {self.state['semantic_memory'][lower]}"

        if "?" in cleaned or len(cleaned.split()) > 2:
            return self.tool_web_research(cleaned)

        return f"Agent Core ready (Storage: {USER_CONFIG_DIR}). Protocols: 'research [topic]', 'calc [expr]', 'audit [url]', 'remember [k] [v]', or 'memory-dump'."

if __name__ == "__main__":
    agent = SuperAgent()
    print("==================================================")
    print("    NEXT-GEN PYTHON AUTONOMOUS AGENT v4.2         ")
    print(f"    Config Path: {USER_CONFIG_DIR}")
    print("==================================================")
    print("Available Commands:")
    print("  • research [topic]     -> Live Web Gathering")
    print("  • calc [expression]    -> Sandbox Math Engine")
    print("  • audit [url]          -> Defensive Security & Header Check")
    print("  • remember [k] [v]     -> Semantic Storage")
    print("  • exit                 -> Clean Shutdown")
    print("==================================================")

    while True:
        try:
            user_in = input("\nOperator > ").strip()
            if not user_in:
                continue
            if user_in.lower() in ["exit", "quit"]:
                print("Agent > State saved. Shutting down cleanly.")
                break
            
            response = agent.plan_and_execute(user_in)
            print(f"\nAgent Intelligence Feed >\n{response}")

        except KeyboardInterrupt:
            print("\nAgent > Interrupted safely.")
            break

