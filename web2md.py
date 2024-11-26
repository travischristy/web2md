import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from PIL import Image
from io import BytesIO
import re
import urllib.parse
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from typing import Set, Optional, Callable
import hashlib

class Web2MD:
    def __init__(self, output_dir: str = 'output', progress_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the Web2MD converter
        
        :param output_dir: Directory to save output markdown and images
        :param progress_callback: Callback function to report progress
        """
        self.output_dir = output_dir
        self.progress_callback = progress_callback
        self.seen_content: Set[str] = set()
        os.makedirs(output_dir, exist_ok=True)
        self.images_dir = os.path.join(output_dir, 'images')
        os.makedirs(self.images_dir, exist_ok=True)

    def report_progress(self, message: str):
        """Report progress through callback if available"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

    def _sanitize_filename(self, url):
        """Create a safe filename from a URL"""
        parsed = urllib.parse.urlparse(url)
        filename = f"{parsed.netloc}_{parsed.path.replace('/', '_')}"
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        return filename[:255]

    def _is_duplicate_content(self, content: str) -> bool:
        """Check if content has been seen before using hash"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self.seen_content:
            return True
        self.seen_content.add(content_hash)
        return False

    def extract_urls(self, text: str) -> list:
        """Extract URLs from text or markdown content"""
        # Match markdown links [text](url)
        markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        markdown_urls = re.findall(markdown_pattern, text)
        urls = [url for _, url in markdown_urls]

        # Match plain URLs
        url_pattern = r'(?<![\(\[])(https?://[^\s\)\]]+)'
        plain_urls = re.findall(url_pattern, text)
        urls.extend(plain_urls)

        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls

    def download_image(self, img_url, base_url):
        """Download an image and save it locally"""
        try:
            if img_url.startswith('//'):
                img_url = f'https:{img_url}'
            elif img_url.startswith('/'):
                parsed_base = urllib.parse.urlparse(base_url)
                img_url = f'{parsed_base.scheme}://{parsed_base.netloc}{img_url}'
            
            if not img_url.startswith(('http://', 'https://')):
                return None

            response = requests.get(img_url, timeout=10)
            response.raise_for_status()
            
            img_filename = self._sanitize_filename(img_url) + '.jpg'
            img_path = os.path.join(self.images_dir, img_filename)
            
            with open(img_path, 'wb') as f:
                f.write(response.content)
            
            return img_filename
        except Exception as e:
            self.report_progress(f"Error downloading image {img_url}: {e}")
            return None

    def clean_markdown(self, content: str) -> str:
        """Clean up markdown content"""
        # Remove empty sections
        content = re.sub(r'#+ [^\n]+\n\s*(?=\n|$)', '', content)
        # Remove duplicate newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        # Remove navigation menus
        content = re.sub(r'(\+ \[FAQ\].*?(?=\n\n|\Z))', '', content, flags=re.DOTALL)
        return content.strip()

    def convert_url_to_markdown(self, url: str, download_images: bool = True) -> str:
        """Convert a webpage to markdown"""
        try:
            self.report_progress(f"Processing {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the page title
            title = soup.title.string if soup.title else url
            # Clean up the title (remove common suffixes, etc)
            title = re.sub(r'\s*[|]-.*$', '', title)  # Remove everything after | or -
            title = title.strip()
            
            # Remove unwanted elements
            for element in soup.select('nav, footer, .navigation, .menu, script, style'):
                element.decompose()
            
            # Convert to markdown
            markdown_content = markdownify(str(soup), heading_style="ATX")
            
            # Skip if duplicate content
            if self._is_duplicate_content(markdown_content):
                self.report_progress(f"Skipping duplicate content from {url}")
                return ""
            
            # Handle images if requested
            if download_images:
                images = soup.find_all('img')
                for img in images:
                    img_url = img.get('src')
                    if img_url:
                        local_img_path = self.download_image(img_url, url)
                        if local_img_path:
                            markdown_content = markdown_content.replace(img_url, local_img_path)
            else:
                # Remove image references when not downloading
                markdown_content = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', markdown_content)
            
            # Add title as heading
            markdown_content = f"# {title}\n\n{self.clean_markdown(markdown_content)}"
            
            return markdown_content
            
        except Exception as e:
            self.report_progress(f"Error processing {url}: {e}")
            return f"# Error Converting {url}\n\n{str(e)}"

    def generate_toc(self, markdown_content: str) -> str:
        """Generate a table of contents from markdown headings"""
        lines = markdown_content.split('\n')
        toc_lines = ['# Table of Contents\n']
        headers = []
        current_section = None
        
        # First pass: collect all headers
        for line in lines:
            if line.startswith('#'):
                # Count the heading level and get the text
                hashes = re.match(r'^#+', line).group()
                level = len(hashes)
                heading = line[level:].strip()
                
                # Skip empty headings and the TOC title itself
                if not heading or heading == "Table of Contents":
                    continue
                
                # Create an anchor link
                anchor = re.sub(r'[^\w\s-]', '', heading.lower())
                anchor = re.sub(r'[-\s]+', '-', anchor).strip('-')
                
                # Track main sections (h1) and their subsections
                if level == 1:
                    current_section = heading
                    headers.append((level, heading, anchor, None))
                else:
                    headers.append((level, heading, anchor, current_section))
        
        # Second pass: build TOC with proper indentation
        current_section = None
        for level, heading, anchor, section in headers:
            # Handle section changes
            if section != current_section and section is not None:
                if current_section is not None:
                    toc_lines.append('')  # Add blank line between sections
                current_section = section
            
            # Add to TOC with proper indentation
            indent = '    ' * (level - 1)  # Indent based on header level
            toc_lines.append(f"{indent}- [{heading}](#{anchor})")
        
        # Only add TOC if we found headers
        if len(toc_lines) > 1:  # More than just the "Table of Contents" line
            return '\n'.join(toc_lines) + '\n\n---\n\n'
        else:
            return ''

    def convert_urls_to_markdown(self, urls: list, output_filename: str = 'combined_output.md',
                               download_images: bool = True, include_toc: bool = False) -> None:
        """Convert multiple URLs to a single markdown file"""
        all_content = []
        
        for url in urls:
            content = self.convert_url_to_markdown(url, download_images)
            if content:
                all_content.append(content)
        
        if not all_content:
            self.report_progress("No content was generated from the provided URLs")
            return
        
        # Join all content with separators
        combined_content = '\n\n---\n\n'.join(all_content)
        
        # Add table of contents if requested and headers were found
        if include_toc:
            toc = self.generate_toc(combined_content)
            if toc:  # Only add if TOC was generated
                combined_content = toc + combined_content
        
        output_path = os.path.join(self.output_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(combined_content)
        
        self.report_progress(f"Markdown file saved to {output_path}")

class Web2MDGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Web2MD Converter")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URLs input
        ttk.Label(main_frame, text="Paste text containing URLs (markdown format supported):").grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.urls_text = scrolledtext.ScrolledText(main_frame, height=10)
        self.urls_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Extracted URLs preview
        ttk.Label(main_frame, text="Extracted URLs:").grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.extracted_urls_text = scrolledtext.ScrolledText(main_frame, height=5)
        self.extracted_urls_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Extract URLs button
        self.extract_button = ttk.Button(main_frame, text="Extract URLs", 
                                       command=self.preview_urls)
        self.extract_button.grid(row=4, column=0, sticky=tk.W)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Download images checkbox
        self.download_images_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Download Images", 
                       variable=self.download_images_var).grid(row=0, column=0, sticky=tk.W)
        
        # Table of Contents checkbox
        self.include_toc_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Table of Contents", 
                       variable=self.include_toc_var).grid(row=0, column=1, sticky=tk.W)
        
        # Output directory selection
        ttk.Label(options_frame, text="Output Directory:").grid(row=1, column=0, sticky=tk.W)
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), 'output'))
        self.output_entry = ttk.Entry(options_frame, textvariable=self.output_dir)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(options_frame, text="Browse", 
                  command=self.choose_output_dir).grid(row=1, column=2, sticky=tk.W)
        
        # Output filename
        ttk.Label(options_frame, text="Output Filename:").grid(row=2, column=0, sticky=tk.W)
        self.output_filename = tk.StringVar(value='combined_output.md')
        self.filename_entry = ttk.Entry(options_frame, textvariable=self.output_filename)
        self.filename_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Configure options_frame grid
        options_frame.columnconfigure(1, weight=1)
        
        # Progress output
        ttk.Label(main_frame, text="Progress:").grid(row=6, column=0, sticky=tk.W)
        self.progress_text = scrolledtext.ScrolledText(main_frame, height=10)
        self.progress_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Submit button
        self.submit_button = ttk.Button(main_frame, text="Convert to Markdown", 
                                      command=self.start_conversion)
        self.submit_button.grid(row=8, column=0, sticky=tk.W)
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def choose_output_dir(self):
        """Open directory chooser dialog"""
        directory = filedialog.askdirectory(
            initialdir=self.output_dir.get(),
            title="Select Output Directory"
        )
        if directory:
            self.output_dir.set(directory)
    
    def preview_urls(self):
        """Extract and preview URLs from input text"""
        input_text = self.urls_text.get("1.0", tk.END)
        converter = Web2MD()
        urls = converter.extract_urls(input_text)
        
        self.extracted_urls_text.delete("1.0", tk.END)
        if urls:
            self.extracted_urls_text.insert(tk.END, "\n".join(urls))
        else:
            self.extracted_urls_text.insert(tk.END, "No URLs found in the input text")
    
    def report_progress(self, message: str):
        """Update progress in GUI"""
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        input_text = self.urls_text.get("1.0", tk.END)
        converter = Web2MD()
        urls = converter.extract_urls(input_text)
        
        if not urls:
            messagebox.showerror("Error", "No URLs found in the input text")
            return
        
        # Validate output directory
        output_dir = self.output_dir.get()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        # Validate filename
        filename = self.output_filename.get()
        if not filename.endswith('.md'):
            filename += '.md'
            self.output_filename.set(filename)
        
        self.submit_button.state(['disabled'])
        self.extract_button.state(['disabled'])
        self.progress_text.delete("1.0", tk.END)
        
        def conversion_thread():
            try:
                converter = Web2MD(
                    output_dir=output_dir,
                    progress_callback=self.report_progress
                )
                converter.convert_urls_to_markdown(
                    urls,
                    output_filename=filename,
                    download_images=self.download_images_var.get(),
                    include_toc=self.include_toc_var.get()
                )
                self.report_progress("Conversion completed!")
                
                # Show the output file location
                full_path = os.path.join(output_dir, filename)
                self.report_progress(f"Output saved to: {full_path}")
                
            except Exception as e:
                self.report_progress(f"Error: {str(e)}")
            finally:
                self.submit_button.state(['!disabled'])
                self.extract_button.state(['!disabled'])
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    gui = Web2MDGUI()
    gui.run()

if __name__ == '__main__':
    main()
