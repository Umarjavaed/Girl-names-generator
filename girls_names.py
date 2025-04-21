import random
import os
import pandas as pd
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Global lock for combination count and file write
combination_lock = threading.Lock()
write_buffer = []
write_lock = threading.Lock()

def load_names():
    try:
        with open('yob2023.txt', 'r') as f:
            raw_data = f.read()

        female_names = [line.split(',')[0] for line in raw_data.splitlines() if line.split(',')[1] == 'F']
        male_names = [line.split(',')[0] for line in raw_data.splitlines() if line.split(',')[1] == 'M']
        return female_names, male_names
    except FileNotFoundError:
        print("Error: yob2023.txt file not found.")
        return [], []

def load_used_combinations():
    combination_counts = defaultdict(int)
    if os.path.exists('duplicates.txt'):
        with open('duplicates.txt', 'r') as f:
            for line in f:
                combination = line.strip()
                combination_counts[combination] += 1
    return combination_counts

def buffer_combination_for_later_write(first_name, last_name):
    with write_lock:
        write_buffer.append(f"{first_name},{last_name}\n")

def flush_write_buffer():
    with write_lock:
        if write_buffer:
            with open('duplicates.txt', 'a') as f:
                f.writelines(write_buffer)
            write_buffer.clear()

def worker_task(female_names, male_names, used_combinations, results, target_count):
    while True:
        if len(results) >= target_count:
            return

        female = random.choice(female_names)
        male = random.choice(male_names)
        combo = f"{female},{male}"

        with combination_lock:
            if used_combinations[combo] < 2:
                used_combinations[combo] += 1
                results.append({'First Name': female, 'Last Name': male})
                buffer_combination_for_later_write(female, male)

def generate_names(num_combinations, num_threads=160):
    female_names, male_names = load_names()
    if not female_names or not male_names:
        return []

    used_combinations = load_used_combinations()
    results = []
    results_lock = threading.Lock()

    start_time = time.time()
    timeout = 1200  # 20 minutes

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_task, female_names, male_names, used_combinations, results, num_combinations)
                   for _ in range(num_threads)]

        while len(results) < num_combinations and time.time() - start_time < timeout:
            time.sleep(0.1)

        # Cancel threads if needed
        for future in futures:
            future.cancel()

    flush_write_buffer()

    if len(results) < num_combinations:
        print(f"⚠️  Only generated {len(results)} combinations out of {num_combinations}.")

    return results[:num_combinations]  # Trim in case of slight overfill

def main():
    try:
        num_combinations = int(input("How many unique name combinations do you want to generate? "))
        if num_combinations <= 0:
            print("Please enter a positive number.")
            return

        results = generate_names(num_combinations)

        if results:
            df = pd.DataFrame(results)
            df.to_csv("generated_names.csv", index=False)
            print(f"\n✅ Generated {len(results)} unique name combinations and saved to 'generated_names.csv'")
            print("\nSample:")
            print(df.head())

    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
