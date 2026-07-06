import re

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove import vosk
content = re.sub(r'import vosk\n', '', content)

# Remove setup_vosk and log_voice_activation
content = re.sub(r'def log_voice_activation.*?def get_base_dir', 'def get_base_dir', content, flags=re.DOTALL)

# Modify TOOL_DECLARATIONS for go_to_sleep
old_desc = "Puts Jarvis into sleep mode. Use this when the user says 'go to sleep', 'goodbye', 'close yourself', or indicates they are done talking to you. Jarvis will stop listening until woken up again."
new_desc = "Shuts down Jarvis. Use this when the user says 'go to sleep', 'goodbye', 'close yourself', or indicates they are done talking to you. The application will completely close and wait in the background until woken up."
content = content.replace(old_desc, new_desc)

# Modify __init__
content = re.sub(r'self\.is_awake = False\s*self\.vosk_recognizer = setup_vosk\(\)\s*self\._sleep_event = asyncio\.Event\(\)', '', content)

# Modify _execute_tool for go_to_sleep
old_execute = '''        if name == "go_to_sleep":
            self.ui.write_log("SYS: Going to sleep.")
            self.is_awake = False
            self._loop.call_soon_threadsafe(self._sleep_event.set)
            result = "Going to sleep now. Goodbye!"'''
new_execute = '''        if name == "go_to_sleep":
            self.ui.write_log("SYS: Shutting down.")
            import sys
            sys.exit(0)
            result = "Going to sleep now. Goodbye!"'''
content = content.replace(old_execute, new_execute)

# Remove _wait_for_wake_word
content = re.sub(r'\s*async def _wait_for_wake_word\(self\):.*?async def run\(self\):', '\n\n    async def run(self):', content, flags=re.DOTALL)

# Remove if not self.is_awake: await self._wait_for_wake_word()
content = re.sub(r'\s*if not self\.is_awake:\s*await self\._wait_for_wake_word\(\)', '', content)

# Remove self._sleep_event.clear() from run()
content = content.replace('self._sleep_event.clear()', '')

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("main.py updated!")
