import csv


def load_csv_to_dict(filename, key_column):
    """Load CSV data into a dictionary with specified key column."""
    data_dict = {}
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_dict[row[key_column]] = row
    return data_dict


def determine_power_range(cpu_mark):
    """Determine the power range based on CPU Mark."""
    if cpu_mark >= 80000:
        return "high"
    elif cpu_mark >= 60000:
        return "mid"
    else:
        return "low"


def generate_prompt_and_response(cpu_data):
    """Generate prompt and response based on CPU data."""
    prompts_responses = []

    for cpu_name, cpu_info in cpu_data.items():
        company = cpu_name.split(" ")[
            0
        ]  # Assuming the company is the first word in cpuName
        cpu_mark = int(cpu_info["cpuMark"])
        power_range = determine_power_range(cpu_mark)

        # Create a Markdown-compatible description
        description = (
            f"**CPU Name:** {cpu_name}\n\n"
            f"**Company:** {company}\n\n"
            f"**Socket:** {cpu_info['socket']}\n\n"
            f"**Supported Chipsets:** {cpu_info['SupportedChipsets']}\n\n"
            f"**Max RAM Speed:** {cpu_info['MaxRAMSpeed']}\n\n"
            f"**Memory Type:** {cpu_info['MemoryType']}\n\n"
            f"**CPU Mark:** {cpu_info['cpuMark']}\n\n"
            f"**CPU Value:** {cpu_info['cpuValue']}\n\n"
            f"**Thread Mark:** {cpu_info['threadMark']}\n\n"
            f"**Thread Value:** {cpu_info['threadValue']}\n\n"
            f"**TDP:** {cpu_info['TDP']}\n\n"
            f"**Power Performance:** {cpu_info['powerPerf']}\n\n"
            f"**Cores:** {cpu_info['cores']}\n"
        )

        prompt = f"I need a CPU of {company} - {power_range} power range"
        response = description

        prompts_responses.append({"Prompt": prompt, "Response": response})

    return prompts_responses


# Load CPU data from CSV
cpu_data = load_csv_to_dict("../data/cpu_complete.csv", "cpuName")

# Generate prompts and responses
training_data = generate_prompt_and_response(cpu_data)

# Save the training data to CSV
with open("../training_data/cpu_training_data.csv", "w", newline="") as csvfile:
    fieldnames = ["Prompt", "Response"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(training_data)

print("Training data generated and saved to cpu_training_data.csv")
