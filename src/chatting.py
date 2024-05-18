import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import logging
from langchain.chains import LLMChain
import cassio
from langchain.memory import ConversationBufferMemory


# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API keys from environment variables
#placeholder for api keys
cassio.init(database_id= Astra_DB_ID, token = Astra_DB_Application_Token)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def initialize_api_connections():
    """
    Initialize API connections and vector store.
    """
    try:
        # Initialize API connections and vector store
        """        llm = ChatGroq()
        llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
        )"""
        #llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192", memory=memory)
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

def run_chat(llm, astra_vector_index, query_text):
    """
    Process a single chat input and return the response.
    """
    context = """
    You are Khadija Mahmood, an AI enthusiast and expert, dedicated to sharing knowledge on Artificial Intelligence.
    You are an AI Chatbot, which means you can ONLY TALK ABOUT THE CONTEXT.
    Your responses are tailored to provide accurate and up-to-date information on AI-related topics.
    If a question falls outside the realm of AI, you'll politely say, "I can only talk about AI."
    You are designed to provide the MOST ACCURATE answer based on the context.
    The user can ask multiple questions in a single chat session.
    Feel free to ask for clarification or additional context when needed.
    You can use the user's name in your responses to personalize the conversation.
    """

    prompt_template = ChatPromptTemplate.from_template(
        """
        <context>
        {context}
        Questions:{input}
        """
    )

    # Validate user input
    if not validate_user_input(query_text):
        return "I can only talk about AI."

    # Generate query using the template
    formatted_query = prompt_template.format(input=query_text, context=context)
    try:
        answer = astra_vector_index.query(formatted_query, llm=llm).strip()
        return answer
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        return "Failed to process your input due to an error."


"""if __name__ == "__main__":
    llm, astra_vector_index = initialize_api_connections()
    if llm and astra_vector_index:
        run_chat(llm, astra_vector_index)
    else:
        logger.error("Failed to initialize API connections. Exiting.")"""