import csv
import itertools


class CompatibilityChecker:
    def __init__(self, compatibility_data):
        self.compatibility_data = compatibility_data

    def is_cpu_ram_compatible(self, cpu, ram):
        cpu_data = self.compatibility_data["CPUs"].get(cpu)
        ram_data = self.compatibility_data["RAM"].get(ram)

        if not cpu_data or not ram_data:
            return False

        return (
            cpu_data["memory_type"] == ram_data["type"]
            and ram_data["speed"] <= cpu_data["max_ram_speed"]
        )

    def is_cpu_motherboard_compatible(self, cpu, motherboard):
        cpu_data = self.compatibility_data["CPUs"].get(cpu)
        motherboard_data = self.compatibility_data["Motherboards"].get(motherboard)

        if not cpu_data or not motherboard_data:
            return False

        return (
            cpu_data["socket"] == motherboard_data["socket"]
            and motherboard_data["chipset"] in cpu_data["chipset"]
        )

    def is_cpu_ssd_compatible(self, cpu, motherboard, ssd):
        return self.is_cpu_motherboard_compatible(
            cpu, motherboard
        ) and self.is_ssd_motherboard_compatible(motherboard, ssd)

    def is_ram_motherboard_compatible(self, ram, motherboard):
        ram_data = self.compatibility_data["RAM"].get(ram)
        motherboard_data = self.compatibility_data["Motherboards"].get(motherboard)

        if not ram_data or not motherboard_data:
            return False

        return (
            ram_data["type"] == motherboard_data["memory_type"]
            and ram_data["speed"] <= motherboard_data["max_ram_speed"]
        )

    def is_ram_ssd_compatible(self, ram, motherboard, ssd):
        return self.is_ram_motherboard_compatible(
            ram, motherboard
        ) and self.is_ssd_motherboard_compatible(motherboard, ssd)

    def is_ssd_motherboard_compatible(self, motherboard, ssd):
        motherboard_data = self.compatibility_data["Motherboards"].get(motherboard)
        ssd_data = self.compatibility_data["SSDs"].get(ssd)

        if not motherboard_data or not ssd_data:
            return False

        return (
            ssd_data["interface"] in motherboard_data["supported_storage_interfaces"]
            and ssd_data["form_factor"] in motherboard_data["supported_form_factors"]
        )


def load_csv_to_dict(filename):
    data_dict = {}
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data_dict[row["name"]] = row
    return data_dict


# Load data from CSV files
cpus = load_csv_to_dict("../data/cpu_complete.csv")
rams = load_csv_to_dict("../data/ram_complete.csv")
motherboards = load_csv_to_dict("../data/motherboard_complete.csv")
ssds = load_csv_to_dict("../data/ssd_complete.csv")

# Combine the loaded data into compatibility_data dictionary
compatibility_data = {
    "CPUs": cpus,
    "RAM": rams,
    "Motherboards": motherboards,
    "SSDs": ssds,
}

checker = CompatibilityChecker(compatibility_data)

# Generate combinations and filter for compatibility
training_data = []
compatibility_datas = []

for cpu, ram, mb, ssd in itertools.product(
    cpus.keys(), rams.keys(), motherboards.keys(), ssds.keys()
):
    if (
        checker.is_cpu_ram_compatible(cpu, ram)
        and checker.is_cpu_motherboard_compatible(cpu, mb)
        and checker.is_cpu_ssd_compatible(cpu, mb, ssd)
        and checker.is_ram_motherboard_compatible(ram, mb)
        and checker.is_ram_ssd_compatible(ram, mb, ssd)
        and checker.is_ssd_motherboard_compatible(mb, ssd)
    ):

        prompt = f"I need a {rams[ram]['Capacity (GB)']}GB RAM, a {cpus[cpu]['category']} processor, and a {ssds[ssd]['Capacities']} SSD."
        response = f"CPU: {cpus[cpu]['name']}, RAM: {rams[ram]['name']}, SSD: {ssds[ssd]['name']}, Motherboard: {motherboards[mb]['name']}"

        compatibility_datas.append(response)
        training_data.append({"Prompt": prompt, "Response": response})

# Save the training data to CSV
with open("training_data.csv", "w", newline="") as csvfile:
    fieldnames = ["Prompt", "Response"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(training_data)


# Save the training data to CSV
with open("compatibility_data.csv", "w", newline="") as csvfile:
    fieldnames = ["Prompt", "Response"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(training_data)
