from flask import Flask

database_name = "latex_pgfplots_doctest"

file_host = Flask(__name__, static_folder=database_name)
file_host.run(host="0.0.0.0", port=3000) # global access