import pandas as pd
import numpy as np

def read_csv_result(csv_file, platform):
    return pd.read_csv(csv_file, index_col="file")["time"].rename(platform)

result_ppedt = read_csv_result("ppedt_times.csv", "PGFPlotsEdt")
result_ppedt_deploy = read_csv_result("ppedt_deploy_times.csv", "PGFPlotsEdt-deploy")
result_laton = read_csv_result("laton_times.csv", "LaTeXOnline")

# Only keep the common successful files
merged_result = pd.DataFrame([result_ppedt_deploy, result_ppedt, result_laton]).T

# index column only keep the parsed number
merged_result.index = merged_result.index.str.extract(r"(\d+)", expand=False).astype(int)

# save the full result
merged_result.replace(np.nan, 0).to_csv("merged_result_times.csv")

# drop the NaN
merged_result = merged_result.dropna()

# save the average time for each column
merged_result.mean(skipna=True).to_csv("merged_result_times_avg.csv", header=["avg"], index_label="method")
