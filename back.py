import random
import os
import pandas as pd
from collections import defaultdict

def load_names():
    # Read directly from the local file
    try:
        with open('yob2023.txt', 'r') as f:
            raw_data = f.read()
        
        # Parse female and male names
        female_names = [line.split(',')[0] for line in raw_data.splitlines() if line.split(',')[1] == 'F']
        male_names = [line.split(',')[0] for line in raw_data.splitlines() if line.split(',')[1] == 'M']
        
        return female_names, male_names
    except FileNotFoundError:
        print("Error: yob2023.txt file not found in the current directory.")
        return [], []

def load_used_combinations():
    combination_counts = defaultdict(int)
    if os.path.exists('duplicates.txt'):
        with open('duplicates.txt', 'r') as f:
            for line in f:
                combination = line.strip()
                combination_counts[combination] += 1
    return combination_counts

def save_used_combination(first_name, last_name):
    with open('duplicates.txt', 'a') as f:
        f.write(f"{first_name},{last_name}\n")

def generate_names(num_combinations):
    female_names, male_names = load_names()
    used_combinations = load_used_combinations()
    
    results = []
    attempts = 0
    max_attempts = 1000000  # Prevent infinite loop
    
    while len(results) < num_combinations and attempts < max_attempts:
        attempts += 1
        
        # Get random female and male names
        female_name = random.choice(female_names)
        male_name = random.choice(male_names)
        
        # Create combination string
        combination = f"{female_name},{male_name}"
        
        # Check if combination has been used less than 2 times
        if used_combinations[combination] < 2:
            results.append({
                'First Name': female_name,
                'Last Name': male_name
            })
            used_combinations[combination] += 1
            save_used_combination(female_name, male_name)
    
    if attempts >= max_attempts:
        print("Warning: Could not generate all unique combinations. Try with a smaller number.")
    
    return results

def main():
    try:
        num_combinations = int(input("How many unique name combinations do you want to generate? "))
        if num_combinations <= 0:
            print("Please enter a positive number.")
            return
            
        results = generate_names(num_combinations)
        if results:
            # Create DataFrame and save to CSV
            df = pd.DataFrame(results)
            csv_file = 'generated_names.csv'
            df.to_csv(csv_file, index=False)
            print(f"\nGenerated {len(results)} unique name combinations and saved them to '{csv_file}'")
            print("\nFirst few names:")
            print(df.head())
            
    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
