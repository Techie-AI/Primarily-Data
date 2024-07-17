import os
import csv
import time
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tqdm import tqdm


def read_csv(file_path):
    with open(file_path, newline="") as csvfile:
        return list(csv.DictReader(csvfile))


def write_csv(file_path, fieldnames, rows):
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


llm = ChatOllama(model="lamma3:8b")
prompt = ChatPromptTemplate.from_template('{Prompt} "{text}"')
chain = prompt | llm | StrOutputParser()

input_csv_path = "../raw_data/cpu.csv"
output_csv_path = "../data/cpu_complete.csv"

data = read_csv(input_csv_path)

fieldnames = data[0].keys()

print(data)
# print(fieldnames)

csv_file_path = "processing_times.csv"
with open(csv_file_path, "w", newline="") as csvfile:
    fieldnames_times = ["File Name", "Processing Time (s)"]
    writer_times = csv.DictWriter(csvfile, fieldnames=fieldnames_times)
    writer_times.writeheader()

    total_processing_time = 0

    for row in tqdm(data, desc="Processing rows"):
        missing_fields = [key for key, value in row.items() if not value]

        if missing_fields:
            start_time = time.time()

            for field in missing_fields:
                prompt_text = f"""Fill in the missing value for the following CPU data:
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
                
                Please provide the missing value for {field}."""

                response = chain.invoke({"Prompt": prompt_text, "text": ""})
                row[field] = response.strip()

            end_time = time.time()

            processing_time = end_time - start_time
            total_processing_time += processing_time

            writer_times.writerow(
                {"File Name": row["cpuName"], "Processing Time (s)": processing_time}
            )

    write_csv(output_csv_path, fieldnames, data)

print(f"Total Processing Time: {total_processing_time} seconds")
