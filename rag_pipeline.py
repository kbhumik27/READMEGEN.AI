import os
import shutil
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import GitLoader
from langchain_qdrant import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient # Use the direct HF client

# --- Environment Variables ---
QDRANT_URL = os.getenv("QDRANT_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

# --- Configuration ---
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_REPO_ID = "meta-llama/Llama-3.1-8B-Instruct"

def generate_readme_from_repo(repo_url: str) -> str:
    """
    The main RAG pipeline function, designed to be called by a Celery worker.
    It uses the direct Hugging Face InferenceClient for robust API calls.
    """
    collection_name = repo_url.replace("https://github.com/", "").replace("/", "_")
    
    print(f"Cloning repository: {repo_url}...")
    temp_path = f"./temp_repos/{collection_name}"
    
    # NOTE: You may need to change 'main' to 'master' for older repositories.
    loader = GitLoader(
        clone_url=repo_url,
        repo_path=temp_path,
        branch="main", 
        file_filter=lambda file_path: file_path.endswith((".py", ".js", ".ts", "Dockerfile", ".md", ".txt", ".json"))
    )

    docs = loader.load()
    if not docs:
        shutil.rmtree(temp_path)
        raise ValueError("No processable files found in the repository.")
    print(f"Loaded {len(docs)} documents.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    print("Creating vector store...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={'device': 'cpu'})
    vector_store = Qdrant.from_documents(splits, embeddings, url=QDRANT_URL, collection_name=collection_name, force_recreate=True)
    retriever = vector_store.as_retriever()
    print("Vector store created successfully.")

    print("Initializing HF Inference Client...")
    client = InferenceClient(token=HF_TOKEN)
    print("Client initialized.")

    system_prompt = """You are an expert technical writer. Your task is to generate a specific section of a GitHub README.md file based on the provided context. Be concise, professional, and use standard markdown formatting. Only output the markdown for the requested section, without any introductory text or conversational filler."""

    print("Generating README sections...")
    sections_to_generate = {
        "Project Title and Overview": "Project Title and Overview",
        "Key Features": "Key Features",
        "Installation Instructions": "Installation Instructions",
        "Usage Guide": "Usage Guide"
    }
    generated_readme_parts = []
    
    for section_name in sections_to_generate.values():
        print(f"Generating section: {section_name}...")
        
        retrieved_docs = retriever.get_relevant_documents(section_name)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        user_prompt = f"""Context from the repository:
{context}

Based on this context, please write the "{section_name}" section of the README."""

        stream = client.chat.completions.create(
            model=LLM_REPO_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1024,
            temperature=0.7,
            stream=True,
        )

        full_response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
        
        generated_readme_parts.append(full_response)
        print(f"  -> Finished generating section: '{section_name}'.")

    final_readme = "\n\n".join(generated_readme_parts)
    print("Cleaning up temporary files...")
    shutil.rmtree(temp_path)
    return final_readme