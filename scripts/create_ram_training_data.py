import csv


def load_csv_to_dict(filename, key_column):
    """Load CSV data into a dictionary with specified key column."""
    data_dict = {}
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_dict[row[key_column]] = row
    return data_dict


def determine_speed_and_capacity(speed, capacity):
    """Determine the speed and capacity range."""
    if int(speed) >= 6000 and int(capacity) >= 32:
        return "high"
    elif int(speed) >= 4000 and int(capacity) >= 16:
        return "mid"
    else:
        return "low"


def generate_prompt_and_response(ram_data):
    """Generate prompt and response based on RAM data."""
    prompts_responses = []

    for ram_model, ram_info in ram_data.items():
        speed = ram_info["speed"]
        capacity = ram_info["Capacity (GB)"]
        speed_capacity_range = determine_speed_and_capacity(speed, capacity)

        # Create a Markdown-compatible description
        description = (
            f"**Model:** {ram_model}\n\n"
            f"**Type:** {ram_info['type']}\n\n"
            f"**Speed:** {speed}\n\n"
            f"**Capacity (GB):** {capacity}\n\n"
            f"**Form Factor:** {ram_info['Form Factor']}\n\n"
            f"**DRAM Configuration:** {ram_info['DRAM Configuration']}\n"
        )

        prompt = (
            f"I need {capacity}GB RAM with {speed} speed - {speed_capacity_range} range"
        )
        response = description

        prompts_responses.append({"Prompt": prompt, "Response": response})

    return prompts_responses


# Load RAM data from CSV
ram_data = load_csv_to_dict("../data/ram_complete.csv", "model")

# Generate prompts and responses
training_data = generate_prompt_and_response(ram_data)

# Save the training data to CSV
with open("../training_data/ram_training_data.csv", "w", newline="") as csvfile:
    fieldnames = ["Prompt", "Response"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(training_data)

print("Training data generated and saved to ram_training_data.csv")
