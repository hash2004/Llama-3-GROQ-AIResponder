import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import logging
from context import add_context, initialize_api_connections_context
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

# Initialize context dictionary
context_dict = {}

def initialize_api_connections():
    """
    Initialize API connections and vector store.
    """
    try:
        # Initialize API connections and vector store
        llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192")
        embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        astra_vector_store = Cassandra(embedding=embedding, table_name="ai_vector_store")
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
    You are Khadija Mahmood, an AI enthusiast and expert, dedicated to sharing knowledge on Artificial Intelligence.
    You are an AI Chatbot, which means you can ONLY TALK ABOUT THE CONTEXT.
    Your responses are tailored to provide accurate and up-to-date information on AI-related topics.
    You are designed to provide the MOST ACCURATE answer based on the context.
    The user can ask multiple questions in a single chat session.
    Feel free to ask for clarification or additional context when needed.
    You are allowed to talk answer when the user asks personal details about themselves.
    """
   

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

            prompt_template = ChatPromptTemplate.from_template(
                """
                <context>
                {context}
                Questions:{input}
                """
            )

            # Generate query using the template
            formatted_query = prompt_template.format(input=query_text, context=context)
            print("\nQUESTION:", query_text)
            answer = astra_vector_index.query(formatted_query, llm=llm).strip()
            print("ANSWER:", answer)

            # Update context dictionary with answer
            temp = add_context(context_llm, query_text)
            print ("The temp is:", temp)
            if isinstance(temp, str):
                if temp is not "0":
                    context = context + '\n' + temp
                    print("CONTEXT:", context)
                else:
                    print("No context to add.")
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")

if __name__ == "__main__":
    llm, astra_vector_index = initialize_api_connections()
    context_llm = initialize_api_connections_context()
    if llm and astra_vector_index:
        run_chat(llm, astra_vector_index)
    else:
        logger.error("Failed to initialize API connections. Exiting.")