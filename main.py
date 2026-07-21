from agent_core import AgentCore

def main():
    agent = AgentCore()
    print("==================================================")
    print("       ADVANCED PYTHON AUTONOMOUS AGENT v3.0      ")
    print("==================================================pss")
    print("Commands available:")
    print("  • search [query]       -> Live web intelligence")
    print("  • calc [expression]    -> Advanced math evaluation")
    print("  • learn [key] [fact]   -> Store permanent facts")
    print("  • status               -> View brain metrics & memory size")
    print("  • exit                 -> Safely shutdown and save state")
    print("==================================================")

    while True:
        try:
            user_input = input("\nUser > ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "shutdown"]:
                print("Agent > Saving state to disk. Shutting down cleanly. Goodbye!")
                break

            # Log user intent
            agent.log_event("user", user_input)

            # Process through agent brain core
            response = agent.evaluate_intent(user_input)

            # Log agent response
            agent.log_event("assistant", response)

            print(f"\nAgent >\n{response}")

        except KeyboardInterrupt:
            print("\nAgent > Emergency shutdown signal caught. State preserved. Goodbye!")
            break
        except Exception as ex:
            print(f"\nSystem Error: {ex}")

if __name__ == "__main__":
    main()