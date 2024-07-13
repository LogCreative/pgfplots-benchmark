import subprocess
import os
import shutil
import re

# Generate the gallery from documentation.
print("Generating the gallery from documentation...")
if (subprocess.call(["make", "clean"], cwd="pgfplots/doc/latex/pgfplots/gallery")):
    raise Exception("Failed to clean the gallery")
if (subprocess.call(["make", "prepare"], cwd="pgfplots/doc/latex/pgfplots/gallery")):
    raise Exception("Failed to generate the gallery")

dataset_name = "latex_pgfplots_doctest"
if (os.path.exists(dataset_name)):
    print("! The existing dataset will be removed.")
    shutil.rmtree(dataset_name)
os.makedirs(dataset_name)

# Copy the gallery to the dataset, only copy example_*.tex
print("Copying the gallery to the dataset...")
plotdata_re = re.compile(r"plotdata/([^\}\n\\]*)\}")
plotdata_addr = "pgfplots/doc/latex/pgfplots/plotdata"
rootdata_re = re.compile(r"\{([^\}/\n\\]*.dat)\}")
rootdata_addr = "pgfplots/doc/latex/pgfplots/"
for root, dirs, files in os.walk("pgfplots/doc/latex/pgfplots/gallery"):
    for file in files:
        if file.startswith("example_") and file.endswith(".tex"):
            with open(os.path.join(root, file), "r") as texf:
                content = texf.read()
                file_matches = plotdata_re.findall(content)
                content = content.replace("plotdata/","") # use local folder
                root_matches = rootdata_re.findall(content)
                file_matches.extend(root_matches)
                if len(file_matches) > 0:
                    plotdata_content = ""
                    file_matches = list(set(file_matches))  # remove duplicate
                    for file_match in file_matches:
                        plotdata_file_addr = os.path.join(plotdata_addr, file_match)
                        rootdata_file_addr = os.path.join(rootdata_addr, file_match)
                        file_addr = plotdata_file_addr if os.path.exists(plotdata_file_addr) else rootdata_file_addr if os.path.exists(rootdata_file_addr) else None
                        if file_addr is None: continue
                        with open(file_addr, "r") as plotf:
                            try:
                                plotdata_content += "\\begin{filecontents*}[overwrite]{" + file_match + "}\n" + plotf.read() + "\\end{filecontents*}\n"
                            except:
                                continue
                    content = content.replace("\\begin{document}", "\\begin{document}\n" + plotdata_content)
                with open(os.path.join(dataset_name, file), "w") as dstf:
                    dstf.write(content)
            # shutil.copy(os.path.join(root, file), os.path.join(dataset_name, file))

# print("Copy dependencies to the dataset...")
# shutil.copytree("pgfplots/doc/latex/pgfplots/plotdata", os.path.join(dataset_name, "plotdata"))
# shutil.copytree("pgfplots/doc/latex/pgfplots/figures", os.path.join(dataset_name, "figures"))

print("Done.")
# print(f"You need to add ${dataset_name}/plotdata and ${dataset_name}/figures to the TEXINPUTS.")
# print(f" export TEXINPUTS=$(TEXINPUTS):${dataset_name}:")
