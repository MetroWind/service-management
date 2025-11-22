import os
import base64
import tomllib

import chainlit as cl
from openai import AsyncOpenAI

# --- CONFIGURATION ---

# 1. Point this to your local llama.cpp server
# Note: We use "host.docker.internal" if in docker, but "localhost" works if running natively
LLAMA_API_URL = "http://localhost:8080/v1"
LLAMA_API_KEY = "sk-dummy-key" # llama.cpp doesn't verify this by default

# 2. Define your Users (Static Configuration)
# Format: "username": "password"
def loadUsers():
    """Loads users from users.toml, or returns default users if file doesn't exist."""
    if os.path.exists("accounts.toml"):
        with open("accounts.toml", "r") as f:
            users = tomllib.load(f)
        return users
    else:
        return {"guest": "llm"}

def findSysPromptPresets():
    """Finds and loads system prompt presets from a directory.

    This function searches for markdown (.md) files in the specified directory
    and loads their content as system prompt presets. The filename (without the
    .md extension) is used as the key in the returned dictionary.

    Args:
        None

    Returns:
        A dictionary where keys are preset names (without .md extension) and
        values are the corresponding prompt content. Returns an empty dictionary
        if the directory does not exist or no .md files are found.
    """
    prompts_dir = "/opt/llm/chat/prompts"
    prompts = dict()
    if not os.path.exists(prompts_dir):
        return prompts
    for filename in os.listdir(prompts_dir):
        if not filename.endswith(".md"):
            continue
        with open(os.path.join(prompts_dir, filename), 'r') as f:
            prompts[filename[:-3]] = f.read()
    return prompts

SYS_PROMPT_PRESETS = findSysPromptPresets()
if SYS_PROMPT_PRESETS:
    DEFAULT_PRESET_NAME = min(SYS_PROMPT_PRESETS.keys())
else:
    DEFAULT_PRESET_NAME = None

# --- AUTHENTICATION LOGIC ---
@cl.password_auth_callback
def auth_callback(username, password):
    """
    Check if username/password matches the dictionary above.
    Returns a User object if valid, None if invalid.
    """
    users = loadUsers()
    if username in users and users[username] == password:
        # You can add "role" or "provider" here if you want to get fancy later
        return cl.User(identifier=username)
    return None

# --- CHAT LOGIC ---

@cl.on_chat_start
async def start():
    """
    Runs when a user logs in or refreshes the page.
    """
    # Create the OpenAI client specifically for this user session
    client = AsyncOpenAI(base_url=LLAMA_API_URL, api_key=LLAMA_API_KEY)

    # Store the client in the user session so we can reuse it
    cl.user_session.set("client", client)
    username = cl.user_session.get("user").identifier
    if username == "mw":
        available_prompt_preset_names = SYS_PROMPT_PRESETS.keys()
    else:
        available_prompt_preset_names = \
            [key for key in SYS_PROMPT_PRESETS.keys() if key != "girlfriend"]

    settings = await cl.ChatSettings(
        [
            # 1. The Preset Dropdown
            cl.input_widget.Select(
                id="system_preset",
                label="System Persona (Preset)",
                values=sorted(available_prompt_preset_names),
                initial_index=0,
            ),
            # 2. The Custom Override
            cl.input_widget.TextInput(
                id="custom_system_prompt",
                label="Custom Persona (Overrides Preset if set)",
                initial="", # Empty by default
                description="Type here to ignore the preset and use your own prompt."
            ),
            cl.input_widget.Slider(
                id="temperature",
                label="Temperature",
                initial=1.0,
                min=0,
                max=2,
                step=0.1,
            ),
        ]
    ).send()

    # Default to the first preset
    if DEFAULT_PRESET_NAME:
        default_prompt = SYS_PROMPT_PRESETS.get(DEFAULT_PRESET_NAME, "")
    else:
        default_prompt = "You are a helpful assistant."

    cl.user_session.set("settings", settings)
    message_history = []
    message_history.append({"role": "system", "content": default_prompt})
    cl.user_session.set("message_history", message_history)

    # Send a welcome message
    await cl.Message(content=f"Hello! The AI server is ready.").send()

@cl.on_settings_update
async def setup_agent(settings):
    """
    Updates the agent's system prompt based on user settings.

    This function checks if a custom system prompt is provided in the settings.
    If a custom prompt exists, it is used. Otherwise, it selects a preset system
    prompt based on the selected preset name. It then updates the message history and
    user session with the new prompt and sends a confirmation message.

    Args:
        settings (dict): A dictionary containing the user settings, including
                         'custom_system_prompt' and 'system_preset'.

    Returns:
        None
    """
    # Logic: Check Custom first. If empty, use Preset.
    custom_input = ""
    if settings["custom_system_prompt"]:
        custom_input = settings["custom_system_prompt"].strip()
    selected_preset_name = settings["system_preset"]

    if custom_input:
        new_prompt = custom_input
        source_msg = "Custom Input"
    else:
        new_prompt = SYS_PROMPT_PRESETS[selected_preset_name]
        source_msg = f"Preset: {selected_preset_name}"

    # Update History
    message_history = cl.user_session.get("message_history")
    if message_history:
        message_history[0] = {"role": "system", "content": new_prompt}

    # Update Session
    cl.user_session.set("settings", settings)
    cl.user_session.set("message_history", message_history)

    await cl.Message(content=f"✅ Persona updated using **{source_msg}**.").send()

@cl.on_message
async def main(message: cl.Message):
    """
    Runs on every message sent by the user.
    """
    client = cl.user_session.get("client")
    message_history = cl.user_session.get("message_history")
    settings = cl.user_session.get("settings")

    # Handle image uploads
    content = []
    if message.elements:
        for element in message.elements:
            if "image" in element.mime:
                # Read the image file and encode to base64
                with open(element.path, "rb") as image_file:
                    base64_image = \
                        base64.b64encode(image_file.read()).decode('utf-8')
                content.append({"type": "image_url", "image_url": {
                    "url": f"data:{element.mime};base64,{base64_image}"}})
    content.append({"type": "text", "text": message.content})
    message_history.append({"role": "user", "content": content})

    # Create a streaming message bucket
    msg = cl.Message(content="")
    await msg.send()

    # Call the Local LLM
    stream = await client.chat.completions.create(
        model="dummy", messages=message_history, stream=True,
        temperature=settings["temperature"])

    full_response_text = ""
    # Stream the response back to the UI token by token
    async for part in stream:
        if token := part.choices[0].delta.content:
            await msg.stream_token(token)
            full_response_text += token

    await msg.update()

    message_history.append({"role": "assistant", "content": full_response_text})
    cl.user_session.set("message_history", message_history)
