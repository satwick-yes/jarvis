import os
import sys

def main():
    print("Setting up Jarvis to run on Windows startup...")
    
    # Get the Windows startup folder
    appdata = os.getenv("APPDATA")
    if not appdata:
        print("Error: Could not find APPDATA environment variable.")
        return
        
    startup_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    
    # Check if the folder exists
    if not os.path.exists(startup_dir):
        print(f"Error: Startup directory does not exist at {startup_dir}")
        return
        
    # Get the paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    wake_script = os.path.join(script_dir, "wake_word_listener.py")
    
    # Path for the pythonw executable (runs python scripts without a console window)
    pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        # Fallback if pythonw.exe isn't adjacent to python.exe (e.g. in some virtualenvs)
        pythonw_exe = "pythonw" 
        
    vbs_path = os.path.join(startup_dir, "jarvis_wake_word.vbs")
    
    # Create the VBScript content
    # We use chr(34) to properly enclose the paths in quotes in VBScript
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "{pythonw_exe}" & chr(34) & " " & chr(34) & "{wake_script}" & chr(34), 0, False
'''
    
    # Write the VBScript to the Startup folder
    try:
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_content)
            
        print(f"Successfully added Jarvis Wake Word listener to Windows Startup!")
        print(f"   Startup script created at: {vbs_path}")
        print("\nJarvis will now start the background listener automatically every time you boot your PC.")
        print("You can test the listener now by running: python wake_word_listener.py")
    except Exception as e:
        print(f"Failed to create startup script: {e}")

if __name__ == "__main__":
    main()
