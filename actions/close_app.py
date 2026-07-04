import subprocess

def close_app(parameters: dict, player=None) -> str:
    """
    Closes a running application or process by name.
    """
    app_name = parameters.get("app_name")
    if not app_name:
        return "Error: No app_name provided to close."
        
    if player:
        player.write_log(f"SYS: Closing app: {app_name}")

    try:
        # We run via powershell to stop the process
        # Using Stop-Process with -ErrorAction SilentlyContinue to avoid long red errors if not found
        ps_command = f"Get-Process '{app_name}' -ErrorAction SilentlyContinue | Stop-Process -Force"
        
        # Also try to close by window title just in case
        ps_command_title = f"Get-Process | Where-Object {{$_.MainWindowTitle -match '{app_name}'}} | Stop-Process -Force"
        
        full_command = f"{ps_command}; {ps_command_title}"
        
        result = subprocess.run(
            ["powershell", "-Command", full_command],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        error = result.stderr.strip()
        if error and "Stop-Process" in error:
             return f"Attempted to close {app_name}, but encountered an error: {error}"
             
        return f"Successfully issued close command for '{app_name}'."
    except Exception as e:
        return f"Error closing app '{app_name}': {e}"
