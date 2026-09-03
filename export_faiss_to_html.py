import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def generate_database_view():
    print("Loading FAISS Database for extraction...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    index_path = os.path.join(os.path.dirname(__file__), "backend", "faiss_index")
    
    if not os.path.exists(index_path):
        print("Error: FAISS index not found!")
        return
        
    vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    docstore = vector_store.docstore._dict
    index = vector_store.index
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FAISS Vector Database View</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 40px; }
            h1 { color: #2c3e50; text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background-color: white; }
            th, td { padding: 15px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #34495e; color: white; position: sticky; top: 0; }
            tr:hover { background-color: #f5f5f5; }
            .tensor { font-family: 'Courier New', Courier, monospace; color: #e74c3c; font-size: 0.9em; background: #fdf2f0; padding: 5px; border-radius: 4px; word-break: break-all; }
            .text-content { font-size: 0.95em; color: #333; line-height: 1.5; }
        </style>
    </head>
    <body>
        <h1>FAISS Vector Database Explorer</h1>
        <p style="text-align:center; color:#7f8c8d;">This is a visual representation of the chunks and mathematical tensors currently stored in your AI's memory.</p>
        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">ID</th>
                    <th style="width: 45%;">Document Text Chunk (What humans read)</th>
                    <th style="width: 50%;">Mathematical Tensor Vector (What the AI reads)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i, doc_id in enumerate(docstore.keys()):
        document = docstore[doc_id]
        tensor = index.reconstruct(i)
        
        # Format tensor to look neat (first 5 and last 5)
        tensor_preview = f"[{tensor[0]:.4f}, {tensor[1]:.4f}, {tensor[2]:.4f}, {tensor[3]:.4f}, {tensor[4]:.4f} ...... {tensor[-5]:.4f}, {tensor[-4]:.4f}, {tensor[-3]:.4f}, {tensor[-2]:.4f}, {tensor[-1]:.4f}] (Total: 384 dimensions)"
        
        text = document.page_content.replace('\n', '<br>')
        
        html_content += f"""
                <tr>
                    <td>{i}</td>
                    <td class="text-content">{text}</td>
                    <td class="tensor">{tensor_preview}</td>
                </tr>
        """
        
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    output_file = os.path.join(os.path.dirname(__file__), "faiss_database_view.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"SUCCESS! Database view generated at: {output_file}")
    print("Double-click that file in your file explorer to open it in your browser!")

if __name__ == "__main__":
    generate_database_view()
