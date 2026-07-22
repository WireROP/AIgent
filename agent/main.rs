use std::env;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 3 {
        println!("Error: Rust engine requires an operation and a payload.");
        process::exit(1);
    }

    let operation = &args[1];
    let payload = &args[2];

    match operation.as_str() {
        "secure_eval" => {
            // Rust processes heavy or strict mathematical parsing safely
            println!("Rust Engine Processing Math: {}", payload);
            // Simple mockup calculation parser for demonstration
            match payload.parse::<f64>() {
                Ok(val) => println!("Result: {}", val * 2.0),
                Err(_) => println!("Result: Invalid numeric input for Rust fast-path."),
            }
        }
        "greet" => {
            println!("Hello from compiled Rust, {}! Execution speed: Optimal.", payload);
        }
        _ => {
            println!("Unknown Rust tool instruction.");
        }
    }
}