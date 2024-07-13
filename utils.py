import os

def getDataset(dir):
    dataset_files = os.listdir(dir)
    dataset_files = [f for f in dataset_files if f.startswith("example_") and f.endswith(".tex")]
    dataset_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    return dataset_files