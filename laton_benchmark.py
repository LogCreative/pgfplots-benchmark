# create a server for file feed and map it to the docker
# latex online will get the file from the url of the file

import subprocess
import sys
import docker
import time
import utils
import requests
import argparse
import tqdm

argparser = argparse.ArgumentParser()
argparser.add_argument("--compiler", type=str, choices=["pdflatex","xelatex"], default="pdflatex")
args = argparser.parse_args()


dataset_name = "latex_pgfplots_doctest"

# Start the file server to feed the LaTeX Online
print("Start file server ...")
server_id = subprocess.Popen(f"{sys.executable} file_server.py", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

# Start LaTeX Online from docker
# Please build the image first.
print("Start LaTeX Online ...")
client = docker.from_env()
container = client.containers.run("logcreative/latex-online:latest", detach=True, ports={'2700/tcp': 2700}, extra_hosts={"host.docker.internal": "host-gateway"})
# docker run --add-host=host.docker.internal:host-gateway -p 2700:2700 -d aslushnikov/latex-online:latest

# Wait for the server to start, git clone may slow for LaTeX Online
print("Wait for the server to start (30s) ...")
time.sleep(30)

print("Benchmark started ...")
dataset_files = utils.getDataset(dataset_name)
dataset_size = len(dataset_files)
success_size = 0

# Post request to the server
# create a session
session = requests.Session()

total_time = 0
success_time = 0

result_file = "laton_times.csv"

with open(result_file, "w") as bf:
    bf.write(f"file,time,reason\n")

def write_result(line):
    with open(result_file, "a") as bf:
        bf.write(f"{line}\n")

with tqdm.tqdm(dataset_files, leave=True) as pbar:
    for file in pbar:
        start = time.time()
        try:
            response = session.get(f"http://127.0.0.1:2700/compile?url=http://host.docker.internal:3000/{dataset_name}/{file}&compiler={args.compiler}")
        except Exception as e:
            print(f"Error: {e}")
            write_result(f"{file},NaN")
            total_time += time.time() - start
            pbar.set_description(f"{file} FAILED")
            continue
        end = time.time()
        elapsed_time = end - start
        total_time += elapsed_time
        if response.headers["Content-Type"] != "application/pdf":
            if response.headers["Content-Type"] == "text/plain; charset=utf-8" or response.headers["Content-Type"] == "text/plain; charset=UTF-8":
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

# Close the session
session.close()

# Close the LaTeX Online
container.stop()

# Close the file server
server_id.kill()

# Print the result
print(f"**** LaTeX Online benchmark ****")
print(f"Total time: {total_time/60} min")
print(f"Avg time: {total_time/dataset_size} s for all {dataset_size} examples")
if success_size > 0:
    print(f"Avg time (successful): {success_time/success_size} s for all {success_size} successful examples, success rate: {success_size/dataset_size}")
else:
    print(f"! ALL FAILED")