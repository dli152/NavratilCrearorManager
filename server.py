import http.server
import socketserver
import threading
import tkinter as tk
from tkinter import messagebox
import webbrowser
import os
import requests
import json

def load_firebase_config():
    """Loads Firebase configuration from dedede.json."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "resources", "dedede.json")
        with open(file_path, "r") as f:
            config = json.load(f)
            return config.get("databaseURL"), config.get("databaseSecret")
    except FileNotFoundError:
        print("Error: dedede.json not found.")
        return None, None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in dedede.json.")
        return None, None
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return None, None

DATABASE_URL, DATABASE_SECRET = load_firebase_config()

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            if os.path.exists("pg/index.html"):
                self.path = "pg/index.html"
        elif self.path.startswith("/firebase"):
            self.handle_firebase_requests()
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def handle_firebase_requests(self):
        if self.path == "/firebase/read":
            self.read_from_firebase()
        elif self.path == "/firebase/write":
            self.write_to_firebase()
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")

    def read_from_firebase(self):
        if not DATABASE_URL or not DATABASE_SECRET:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Firebase configuration not loaded.".encode())
            return
        try:
            url = f"{DATABASE_URL}.json?auth={DATABASE_SECRET}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            else:
                self.send_response(response.status_code)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(response.content)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(str(e).encode())

    def write_to_firebase(self):
        if not DATABASE_URL or not DATABASE_SECRET:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Firebase configuration not loaded.".encode())
            return
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            url = f"{DATABASE_URL}.json?auth={DATABASE_SECRET}"
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Data written successfully".encode())
            else:
                self.send_response(response.status_code)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(response.content)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(str(e).encode())

def run_server(port):
    """Starts the local HTTP server."""
    Handler = MyHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()

def main():
    """Main function to start the server, display the address, and handle shutdown."""
    port = 8000  # You can change this port number
    server_thread = threading.Thread(target=run_server, args=(port,))
    server_thread.daemon = True
    server_thread.start()

    root = tk.Tk()
    root.title("Localhost Running")
    root.iconify()
    label = tk.Label(root, text=f"Localhost running on http://localhost:{port}")
    label.pack(padx=20, pady=20)

    url = f"http://localhost:{port}"
    messagebox.showinfo(
        "Running",
        f"The Navratil Creator Maanger Localhost is currently running on http://localhost:{port}",
        detail="The program will open automatically once you press [OK], please do not close the program window while the browser window is active.",
    )
    webbrowser.open(url)

    def on_closing():
        """Stops the server and closes the window."""
        root.destroy()
        os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()