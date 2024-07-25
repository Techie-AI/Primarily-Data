import csv
import re


def load_csv_to_dict(filename, key_column):
    """Load CSV data into a dictionary with specified key column."""
    data_dict = {}
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_dict[row[key_column]] = row
    return data_dict


def parse_capacity(capacity_str):
    """Extract numerical value from capacity string and convert to GB."""
    match = re.search(r"(\d+\.?\d*)\s*(GB|TB)", capacity_str, re.IGNORECASE)
    if match:
        value = float(match.group(1))
        unit = match.group(2).upper()
        if unit == "TB":
            value *= 1024  # Convert TB to GB
        return int(value)
    return 0


def parse_rw_speed(rw_speed_str):
    """Extract numerical value from R/W speed string and convert to MB/s."""
    match = re.search(r"(\d+\.?\d*)\s*MB/s", rw_speed_str, re.IGNORECASE)
    if match:
        return int(float(match.group(1)))
    return 0


def determine_capacity_and_speed(capacities, rw_speed):
    """Determine the capacity and speed range based on SSD data."""
    capacities = parse_capacity(capacities)
    rw_speed = parse_rw_speed(rw_speed)

    if capacities >= 2000 and rw_speed >= 3500:
        return "high"
    elif capacities >= 1000 and rw_speed >= 1500:
        return "mid"
    else:
        return "low"


def generate_prompt_and_response(ssd_data):
    """Generate prompt and response based on SSD data."""
    prompts_responses = []

    for ssd_model, ssd_info in ssd_data.items():
        capacities = ssd_info["Capacities"]
        rw_speed = ssd_info["R/W"]
        capacity_speed_range = determine_capacity_and_speed(capacities, rw_speed)

        # Create a Markdown-compatible description
        description = (
            f"**Model:** {ssd_model}\n\n"
            f"**Interface:** {ssd_info['Interface']}\n\n"
            f"**Form Factor:** {ssd_info['FormFactor']}\n\n"
            f"**Capacities:** {capacities}\n\n"
            f"**Controller:** {ssd_info['Controller']}\n\n"
            f"**Configuration:** {ssd_info['Configuration']}\n\n"
            f"**DRAM:** {ssd_info['DRAM']}\n\n"
            f"**HMB:** {ssd_info['HMB']}\n\n"
            f"**NAND Brand:** {ssd_info['NAND Brand']}\n\n"
            f"**NAND Type:** {ssd_info['NANDType']}\n\n"
            f"**Layers:** {ssd_info['Layers']}\n\n"
            f"**R/W Speed:** {rw_speed}\n\n"
            f"**Categories:** {ssd_info['Categories']}\n"
        )

        prompt = f"I need an SSD with {capacities} capacities and {rw_speed} speed - {capacity_speed_range} range"
        response = description

        prompts_responses.append({"Prompt": prompt, "Response": response})

    return prompts_responses


# Load SSD data from CSV
ssd_data = load_csv_to_dict("../data/ssd_complete.csv", "Model")

# Generate prompts and responses
training_data = generate_prompt_and_response(ssd_data)

# Save the training data to CSV
with open("../training_data/ssd_training_data.csv", "w", newline="") as csvfile:
    fieldnames = ["Prompt", "Response"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(training_data)

print("Training data generated and saved to ssd_training_data.csv")
