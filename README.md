# Web2MD - Web Content to Markdown Converter

🌐 A powerful tool to convert web content into clean, organized markdown documents.

## 🌟 Features

- 📝 Convert web pages to clean markdown
- 🔄 Process multiple URLs simultaneously
- 📚 Generate table of contents
- 🖼️ Optional image downloading
- 🔍 Smart content extraction
- 🧹 Automatic content cleaning
- 📱 Modern, user-friendly GUI
- 🔗 Handle relative and absolute URLs
- 🎯 Remove navigation menus and irrelevant elements

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Conda (Miniconda or Anaconda)

### macOS (Intel & Apple Silicon)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/web2md.git
   cd web2md
   ```

2. Run the build script:
   ```bash
   ./build_macos.sh
   ```

3. The application will be available in `dist/Web2MD.app`

### Windows

1. Clone the repository:
   ```cmd
   git clone https://github.com/yourusername/web2md.git
   cd web2md
   ```

2. Run the build script:
   ```cmd
   build_windows.bat
   ```

3. The application will be available in `dist/Web2MD.exe`

## 💻 Usage

1. Launch the application (Web2MD.app on macOS, Web2MD.exe on Windows)
2. Enter URLs in the text area (one per line)
3. Configure options:
   - Toggle image downloading
   - Toggle table of contents generation
   - Choose output directory
   - Set custom filename
4. Click "Convert" to start the process
5. Find your markdown files in the selected output directory

## 🛠️ Development

### Setting up the development environment

```bash
# Create conda environment
conda create -n web2md_new python=3.10
conda activate web2md_new

# Install dependencies
pip install -r requirements.txt
```

### Project Structure

```
web2md/
├── web2md.py          # Main application
├── build.py           # Build script
├── build_macos.sh     # macOS build automation
├── build_windows.bat  # Windows build automation
├── requirements.txt   # Python dependencies
└── resources/         # Application resources
```

## 📦 Dependencies

- requests: Web page fetching
- beautifulsoup4: HTML parsing
- markdownify: HTML to markdown conversion
- Pillow: Image handling
- tkinter: GUI framework
- PyInstaller: Application packaging

## 🔒 Security

- URL sanitization
- Safe file handling
- Network request timeouts
- Error handling
- No sensitive data exposure

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Markdownify](https://github.com/matthewwithanm/python-markdownify)
- [PyInstaller](https://www.pyinstaller.org/)

## 📞 Support

For support, please open an issue in the GitHub repository.
