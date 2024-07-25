import csv
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tqdm import tqdm


def read_csv(file_path):
    with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
        return data, reader.fieldnames


def write_csv(file_path, fieldnames, rows):
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerows(rows)


llm = ChatOllama(model="llama3")
prompt = ChatPromptTemplate.from_template('{Prompt} "{text}"')
chain = prompt | llm | StrOutputParser()

input_csv_path = "../raw_data/cpu.csv"
output_csv_path = "../data/cpu_complete.csv"

data, fieldnames = read_csv(input_csv_path)

# Remove BOM character from the first column name if it exists
first_column = list(data[0].keys())[0]
if first_column.startswith("\ufeff"):
    new_first_column = first_column.lstrip("\ufeff")
    for row in data:
        row[new_first_column] = row.pop(first_column)

# Ensure the output file has the headers written initially
with open(output_csv_path, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

for row in tqdm(data, desc="Processing rows"):
    missing_fields = [key for key, value in row.items() if not value]

    if missing_fields:
        prompt_text = f"""Given the following CPU data:
        cpuName: {row['cpuName']}
        socket: {row['socket']}
        SupportedChipsets: {row['SupportedChipsets']}
        MaxRAMSpeed: {row['MaxRAMSpeed']}
        MemoryType: {row['MemoryType']}
        cpuMark: {row['cpuMark']}
        cpuValue: {row['cpuValue']}
        threadMark: {row['threadMark']}
        threadValue: {row['threadValue']}
        TDP: {row['TDP']}
        powerPerf: {row['powerPerf']}
        cores: {row['cores']}
        
        Please fill in the missing values in this format:

        cpuName: {row['cpuName']}
        socket: {row['socket']}
        SupportedChipsets: {row['SupportedChipsets']}
        MaxRAMSpeed: {row['MaxRAMSpeed']}
        MemoryType: {row['MemoryType']}
        cpuMark: {row['cpuMark']}
        cpuValue: {row['cpuValue']}
        threadMark: {row['threadMark']}
        threadValue: {row['threadValue']}
        TDP: {row['TDP']}
        powerPerf: {row['powerPerf']}
        cores: {row['cores']}
        """

        response = chain.invoke({"Prompt": prompt_text, "text": ""})
        response_data = response.strip().split("\n")
        for line in response_data:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key in row and not row[key]:
                    row[key] = value

    # Write the updated row to the output CSV file
    write_csv(output_csv_path, fieldnames, [row])
