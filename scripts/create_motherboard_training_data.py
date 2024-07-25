import csv


def load_csv_to_dict(filename, key_column):
    """Load CSV data into a dictionary with specified key column."""
    data_dict = {}
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_dict[row[key_column]] = row
    return data_dict


def determine_power_range(max_ram_speed):
    """Determine the power range based on Max RAM Speed."""
    # Assumed ranges based on typical values
    if "DDR5" in max_ram_speed or "DDR4-3600" in max_ram_speed:
        return "high"
    elif "DDR4-3200" in max_ram_speed or "DDR4-2933" in max_ram_speed:
        return "mid"
    else:
        return "low"


def generate_prompt_and_response(motherboard_data):
    """Generate prompt and response based on motherboard data."""
    prompts_responses = []

    for mb_name, mb_info in motherboard_data.items():
        # Extract company name from motherboard name if possible
        company = mb_name.split(" ")[
            0
        ]  # Assuming the company is the first word in Name
        max_ram_speed = mb_info["MaxRAMSpeed"]
        power_range = determine_power_range(max_ram_speed)

        # Create a Markdown-compatible description
        description = (
            f"**Motherboard Name:** {mb_name}\n\n"
            f"**Company:** {company}\n\n"
            f"**Socket:** {mb_info['Socket']}\n\n"
            f"**Chipset:** {mb_info['Chipset']}\n\n"
            f"**Max RAM Speed:** {mb_info['MaxRAMSpeed']}\n\n"
            f"**Memory Type:** {mb_info['MemoryType']}\n\n"
            f"**Supported Storage Interfaces:** {mb_info['SupportedStorageInterfaces']}\n\n"
            f"**Supported Form Factors:** {mb_info['SupportedFormFactors']}\n\n"
            f"**Form Factor:** {mb_info['Formfactor']}\n"
        )

        prompt = f"I need a motherboard of {company} - {power_range} power range"
        response = description

        prompts_responses.append({"Prompt": prompt, "Response": response})

    return prompts_responses


# Load motherboard data from CSV
motherboard_data = load_csv_to_dict("../data/motherboard_complete.csv", "Name")

# Generate prompts and responses
training_data = generate_prompt_and_response(motherboard_data)

# Save the training data to CSV
with open("../training_data/motherboard_training_data.csv", "w", newline="") as csvfile:
    fieldnames = ["Prompt", "Response"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(training_data)

print("Training data generated and saved to motherboard_training_data.csv")
