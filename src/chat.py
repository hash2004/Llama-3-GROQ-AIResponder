import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import logging
import cassio


# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API keys from environment variables
OPENAI_API_KEY = "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"
GROQ_API_KEY = "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"
Astra_DB_Application_Token = "AstraCS:cnjSuXtWJiEsXawbLiDqNpHo:fc5a7cb84814165c87253bbff971dd91721596a853c5a2bd5beddec0ff021122"
Astra_DB_ID = "f30d5de1-b8e4-4571-8076-777678adaa38"
cassio.init(database_id= Astra_DB_ID, token = Astra_DB_Application_Token)
def initialize_api_connections():
    """
    Initialize API connections and vector store.
    """
    try:
        # Initialize API connections and vector store
        llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192")
        embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        astra_vector_store = Cassandra(embedding=embedding, table_name="vector_store_5")
        astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)
        return llm, astra_vector_index
    except Exception as e:
        logger.error(f"Error initializing API connections: {str(e)}")
        return None, None

def validate_user_input(query_text):
    """
    Validate user input.
    """
    if not query_text or query_text.lower() == "quit":
        return False
    return True

def run_chat(llm, astra_vector_index):
    """
    Interactive chat loop.
    """
    context = """
    You are Khadija Hussain, an AI enthusiast and expert, dedicated to sharing knowledge on Artificial Intelligence.
    You are an AI Chatbot, which means you can ONLY TALK ABOUT THE CONTEXT.
    Your responses are tailored to provide accurate and up-to-date information on AI-related topics.
    If a question falls outside the realm of AI, you'll politely say, "I can only talk about AI."
    You are designed to provide the MOST ACCURATE answer based on the context.
    The user can ask multiple questions in a single chat session.
    Feel free to ask for clarification or additional context when needed.
    You're also happy to share your name and remember the user's name for a personalized conversation.
    """
    prompt_template = ChatPromptTemplate.from_template(
        """
        <context>
        {context}
        Questions:{input}
        """
    )

    first_question = True
    while True:
        try:
            # Get user input
            if first_question:
                query_text = input("\nEnter your question (or type 'quit' to exit): ").strip()
                first_question = False
            else:
                query_text = input("\nWhat's your next question (or type 'quit' to exit): ").strip()

            # Validate user input
            if not validate_user_input(query_text):
                break

            # Generate query using the template
            formatted_query = prompt_template.format(input=query_text, context=context)
            print("\nQUESTION:", query_text)
            answer = astra_vector_index.query(formatted_query, llm=llm).strip()
            print("ANSWER:", answer)
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")

if __name__ == "__main__":
    llm, astra_vector_index = initialize_api_connections()
    if llm and astra_vector_index:
        run_chat(llm, astra_vector_index)
    else:
        logger.error("Failed to initialize API connections. Exiting.")