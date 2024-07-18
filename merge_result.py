import pandas as pd

def read_csv_result(csv_file, platform):
    return pd.read_csv(csv_file, index_col="file")["time"].dropna().rename(platform)

result_ppedt = read_csv_result("ppedt_times.csv", "ppedt")
result_ppedt_deploy = read_csv_result("ppedt_deploy_times.csv", "ppedt_deploy")
result_laton = read_csv_result("laton_times.csv", "laton")

# Only keep the common successful files
merged_result = pd.DataFrame([result_ppedt, result_ppedt_deploy, result_laton]).T.dropna()

# index column only keep the parsed number
merged_result.index = merged_result.index.str.extract(r"(\d+)", expand=False).astype(int)

# save the full result
merged_result.to_csv("merged_result_times.csv")

# save the average time for each column
merged_result.mean().to_csv("merged_result_times_avg.csv", header=["avg_time"], index_label="method")
