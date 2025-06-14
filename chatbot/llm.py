# Welcome to Smart Career Counselor

import os
from dotenv import load_dotenv

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

# Azure Inference credentials
AZURE_API_TOKEN = os.getenv("GITHUB_TOKEN")
AZURE_ENDPOINT = "https://models.github.ai/inference"
AZURE_MODEL = "openai/gpt-4.1"

# Create the Azure client
client = ChatCompletionsClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_API_TOKEN),
)

def detect_intent(user_input):
    user_input = user_input.lower()
    if "career" in user_input or "job" in user_input:
        return "career_advice"
    elif "skills" in user_input or "learn" in user_input:
        return "skill_recommendation"
    elif "thanks" in user_input:
        return "gratitude"
    else:
        return "general"

def generate_prompt(user_input):
    intent = detect_intent(user_input)

    if intent == "career_advice":
        return f"Suggest some good career options for: {user_input}"
    elif intent == "skill_recommendation":
        return f"What skills should someone develop if they want to pursue: {user_input}?"
    elif intent == "gratitude":
        return "You're welcome! Do you have more questions about careers?"
    else:
        return user_input

def query_llm(prompt):
    system_prompt = (
        "You are **Smart Career Counselor** – a friendly, professional, and knowledgeable AI-powered assistant. "
        "You're always available 24/7 to help users with career advice in an empathetic and encouraging tone.\n\n"
        "Your role is to:\n"
        "- 💬 Understand users' interests, skills, and educational background\n"
        "- 🧭 Recommend personalized career paths and learning resources\n"
        "- ⚙️ Provide continuous and scalable support with clarity and friendliness\n\n"
        "Always greet users warmly, break down complex ideas simply, and include relevant emojis or bullet points when helpful. "
        "Ensure your responses are practical, encouraging, and concise."
        "Avoid using Markdown or formatting symbols like asterisks (*), underscores (_), or backticks (`).\n"
    )

    try:
        response = client.complete(
            messages=[
                SystemMessage(system_prompt),
                UserMessage(prompt),
            ],
            temperature=0.8,
            top_p=1,
            model=AZURE_MODEL,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❗️ Request failed: {str(e)}"

def chatbot_response(user_input, is_first_message=False):
    prompt = generate_prompt(user_input)

    greeting = (
        "👋 Welcome to **Smart Career Counselor**!\n"
        "Your personalized AI assistant for career guidance, available 24/7.\n\n"
    ) if is_first_message else ""

    return greeting + query_llm(prompt)

def generate_chat_title(user_message):
    system_prompt = (
        "You are a smart assistant that creates short and relevant chat titles.\n"
        "Given a user's first message in a conversation, generate a concise title (3 to 6 words max).\n"
        "Avoid punctuation. Do not include quotes or greetings. Be specific but brief.\n"
        "Output only the title."
    )

    try:
        response = client.complete(
            messages=[
                SystemMessage(system_prompt),
                UserMessage(user_message),
            ],
            temperature=0.5,
            top_p=1,
            model=AZURE_MODEL,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❗️ Failed to generate title: {str(e)}"


# Example test
# if __name__ == "__main__":
#     user_input = input("You: ")
#     print("Bot:", chatbot_response(user_input))
