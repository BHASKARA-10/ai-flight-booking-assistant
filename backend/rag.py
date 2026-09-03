import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Global variable to hold the vector store in memory
vector_store = None

def get_vector_store():
    global vector_store
    if vector_store is not None:
        return vector_store
        
    print("Loading embedding model and initializing FAISS database...")
    # Initialize embeddings (downloads a tiny lightweight model locally ~80MB)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    index_path = os.path.join(os.path.dirname(__file__), "faiss_index")
    
    # If the database already exists on the hard drive, just load it!
    if os.path.exists(index_path):
        print("Loading existing FAISS database from disk...")
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        return vector_store
        
    print("Creating new FAISS database from scratch...")
    # Load the PDF file
    data_path = os.path.join(os.path.dirname(__file__), "data", "Company_Travel_Policy.pdf")
    if not os.path.exists(data_path):
        return None
        
    loader = PyPDFLoader(data_path)
    docs = loader.load()
    
    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(docs)
    
    # Create the FAISS database from chunks
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # SAVE IT TO DISK so the user can see it!
    vector_store.save_local(index_path)
    print("FAISS database saved to disk successfully!")
    return vector_store

def search_policy(query: str, k: int = 2) -> str:
    """Search the FAISS vector database for relevant policies."""
    try:
        vs = get_vector_store()
        if not vs:
            return "Error: Knowledge base file not found."
            
        # Retrieve the most relevant chunks using Vector Similarity Search
        results = vs.similarity_search(query, k=k)
        
        if not results:
            return "No relevant policies found in the knowledge base."
            
        # Combine the chunk contents
        context = "\n\n".join([doc.page_content for doc in results])
        return f"Found the following information in the official policy document:\n\n{context}"
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"
