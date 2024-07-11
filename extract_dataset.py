import subprocess
import os
import shutil

# Generate the gallery from documentation.
print("Generating the gallery from documentation...")
if (subprocess.call(["make", "prepare"], cwd="pgfplots/doc/latex/pgfplots/gallery")):
    raise Exception("Failed to generate the gallery")

dataset_name = "latex_pgfplots_doctest"
if (os.path.exists(dataset_name)):
    print("! The existing dataset will be removed.")
    shutil.rmtree(dataset_name)
os.makedirs(dataset_name)

# Copy the gallery to the dataset, only copy example_*.tex
print("Copying the gallery to the dataset...")
for root, dirs, files in os.walk("pgfplots/doc/latex/pgfplots/gallery"):
    for file in files:
        if file.startswith("example_") and file.endswith(".tex"):
            shutil.copy(os.path.join(root, file), os.path.join(dataset_name, file))

print("Copy dependencies to the dataset...")
shutil.copytree("pgfplots/doc/latex/pgfplots/plotdata", os.path.join(dataset_name, "plotdata"))
shutil.copytree("pgfplots/doc/latex/pgfplots/figures", os.path.join(dataset_name, "figures"))

print("Done.")
print(f"You need to add ${dataset_name}/plotdata and ${dataset_name}/figures to the TEXINPUTS.")
print(f" export TEXINPUTS=$(TEXINPUTS):${dataset_name}/plotdata:${dataset_name}/figures:")
