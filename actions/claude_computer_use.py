import json
import sys
import time
import base64
import io
import traceback
from pathlib import Path

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
except ImportError:
    pass

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _get_base_dir()
API_KEY_PATH = BASE_DIR / "config" / "api_keys.json"

def _load_anthropic_api_key() -> str:
    try:
        with open(API_KEY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        key = data.get("anthropic_api_key", "").strip()
        if not key:
            raise ValueError("anthropic_api_key is empty in api_keys.json")
        return key
    except Exception as e:
        raise RuntimeError(f"Failed to load Anthropic API key: {e}")

def run_claude_computer_use(goal: str, player=None, speak=None) -> str:
    if Anthropic is None:
        return "Error: The 'anthropic' package is not installed. Please run 'pip install anthropic'."

    try:
        api_key = _load_anthropic_api_key()
    except Exception as e:
        return f"Error: {e}"

    if speak:
        speak("Taking control of the computer now, sir.")
    
    print(f"\n[ClaudeComputerUse] 🤖 Initiating autonomous loop for goal: {goal}")

    client = Anthropic(api_key=api_key)
    
    # We will use the primary monitor's resolution for scaling
    try:
        w, h = pyautogui.size()
    except Exception:
        w, h = 1920, 1080

    # Anthropic recommends not exceeding WXGA/FHD for cost/latency, but we'll send native for accuracy and let it scale if needed.
    # To save tokens, we might scale down to something reasonable like 1280x720, but we need to map coordinates back!
    # Let's just use the native resolution for now to ensure precise clicks.
    
    system_prompt = (
        "You are an advanced AI agent controlling a Windows computer to accomplish the user's task. "
        "You have access to the computer_20241022 tool. "
        "1. Start by taking a screenshot to see the current state. "
        "2. Make reasonable assumptions to accomplish the task efficiently. "
        "3. Once the task is fully complete, output a summary of what you did and stop."
    )

    messages = [
        {"role": "user", "content": goal}
    ]

    max_steps = 15
    
    for step in range(max_steps):
        print(f"\n[ClaudeComputerUse] 🔄 Step {step + 1}/{max_steps}")
        
        try:
            response = client.beta.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,
                tools=[
                    {
                        "type": "computer_20241022",
                        "name": "computer",
                        "display_width_px": w,
                        "display_height_px": h,
                        "display_number": 1,
                    }
                ],
                betas=["computer-use-2024-10-22"]
            )
        except Exception as e:
            err = f"API Error: {e}"
            print(f"[ClaudeComputerUse] ❌ {err}")
            return err

        # Add the assistant's response to messages
        messages.append({"role": "assistant", "content": response.content})

        tool_calls = [c for c in response.content if c.type == "tool_use"]
        text_blocks = [c for c in response.content if c.type == "text"]

        for t in text_blocks:
            print(f"[ClaudeComputerUse] 🗣️ Claude: {t.text}")

        if not tool_calls:
            print("[ClaudeComputerUse] ✅ Task complete (no more tool calls).")
            # Return the last text block as the result
            if text_blocks:
                return text_blocks[-1].text
            return "Task finished successfully."

        tool_results = []
        for tool_call in tool_calls:
            if tool_call.name == "computer":
                action = tool_call.input.get("action")
                print(f"[ClaudeComputerUse] 🖱️ Action: {action} {tool_call.input}")
                
                try:
                    result_content = _execute_computer_action(action, tool_call.input, w, h)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": result_content
                    })
                except Exception as e:
                    traceback.print_exc()
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": f"Error executing {action}: {e}",
                        "is_error": True
                    })
            else:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": f"Unknown tool: {tool_call.name}",
                    "is_error": True
                })

        messages.append({"role": "user", "content": tool_results})

    msg = f"Task stopped after reaching maximum steps ({max_steps})."
    print(f"[ClaudeComputerUse] ⚠️ {msg}")
    return msg

def _execute_computer_action(action: str, params: dict, screen_w: int, screen_h: int) -> list:
    """Execute a single computer action and return the result for Claude."""
    import pyautogui
    from PIL import ImageGrab
    
    result_text = ""
    result_image = None
    
    if action == "screenshot":
        # Capture screenshot
        img = ImageGrab.grab()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        result_image = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": b64
            }
        }
    
    elif action == "mouse_move":
        coords = params.get("coordinate", [0, 0])
        pyautogui.moveTo(coords[0], coords[1], duration=0.3)
        result_text = f"Mouse moved to {coords}"
        
    elif action == "left_click":
        pyautogui.click(button="left")
        result_text = "Left clicked"
        
    elif action == "right_click":
        pyautogui.click(button="right")
        result_text = "Right clicked"
        
    elif action == "middle_click":
        pyautogui.click(button="middle")
        result_text = "Middle clicked"
        
    elif action == "double_click":
        pyautogui.doubleClick(button="left")
        result_text = "Double clicked"
        
    elif action == "left_click_drag":
        coords = params.get("coordinate", [0, 0])
        pyautogui.dragTo(coords[0], coords[1], button="left", duration=0.5)
        result_text = f"Dragged to {coords}"
        
    elif action == "type":
        text = params.get("text", "")
        pyautogui.write(text, interval=0.02)
        result_text = f"Typed: {text}"
        
    elif action == "key":
        key = params.get("text", "")
        # Claude might send keys like "Return", "space", "ctrl+c"
        mapping = {
            "Return": "enter",
            "space": "space",
            "Tab": "tab",
            "Escape": "esc"
        }
        pyautogui_key = mapping.get(key, key.lower())
        
        if "+" in pyautogui_key:
            keys = pyautogui_key.split("+")
            pyautogui.hotkey(*[k.strip() for k in keys])
        else:
            pyautogui.press(pyautogui_key)
        result_text = f"Pressed key: {key}"
        
    elif action == "cursor_position":
        x, y = pyautogui.position()
        result_text = f"Cursor position: [{x}, {y}]"
    
    content = []
    if result_text:
        content.append({"type": "text", "text": result_text})
    if result_image:
        content.append(result_image)
        
    if not content:
        content.append({"type": "text", "text": "Action completed."})
        
    return content

def advanced_computer_use(parameters: dict, player=None, speak=None) -> str:
    """Entry point for the agent tool."""
    goal = parameters.get("goal", "")
    if not goal:
        return "Error: No goal provided for advanced_computer_use."
    return run_claude_computer_use(goal, player, speak)

if __name__ == "__main__":
    # Test script
    print(run_claude_computer_use("Open notepad, type 'hello from claude' and save it to desktop as test.txt"))
