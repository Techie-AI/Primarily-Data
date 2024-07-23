import csv
from tqdm import tqdm
import itertools
import re


class CompatibilityChecker:
    def __init__(self, compatibility_data):
        self.compatibility_data = compatibility_data
        self.cache = {}

    def extract_numeric_value(self, value):
        match = re.search(r"\d+", value)
        return int(match.group()) if match else 0

    def cache_result(self, key, result):
        self.cache[key] = result
        return result

    def is_cpu_ram_compatible(self, cpu, ram):
        key = ("cpu_ram", cpu, ram)
        if key in self.cache:
            return self.cache[key]

        cpu_data = self.compatibility_data["CPUs"].get(cpu)
        ram_data = self.compatibility_data["RAM"].get(ram)

        if not cpu_data or not ram_data:
            return self.cache_result(key, False)

        cpu_max_ram_speed = self.extract_numeric_value(cpu_data["MaxRAMSpeed"])
        ram_speed = self.extract_numeric_value(ram_data["speed"])

        result = (
            cpu_data["MemoryType"] == ram_data["type"]
            and ram_speed <= cpu_max_ram_speed
        )
        return self.cache_result(key, result)

    def is_cpu_motherboard_compatible(self, cpu, motherboard):
        key = ("cpu_mb", cpu, motherboard)
        if key in self.cache:
            return self.cache[key]

        cpu_data = self.compatibility_data["CPUs"].get(cpu)
        motherboard_data = self.compatibility_data["Motherboards"].get(motherboard)

        if not cpu_data or not motherboard_data:
            return self.cache_result(key, False)

        result = cpu_data["socket"] == motherboard_data["Socket"] and motherboard_data[
            "Chipset"
        ] in cpu_data["SupportedChipsets"].split(",")
        return self.cache_result(key, result)

    def is_cpu_ssd_compatible(self, cpu, motherboard, ssd):
        key = ("cpu_ssd", cpu, motherboard, ssd)
        if key in self.cache:
            return self.cache[key]

        result = self.is_cpu_motherboard_compatible(
            cpu, motherboard
        ) and self.is_ssd_motherboard_compatible(motherboard, ssd)
        return self.cache_result(key, result)

    def is_ram_motherboard_compatible(self, ram, motherboard):
        key = ("ram_mb", ram, motherboard)
        if key in self.cache:
            return self.cache[key]

        ram_data = self.compatibility_data["RAM"].get(ram)
        motherboard_data = self.compatibility_data["Motherboards"].get(motherboard)

        if not ram_data or not motherboard_data:
            return self.cache_result(key, False)

        ram_speed = self.extract_numeric_value(ram_data["speed"])
        motherboard_max_ram_speed = self.extract_numeric_value(
            motherboard_data["MaxRAMSpeed"]
        )

        result = (
            ram_data["type"] == motherboard_data["MemoryType"]
            and ram_speed <= motherboard_max_ram_speed
        )
        return self.cache_result(key, result)

    def is_ram_ssd_compatible(self, ram, motherboard, ssd):
        key = ("ram_ssd", ram, motherboard, ssd)
        if key in self.cache:
            return self.cache[key]

        result = self.is_ram_motherboard_compatible(
            ram, motherboard
        ) and self.is_ssd_motherboard_compatible(motherboard, ssd)
        return self.cache_result(key, result)

    def is_ssd_motherboard_compatible(self, motherboard, ssd):
        key = ("ssd_mb", motherboard, ssd)
        if key in self.cache:
            return self.cache[key]

        motherboard_data = self.compatibility_data["Motherboards"].get(motherboard)
        ssd_data = self.compatibility_data["SSDs"].get(ssd)

        if not motherboard_data or not ssd_data:
            return self.cache_result(key, False)

        result = ssd_data["Interface"] in motherboard_data[
            "SupportedStorageInterfaces"
        ].split(",") and ssd_data["FormFactor"] in motherboard_data[
            "SupportedFormFactors"
        ].split(
            ","
        )
        return self.cache_result(key, result)


def load_csv_to_dict(filename, key):
    data_dict = {}
    try:
        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data_dict[row[key]] = row
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return data_dict


# Load data from CSV files
cpus = load_csv_to_dict("../data/cpu_complete.csv", "cpuName")
rams = load_csv_to_dict("../data/ram_complete.csv", "model")
motherboards = load_csv_to_dict("../data/motherboard_complete.csv", "Name")
ssds = load_csv_to_dict("../data/ssd_complete.csv", "Model")

# Combine the loaded data into compatibility_data dictionary
compatibility_data = {
    "CPUs": cpus,
    "RAM": rams,
    "Motherboards": motherboards,
    "SSDs": ssds,
}

checker = CompatibilityChecker(compatibility_data)

# Open CSV files for writing
with open("training_data.csv", "w", newline="") as training_file, open(
    "compatibility_data.csv", "w", newline=""
) as compatibility_file:
    fieldnames = ["Prompt", "Response"]
    training_writer = csv.DictWriter(training_file, fieldnames=fieldnames)
    compatibility_writer = csv.DictWriter(compatibility_file, fieldnames=fieldnames)

    training_writer.writeheader()
    compatibility_writer.writeheader()

    # Generate combinations and filter for compatibility
    combinations = itertools.product(
        cpus.keys(), rams.keys(), motherboards.keys(), ssds.keys()
    )

    for cpu, ram, mb, ssd in tqdm(
        combinations, total=len(cpus) * len(rams) * len(motherboards) * len(ssds)
    ):
        if (
            checker.is_cpu_ram_compatible(cpu, ram)
            and checker.is_cpu_motherboard_compatible(cpu, mb)
            and checker.is_cpu_ssd_compatible(cpu, mb, ssd)
            and checker.is_ram_motherboard_compatible(ram, mb)
            and checker.is_ram_ssd_compatible(ram, mb, ssd)
            and checker.is_ssd_motherboard_compatible(mb, ssd)
        ):
            prompt = f"I need a {rams[ram]['Capacity (GB)']}GB RAM, a {cpus[cpu]['cpuName']} processor, and a {ssds[ssd]['Capacities']} SSD."
            response = f"CPU: {cpus[cpu]['cpuName']}, RAM: {rams[ram]['model']}, SSD: {ssds[ssd]['Model']}, Motherboard: {motherboards[mb]['Name']}"

            training_writer.writerow({"Prompt": prompt, "Response": response})
            compatibility_writer.writerow({"Prompt": prompt, "Response": response})
