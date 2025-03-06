from test1 import EmotionalSupportService
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def interactive_session():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    service = EmotionalSupportService.get_instance(api_key)
    user_id = "test_user"
    
    print("Chat with Joy 🌟 (type 'exit' to quit)")
    while True:
        user_message = input("\nYou: ")
        if user_message.lower() in ['quit', 'exit', 'bye']:
            break
            
        response = await service.get_support_response(user_id, user_message)
        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print(f"\nJoy 🌟: {response['response']}")

if __name__ == "__main__":
    asyncio.run(interactive_session()) 