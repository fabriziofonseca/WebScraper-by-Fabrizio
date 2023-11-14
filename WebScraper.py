import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import urljoin, urlparse
import threading

class WebScraperApp:
    def __init__(self, root):
        self.root = root
        root.title("Web Scraper by Fabri")

        # URL Entry
        tk.Label(root, text="Enter URL:").grid(row=0, column=0)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1)

        # Depth Entry
        tk.Label(root, text="Enter Depth:").grid(row=1, column=0)
        self.depth_entry = tk.Entry(root, width=50)
        self.depth_entry.grid(row=1, column=1)

        # Directory Entry
        tk.Label(root, text="Select Directory:").grid(row=2, column=0)
        self.directory_entry = tk.Entry(root, width=50)
        self.directory_entry.grid(row=2, column=1)
        tk.Button(root, text="Browse", command=self.browse_directory).grid(row=2, column=2)

        # File Types
        tk.Label(root, text="Select File Types:").grid(row=3, column=0)
        self.file_types = ['pdf', 'txt', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'mp3', 'mp4', 'zip', 'rar', '7z', 'csv', 'xml', 'epub', 'mobi']
        self.file_type_vars = {}
        col = 1
        row = 3
        for file_type in self.file_types:
            var = tk.BooleanVar()
            tk.Checkbutton(root, text=file_type.upper(), variable=var).grid(row=row, column=col, sticky='w')
            self.file_type_vars[file_type] = var
            col += 1
            if col > 3:
                col = 1
                row += 1

        # Select All Button
        tk.Button(root, text="Select All", command=self.select_all_file_types).grid(row=row+1, column=0)

        # Start Button
        tk.Button(root, text="Start Scraping", command=self.start_scraping).grid(row=row+1, column=1)

        # Stop Button
        tk.Button(root, text="Stop Scraping", command=self.stop_scraping).grid(row=row+1, column=2)

        # Status Log
        tk.Label(root, text="Scraping Log:").grid(row=row+2, column=0)
        self.log = tk.Text(root, height=10, width=75)
        self.log.grid(row=row+2, column=1, columnspan=2)

        self.scraping_thread = None
        self.stop_requested = False

    def browse_directory(self):
        directory = filedialog.askdirectory()
        self.directory_entry.insert(0, directory)

    def select_all_file_types(self):
        for var in self.file_type_vars.values():
            var.set(True)

    def start_scraping(self):
        url = self.url_entry.get()
        depth = int(self.depth_entry.get())
        directory = self.directory_entry.get()
        selected_file_types = [ft for ft, var in self.file_type_vars.items() if var.get()]

        if not os.path.exists(directory):
            os.makedirs(directory)

        self.log.insert(tk.END, f"Starting scraping at {url}\n")
        self.stop_requested = False
        self.scraping_thread = threading.Thread(target=self.scrape, args=(url, directory, selected_file_types, depth, 0))
        self.scraping_thread.start()

    def stop_scraping(self):
        self.stop_requested = True
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.scraping_thread.join()
        self.log.insert(tk.END, "Scraping stopped by user.\n")

    def scrape(self, url, directory, file_types, max_depth, current_depth):
        if current_depth > max_depth or self.stop_requested:
            return

        page_content = self.get_page_content(url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')

            if 'txt' in file_types:
                self.download_text(url, directory, soup)

            # Add logic for other file types here

            # Update log
            self.log.insert(tk.END, f"Scraped {url}\n")
            self.root.update()

            # Follow internal links
            for link in soup.find_all('a', href=True):
                full_link = urljoin(url, link.get('href'))
                if urlparse(full_link).netloc == urlparse(url).netloc:
                    self.scrape(full_link, directory, file_types, max_depth, current_depth + 1)

    def get_page_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.log.insert(tk.END, f"Failed to retrieve {url}: {e}\n")
            return None

    def download_text(self, url, directory, soup):
        text = soup.get_text(separator='\n', strip=True)
        filename = urlparse(url).path.strip("/").replace("/", "_") or "index"
        filepath = os.path.join(directory, f"{filename}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        self.log.insert(tk.END, f"Downloaded text to {filepath}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
