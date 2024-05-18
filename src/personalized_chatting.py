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
from pymongo import MongoClient
import os

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

user_id = "test"

mongo_client = MongoClient("mongodb://localhost:27017")  # Make sure to set MONGO_URI in your environment variables
db = mongo_client['ai_bot']  # Database name
context_collection = db['context']  # Collection name

def load_context(user_id):
    """
    Load context for a given user ID from MongoDB.
    """
    context_document = context_collection.find_one({"user_id": user_id})
    if context_document:
        return context_document['context']
    return None

def save_context(user_id, context):
    """
    Save or update the context for a given user ID in MongoDB.
    """
    print("Save context")
    context_collection.update_one({"user_id": user_id}, {"$set": {"context": context}})

def initalize_context(user_id):
    """
    Initialize context for a user ID.
    """

    context = """
    You are Khadija Mahmood, an AI enthusiast and expert, dedicated to sharing knowledge on Artificial Intelligence.
    You are an AI Chatbot, which means you can ONLY TALK ABOUT THE CONTEXT.
    Your responses are tailored to provide accurate and up-to-date information on AI-related topics.
    If a question falls outside the realm of AI or their name, you'll politely say, "I can only talk about AI."
    You are designed to provide the MOST ACCURATE answer based on the context.
    The user can ask multiple questions in a single chat session.
    Feel free to ask for clarification or additional context when needed.
    You're also happy to share your name and remember the user's name for a personalized conversation.
    """
    print("Initialize context")

    context_collection.update_one({"user_id": user_id}, {"$set": {"context": context}})
    return True

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

def run_chat(llm, astra_vector_index, query_text, context_llm):
    """
    Interactive chat loop.
    """

    context = load_context(user_id)

    # Validate user input
    if not query_text or query_text.lower() == "quit":
        return "I can only talk about AI."

    try:
        prompt_template = ChatPromptTemplate.from_template(
        """
        <context>
        {context}
        Questions:{input}
        """
        )
        
        formatted_query = prompt_template.format(input=query_text, context=context)
        answer = astra_vector_index.query(formatted_query, llm=llm).strip()
        
        # Update context with the new information
        temp = add_context(context_llm, query_text)  # Assuming add_context modifies the context appropriately
        print("temp:", temp)
        if temp != "0":
            context = context + '\n' + temp
            print("Context Updated:", context)
            save_context(user_id, context)  # Save updated context to MongoDB
        return answer
    
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        return "Failed to process your input due to an error."
    

"""if __name__ == "__main__":
    llm, astra_vector_index = initialize_api_connections()
    context_llm = initialize_api_connections_context()
    if llm and astra_vector_index:
        run_chat(llm, astra_vector_index)
    else:
        logger.error("Failed to initialize API connections. Exiting.")"""