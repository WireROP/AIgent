from brain import Brain

def main():
    agent = Brain()
    print("--- Advanced Cognition Agent Active ---")
    print("Commands: search [term], calc [expr], learn [key] [val]")
    
    while True:
        user_in = input("\nYou > ")
        if user_in.lower() in ["exit", "quit"]: break
        
        # Agent 'thinks' then acts
        response = agent.reason(user_in)
        print(f"Agent > {response}")

if __name__ == "__main__":
    main()