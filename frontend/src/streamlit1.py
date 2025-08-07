import os
import shutil
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import GitLoader
from langchain_qdrant import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient
import streamlit as st

# Load environment variables
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_REPO_ID = "meta-llama/Llama-3.1-8B-Instruct"

st.set_page_config(page_title="GitHub README Generator", layout="centered")

# Inject Custom CSS
st.markdown("""
<style>
body {
    background-color: #0d0d0d;
    color: #00ff99;
    font-family: 'Courier New', monospace;
}

.stApp {
    padding: 2rem;
}

input, textarea {
    background-color: #1a1a1a !important;
    color: #00ff99 !important;
    border: 1px solid #00ff99 !important;
    font-family: 'Courier New', monospace;
}

button {
    background-color: #0f0f0f !important;
    border: 1px solid #00ff99 !important;
    color: #00ff99 !important;
    font-weight: bold;
    font-family: 'Courier New', monospace;
}

button:hover {
    background-color: #00ff99 !important;
    color: #0f0f0f !important;
    border: 1px solid #00ff99 !important;
}

h1, h2, h3, h4 {
    color: #00ff99 !important;
}

hr {
    border-color: #00ff99;
}

[data-testid="stSpinner"] > div > div {
    color: #00ff99 !important;
}
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 style="text-align:center;">🤖 GitHub README Generator</h1>', unsafe_allow_html=True)

# Input field
repo_url = st.text_input("Enter GitHub Repository URL:")

if st.button("Generate README") and repo_url:
    try:
        with st.spinner("Cloning and processing repository..."):
            collection_name = repo_url.replace("https://github.com/", "").replace("/", "_")
            temp_path = f"./temp_repos/{collection_name}"
            loader = GitLoader(
                clone_url=repo_url,
                repo_path=temp_path,
                branch="main",
                file_filter=lambda file_path: file_path.endswith((".py", ".js", ".ts", "Dockerfile", ".md", ".txt", ".json"))
            )
            docs = loader.load()
            if not docs:
                shutil.rmtree(temp_path)
                st.error("No processable files found in the repository.")
                st.stop()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            splits = text_splitter.split_documents(docs)

            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={'device': 'cpu'})
            vector_store = Qdrant.from_documents(
                splits,
                embeddings,
                url=QDRANT_URL,
                collection_name=collection_name,
                force_recreate=True
            )
            retriever = vector_store.as_retriever()

        with st.spinner("Generating README sections with LLM..."):
            client = InferenceClient(token=HF_TOKEN)
            system_prompt = """You are an expert technical writer. Your task is to generate a specific section of a GitHub README.md file based on the provided context. Be concise, professional, and use standard markdown formatting. Only output the markdown for the requested section, without any introductory text or conversational filler."""

            sections_to_generate = [
                "Project Title and Overview",
                "Key Features",
                "Installation Instructions",
                "Usage Guide"
            ]

            final_readme = ""
            for section in sections_to_generate:
                st.write(f"Generating: {section}...")
                retrieved_docs = retriever.get_relevant_documents(section)
                context = "\n\n".join([doc.page_content for doc in retrieved_docs])

                user_prompt = f"""Context from the repository:
{context}

Based on this context, please write the \"{section}\" section of the README."""

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

                section_md = ""
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        section_md += content

                final_readme += f"\n\n## {section}\n\n{section_md}"

        st.subheader(":memo: Generated README")
        st.download_button("Download README.md", final_readme, file_name="README.md")
        st.code(final_readme, language="markdown")

        shutil.rmtree(temp_path)
    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
