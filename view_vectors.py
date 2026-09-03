import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def view_tensors():
    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    index_path = os.path.join(os.path.dirname(__file__), "backend", "faiss_index")
    
    if not os.path.exists(index_path):
        print("FAISS index not found! Make sure you run the backend first.")
        return
        
    print("\nLoading FAISS Database...\n")
    vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    # Extract the underlying docstore (which holds the text) and index (which holds the vectors)
    docstore = vector_store.docstore._dict
    index = vector_store.index
    
    print(f"Total Chunks in Database: {index.ntotal}\n")
    print("="*50)
    
    # Let's look at just the very first chunk in the database
    first_id = list(docstore.keys())[0]
    document = docstore[first_id]
    
    # FAISS allows us to reconstruct the vector (tensor) for a specific ID
    # Since we added them in order, ID 0 corresponds to the first vector
    tensor = index.reconstruct(0)
    
    print("DOCUMENT CHUNK (English Text):")
    print("-" * 50)
    print(document.page_content)
    print("-" * 50)
    print(f"\nMATHEMATICAL TENSOR (Vector Representation - {len(tensor)} Dimensions):")
    print("-" * 50)
    # Print the first 20 numbers, then ..., then the last 5 numbers so it doesn't flood the screen
    formatted_tensor = f"[{tensor[0]:.4f}, {tensor[1]:.4f}, {tensor[2]:.4f}, {tensor[3]:.4f}, {tensor[4]:.4f}, {tensor[5]:.4f} ... (372 more numbers) ... {tensor[-3]:.4f}, {tensor[-2]:.4f}, {tensor[-1]:.4f}]"
    print(formatted_tensor)
    print("\n")
    print("This is exactly what the AI 'sees' when it reads that sentence!")
    print("="*50)

if __name__ == "__main__":
    view_tensors()
