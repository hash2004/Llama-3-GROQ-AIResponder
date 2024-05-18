from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import logging
import re
# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API keys from environment variables
#placeholder for api keys


def initialize_api_connections_context():
    """
    Initialize API connections and vector store.
    """
    try:
        # Initialize API connections and vector store
        llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192")
        return llm
    except Exception as e:
        logger.error(f"Error initializing API connections: {str(e)}")
        return None, None

def add_context(llm, query_text):
    context = """
    You are here to help another Large Language Model(Llama) to answer questions more effectivly. 
    You are responsible to identify what specific part of the user's query should be added to the context of the conversation.
    You will recieve the user's query and you will have to identify the part of the query that should be added to the context.
    Your input MUST ONLY be the part of the query that should be added to the context.
    YOU ARE NOT DESIGNED TO BE CONVERSATIONAL.
    You are designed to ONLY remember specific details about the user itself. 
    For example, if the user says "My name is Hashim", you should return "The user's name is Hashim.".
    If the user seems to be struggling with a concept, X , you should return "The user is struggling with the concept of X.".
    If the user asks something that is not personally related to the user, you should return "0". 
    For example, if the user asks "What is the capital of France?", you should return "0".
    Another example, if the user asks "What is is my name?", you should return "0".
    RETURN 0 WHEN THE USER ASKS A QUESTION. IT COULD BE ANY TYPE OF QUESTION.
    Another example, if the user asks "I want to learn about AI.", you should return "0".
    """
    prompt_template = ChatPromptTemplate.from_template(
        """
        <context>
        {context}
        Questions:{input}
        """
    )
    try:
        #answer = llm.query(formatted_query).strip()  # Directly using LLM to query without Cassandra
        chain = prompt_template | llm
        answer = chain.invoke({"input": query_text, "context": context})
        answer  = str(answer)
        match = re.search(r'content=(["\'])(.*?)\1', answer)
        if match:
            required_part = match.group(2)
        print(required_part)
        return required_part
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
        return "Failed to process your input due to an error."


"""if __name__ == "__main__":
    llm = initialize_api_connections_context()
    if llm:
        query_text = "Talk to me about Foucault."
        context_update = add_context(llm, query_text)
        print("Context Update:", context_update)
    else:
        logger.error("Failed to initialize API connections. Exiting.")
"""

