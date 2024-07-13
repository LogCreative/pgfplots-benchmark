import subprocess
import requests
import time
import math
import os
import tqdm
import sys
import utils

dataset_name = "latex_pgfplots_doctest"
compiler = "pdflatex"

texinputs = os.environ.get("TEXINPUTS")
paths = os.environ.get("PATH")

# run python server.py in the background and continue running
server_id = subprocess.Popen(f"{sys.executable} ppedt_server.py", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd="PGFPlotsEdt", shell=True, env={"PATH": paths})
# server_id = subprocess.Popen(f"{sys.executable} gunicorn-deploy.py", stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="PGFPlotsEdt/deploy", shell=True, 
#                              env={"TEXINPUTS": f"{texinputs}:../../{dataset_name}:", "PATH": paths})

# wait for the server to start
time.sleep(5)

# get the dataset list
dataset_files = utils.getDataset(dataset_name)
dataset_size = len(dataset_files)
success_size = 0

# post request to the server.

# generate the request id, make the ending number to 0 to identify it is a benchmark request.
request_id = math.floor(time.time()*10000)

# make it a form data
headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}

# create a session
session = requests.Session()

total_time = 0
success_time = 0

with open("ppedt_times.csv", "w") as bf:
    bf.write(f"file,time,reason\n")

def write_result(line):
    with open("ppedt_times.csv", "a") as bf:
        bf.write(f"{line}\n")

with tqdm.tqdm(dataset_files, leave=True) as pbar:
    for file in pbar:
        with open(os.path.join(dataset_name, file), "r") as f:
            texdata = f.read()
        start_time = time.time()
        response = session.post("http://127.0.0.1:5678/compile", data={
            "requestid": str(request_id),
            "compiler": compiler,
            "texdata": texdata
        }, headers=headers)
        end_time = time.time()
        elapsed_time = end_time - start_time
        total_time += elapsed_time
        if response.headers["Content-Type"] != "application/pdf":
            if response.headers["Content-Type"] == "text/plain; charset=utf-8":
                # find blocks of errors with started "! "
                errors = [line for line in response.text.split("\n") if line.startswith("! ")]
                if len(errors) > 0:
                    error = errors[0].replace(",","") # avoid the comma spliter
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

# Kill the server process
server_id.kill()

# Print the result
print(f"**** PGFPlotsEdt benchmark ****")
print(f"Total time: {total_time/60} min")
print(f"Avg time: {total_time/dataset_size} s for all {dataset_size} examples")
if success_size > 0:
    print(f"Avg time (successful): {success_time/success_size} s for all {success_size} successful examples, success rate: {success_size/dataset_size}")
else:
    print(f"! ALL FAILED")

# Test on MacBook Pro M1
#
# **** PGFPlotsEdt benchmark ****
# Total time: 8.199213667710621 min
# Avg time: 0.6757593682179084 s for all 728 examples
# Avg time (successful): 0.686266279220581 s for all 660 successful examples, success rate: 0.9065934065934066