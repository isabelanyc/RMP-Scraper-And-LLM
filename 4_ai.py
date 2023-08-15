import os
import sys
import gradio
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator

# Load the environment variables from the .env file
load_dotenv()

# Set the OPENAI_API_KEY environment variable with the API key from the .env file
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def ChatBot(query):
    # Enable to save to disk & reuse the model (for repeated queries on the same data)
    
    loader = DirectoryLoader("data/")
    index = VectorstoreIndexCreator().from_loaders([loader])

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-3.5-turbo"),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )

    chat_history = []
    result = chain({"question": query, "chat_history": chat_history})
    return result['answer']

demo = gradio.Interface(fn=ChatBot, inputs='text', outputs='text', title='Rate My Professor w/ GPT3.5')
demo.launch()