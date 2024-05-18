import os
import fitz  # PyMuPDF
import time
from dotenv import load_dotenv
import nltk
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from tqdm import tqdm
import cassio

#nltk.download('punkt')

# Load environment variables
load_dotenv()
OPENAI_API_KEY = "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"
Astra_DB_Application_Token = "AstraCS:cnjSuXtWJiEsXawbLiDqNpHo:fc5a7cb84814165c87253bbff971dd91721596a853c5a2bd5beddec0ff021122"
Astra_DB_ID = "f30d5de1-b8e4-4571-8076-777678adaa38"

print("Initializing Astra DB connection....")
cassio.init(database_id= Astra_DB_ID, token = Astra_DB_Application_Token)
# PDF processing with fitz
def process_pdf(file_path):
    raw_text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            content = page.get_text()
            if content:
                raw_text += content
    return raw_text

# Advanced chunking based on sentence tokenization
def advanced_chunking(text, max_chunk_size=500):
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Function to find all PDF files in a directory
def find_pdf_files(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.lower().endswith('.pdf')]

# Main execution block
if __name__ == "__main__":
    start_time = time.time()
    directory_path = "/home/hashim/Assignments/Sem6/AI/AI-Bot/data"
    pdf_files = find_pdf_files(directory_path)
    
    texts = []
    with ThreadPoolExecutor() as executor:
        # Set up a future list for concurrent processing
        future_to_file = {executor.submit(process_pdf, pdf_file): pdf_file for pdf_file in pdf_files}
        for future in tqdm(as_completed(future_to_file), total=len(future_to_file), desc="Processing PDFs"):
            file_result = future.result()
            if file_result:
                # Perform advanced chunking on each result
                texts.extend(advanced_chunking(file_result, max_chunk_size=500))

    # Setup vector store and embedding
    embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    astra_vector_store = Cassandra(
        embedding=embedding,
        table_name="AI_Vector_Store",
        session=None,
        keyspace=None
    )

    # Add processed texts to the Cassandra vector store
    with tqdm(total=len(texts), desc="Adding texts to vector store") as pbar:
        for text_chunk in texts:
            astra_vector_store.add_texts([text_chunk])
            pbar.update(1)

    # Wrap the vector store with an index wrapper for efficient retrieval
    astra_vector_index = VectorStoreIndexWrapper(vectorstore=astra_vector_store)

    elapsed_time = time.time() - start_time
    print(f"Processing and storing completed in {elapsed_time:.2f} seconds.")
