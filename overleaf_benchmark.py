# Please follow the instruction of overleaf/services/clsi/README.md
# to start the CLSI server before running this script.

import argparse
import utils
import requests
import tqdm
import os
import time

argparser = argparse.ArgumentParser()
argparser.add_argument("--compiler", type=str, choices=["pdflatex","xelatex"], default="pdflatex")
args = argparser.parse_args()

dataset_name = "latex_pgfplots_doctest"
compiler = args.compiler
deploy = args.deploy

# get the dataset list
dataset_files = utils.getDataset(dataset_name)
dataset_size = len(dataset_files)
success_size = 0

# a random project id
project_id=1


headers = {'Content-Type': 'application/json'}

# create a session
session = requests.Session()

total_time = 0
success_time = 0

result_file = "overleaf_times.csv"

with open(result_file, "w") as bf:
    bf.write(f"file,time,reason\n")

def write_result(line):
    with open(result_file, "a") as bf:
        bf.write(f"{line}\n")

with tqdm.tqdm(dataset_files, leave=True) as pbar:
    for file in pbar:
        with open(os.path.join(dataset_name, file), "r") as f:
            texdata = f.read()
        start_time = time.time()
        response = session.post(f"http://127.0.0.1:3013/project/{project_id}/compile", json={
            "compile": {
                "options": {
                    "compiler": compiler,
                    "timeout": 60,
                    "stopOnFirstError": True    # For fair comparsion and for better statistics, stop on the first error.
                },
                "rootResourcePath": "main.tex",
                "resources": [
                    {
                        "path": "main.tex",
                        "content": texdata
                    }
                ]
            }
        }, headers=headers)
        end_time = time.time()
        elapsed_time = end_time - start_time
        total_time += elapsed_time
        try:
            response = response.json()
        except requests.exceptions.JSONDecodeError as e:
            write_result(f"{file},NaN")
            pbar.set_description(f"{file} FAILED")
            continue

        pdf_found = False
        log_text = ""
        for output_file in response["compile"]["outputFiles"]:
            if output_file["type"] == "pdf":
                pdf_found = True
            elif output_file["type"] == "log":
                log_file = requests.get(output_file["url"])
                if log_file.status_code == 200:
                    log_text = log_file.text

        if not pdf_found:
            if log_text:
                # find blocks of errors with started "! "
                errors = [line for line in log_text.split("\n") if line.startswith("! ")]
                if len(errors) > 0:
                    error = errors[0].replace(",","")
                    write_result(f"{file},NaN,{error}")
                else:
                    write_result(f"{file},NaN")
            else:
                write_result(f"{file},NaN")
            pbar.set_description(f"{file} FAILED")
        else:
            pbar.set_description(f"{file} SUCCESS")
            write_result(f"{file},{elapsed_time}")
            success_time += elapsed_time
            success_size += 1

# close the session
session.close()

# Print the result
print(f"**** Overleaf benchmark ****")
print(f"Total time: {total_time/60} min")
print(f"Avg time: {total_time/dataset_size} s for all {dataset_size} examples")
if success_size > 0:
    print(f"Avg time (successful): {success_time/success_size} s for all {success_size} successful examples, success rate: {success_size/dataset_size}")
else:
    print(f"! ALL FAILED")

# **** Overleaf benchmark ****
# Total time: 18.820153113206228 min
# Avg time: 1.5511115203191945 s for all 728 examples
# Avg time (successful): 1.5870506440977195 s for all 658 successful examples, success rate: 0.9038461538461539