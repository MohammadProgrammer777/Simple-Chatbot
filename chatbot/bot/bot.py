import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import langchain_core

# Load environment variables
load_dotenv()
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('API_URL')

# Create bot
class Chat():
    def __init__(self, name, chatbot, temperature=.8):
        self.name = name
        self.chatbot = chatbot
        self.temperature = temperature
        self.langModel = OpenAI(
            model=self.chatbot,
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=self.temperature,
            max_tokens=4000
        )
        self.memory = ConversationBufferMemory()
        self.chain = ConversationChain(
            llm=self.langModel,
            memory=self.memory
        )

    def ask_question(self, question):
        data = self.chain.invoke({'input': question})
        response = data['response']

        return response

    def get_chat_history(self):
        chat_history = self.memory.chat_memory.messages
        result = {'Human': [], 'AI': []}

        for message in chat_history:
            if type(message) == langchain_core.messages.human.HumanMessage:
                result['Human'].append(message.content)
            else:
                result['AI'].append(message.content)

        return result