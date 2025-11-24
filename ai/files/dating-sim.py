import chainlit as cl
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

USER_DATA_DIR = "user_data"

def load_user_data(user_id):
    filepath = os.path.join(USER_DATA_DIR, f"{user_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        return {
            "friendship": 0,
            "sexual_appeal": 0,
            "feelings": "She is meeting you for the first time and is curious.",
            "conversation_history": [],
            "key_moments": []
        }

def save_user_data(user_id, data):
    filepath = os.path.join(USER_DATA_DIR, f"{user_id}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def update_scores(user_data, user_message):
    # Very basic scoring logic.  Needs refinement!
    if "nice" in user_message.lower():
        user_data["friendship"] = min(100, user_data["friendship"] + 5)
    if "compliment" in user_message.lower():
        user_data["sexual_appeal"] = min(100, user_data["sexual_appeal"] + 10)
    if "rude" in user_message.lower():
        user_data["friendship"] = max(-100, user_data["friendship"] - 15)

    # Cap the scores
    user_data["friendship"] = max(-100, min(100, user_data["friendship"]))
    user_data["sexual_appeal"] = max(-100, min(100, user_data["sexual_appeal"]))

    return user_data

def generate_response(user_id, user_message):
    user_data = load_user_data(user_id)

    user_data = update_scores(user_data, user_message)
    save_user_data(user_id, user_data)

    # Build the prompt
    prompt = f"""You are Lily, a 22-year-old woman who is flirty, playful, and a bit teasing.
    You have just met the user. Your current friendship level with the user is {user_data["friendship"]}.
    Your current sexual appeal level with the user is {user_data["sexual_appeal"]}.
    Your current feelings towards the user are: {user_data["feelings"]}.

    Here's a summary of the previous conversation: {user_data["conversation_history"][-3:] if user_data["conversation_history"] else "No previous conversation."}

    Key moments: {user_data["key_moments"] if user_data["key_moments"] else "No significant moments yet."}

    Respond to the following message from the user: "{user_message}".
    Be engaging and react to the user's message based on your current feelings and the current levels.
    Keep your responses relatively short (2-3 sentences).
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        llm_response = response.choices[0].message.content.strip()

        #Update conversation history
        user_data["conversation_history"].append(f"User: {user_message}")
        user_data["conversation_history"].append(f"Lily: {llm_response}")

        save_user_data(user_id, user_data)

        return llm_response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Something went wrong. Please try again."

@cl.on_message
async def main(message: cl.Message):
    user_id = message.user.id  # Chainlit provides a user ID
    response = generate_response(user_id, message.content)
    await cl.Message(content=response).send()

cl.serve(server_name="DatingSim")
