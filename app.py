import os
import markdown
from jinja2 import Environment, FileSystemLoader
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading
from flask import Flask, send_from_directory, abort, redirect

app = Flask(__name__)

# Specify the directory to serve files from
CDN_DIRECTORY = 'output'  # Change this to your desired directory

def safe_join(directory, path):
    # Join the directory and the requested path
    final_path = os.path.join(directory, path)
    
    # Ensure the final path is within the directory
    if os.path.commonprefix([final_path, directory]) == directory:
        return final_path
    return None

@app.route("/")
def route():
    return redirect("/index.html")

@app.route('/<path:filename>')
def serve_file(filename):
    try:
        # Safely join the directory and filename
        file_path = safe_join(CDN_DIRECTORY, filename)

        # Check if the file path is valid and the file exists
        if file_path is None or not os.path.isfile(file_path):
            abort(404)  # File not found

        # Serve the file from the specified directory
        return send_from_directory(CDN_DIRECTORY, filename)
    except Exception as e:
        # Handle exceptions (e.g., file not found, security issues)
        abort(404)

# Paths
CONTENT_DIR = 'content'
OUTPUT_DIR = 'output'
TEMPLATE_DIR = 'templates'

# Set up Jinja2 for templating
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template('base.html')

# Function to generate HTML from Markdown
def generate_html(md_file):
    with open(md_file, 'r') as f:
        text = f.read()
        # Convert markdown to HTML
        html_content = markdown.markdown(text)
    return html_content

# Function to get metadata from Markdown file (e.g., title)
def extract_metadata(md_file):
    metadata = {}
    with open(md_file, 'r') as f:
        lines = f.readlines()
        if lines[0].startswith('# '):  # Assume title is the first line with '#'
            metadata['title'] = lines[0].strip('# ').strip()
        else:
            metadata['title'] = 'Untitled'
    return metadata

# Generate the entire static site
def generate_site():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Iterate over all markdown files in the content directory
    for md_file in os.listdir(CONTENT_DIR):
        if md_file.endswith('.md'):
            # Convert markdown to HTML
            md_path = os.path.join(CONTENT_DIR, md_file)
            html_content = generate_html(md_path)

            # Get metadata (title, etc.)
            metadata = extract_metadata(md_path)

            # Render the HTML file with the template
            output_html = template.render(title=metadata['title'], content=html_content)

            # Write the HTML file to the output directory
            output_filename = md_file.replace('.md', '.html')
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            # Only write the HTML file if it doesn't exist or if the content has changed
            if not os.path.isfile(output_path):
                with open(output_path, 'w') as f:
                    f.write(output_html)
                print(f'Generated {output_filename}')
            else:
                # Read the existing HTML content
                with open(output_path, 'r') as f:
                    existing_content = f.read()

                # Update the file only if the content is different
                if existing_content != output_html:
                    with open(output_path, 'w') as f:
                        f.write(output_html)
                    print(f'Updated {output_filename}')
                else:
                    print(f'{output_filename} is up-to-date, skipping...')

# File system event handler
class WatcherHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            print(f"Detected changes in {event.src_path}. Regenerating site...")
            generate_site()

# Function to start watching the directory
def watch():
    observer = Observer()
    event_handler = WatcherHandler()
    observer.schedule(event_handler, CONTENT_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    generate_site()
    # Start the file watcher in a separate thread
    watch_thread = threading.Thread(target=watch)
    watch_thread.daemon = True  # Daemonize thread
    watch_thread.start()

    # Start the Flask application
    app.run(port=5000)  # You can change the port if needed
