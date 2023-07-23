Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> 
import os

# Create folder, if it doesn't exist
if not os.path.exists('html_files'):
    os.makedirs('html_files')

# Number of HTML files you want to create
num_files = 5

for i in range(num_files):
    # Create a new HTML file
    with open(f'html_files/page{i+1}.html', 'w') as f:
        # Write some basic HTML content in this file
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>Page {i+1}</title>
        </head>
        <body>
        <h1>This is page {i+1}</h1>
        <p>Hello, world!</p>
        </body>
        </html>
        """)

print(f"Created {num_files} HTML files.")
