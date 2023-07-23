Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> 
from flask import Flask, send_from_directory
from time import sleep
import os


app = Flask(__name__)

@app.route('/<path:filename>', methods=['GET'])
def serve_file_in_dir(filename):

    if not os.path.isfile(filename):
        # Returns 404 if the file does not exist
        return 'File not found', 404

    sleep(2)  # Wait 2 seconds to simulate network latency
    
    return send_from_directory('.', filename)

if __name__ == "__main__":
    app.run(port=8080)
