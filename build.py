import os
import platform
import subprocess
import sys

def build_app():
    system = platform.system()
    is_arm = platform.machine().lower().startswith(('arm', 'aarch'))
    
    # Get PyInstaller path
    pyinstaller_path = os.path.join(os.path.dirname(sys.executable), 'pyinstaller')
    
    # Base PyInstaller command
    base_command = [
        pyinstaller_path,
        '--name=Web2MD',
        '--windowed',  # No console window in production
        '--onefile',   # Single executable file
        '--clean',     # Clean PyInstaller cache
        '--noconfirm'  # Replace output directory without confirmation
    ]
    
    # Add icon based on platform
    if system == 'Darwin':  # macOS
        icon_path = os.path.join('resources', 'icon.icns')
        if os.path.exists(icon_path):
            base_command.extend(['--icon', icon_path])
        
        # Add platform-specific flags for macOS
        if is_arm:
            base_command.extend(['--target-arch', 'arm64'])
        
    elif system == 'Windows':
        icon_path = os.path.join('resources', 'icon.ico')
        if os.path.exists(icon_path):
            base_command.extend(['--icon', icon_path])
    
    # Add the main script
    base_command.append('web2md.py')
    
    print("Running PyInstaller with command:", ' '.join(base_command))
    
    # Run PyInstaller
    try:
        subprocess.run(base_command, check=True)
        print(f"\nBuild completed for {system} {'ARM' if is_arm else 'x86'}")
        print("Executable can be found in the 'dist' directory")
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_app()
