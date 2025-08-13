

````markdown
# READMEGEN.AI

Generate high-quality GitHub README files automatically using AI and RAG (Retrieval-Augmented Generation).

This full-stack app includes:
- **Backend (Python)** for repository processing, vector indexing, and AI-based content generation.
- **Frontend (React)** for an interactive UI where users can input a repo link, trigger the pipeline, and preview/download the generated README.

---

## 🚀 Features
- **Automatic Repository Parsing** – Clones and processes supported files (`.py`, `.js`, `.ts`, `Dockerfile`, `.md`, `.txt`, `.json`).
- **Chunked Vector Indexing** – Splits code and docs into manageable pieces with `RecursiveCharacterTextSplitter`.
- **RAG Pipeline** – Uses Qdrant + HuggingFace Embeddings to retrieve the most relevant repository context.
- **LLM-Powered Generation** – Creates `README` sections using `meta-llama/Llama-3.1-8B-Instruct`.
- **React Frontend** – Simple, modern interface for easy interaction without touching the CLI.
- **Configurable** – Works with any public GitHub repo URL, and supports custom branches.

---

## 📦 Installation

### 1️⃣ Backend Setup (Python)
1. **Clone this repository**
   ```bash
   git clone https://github.com/kbhumik27/READMEGEN.AI.git
   cd READMEGEN.AI
````

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   Create a `.env` file in the root folder:

   ```env
   QDRANT_URL=http://localhost:6333
   HF_TOKEN=your_huggingface_api_token
   ```

4. **Run Qdrant** (Docker example)

   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

---

### 2️⃣ Frontend Setup (React)

1. Navigate to the frontend folder:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

---

## 🛠 Usage

### Run backend

```bash
python rag_pipeline.py
```

### Access frontend

Open your browser and go to:

```
http://localhost:3000
```

Paste any **public GitHub repo URL**, click **Generate README**, and watch it work!

---

## 🎥 Demo Video

https://drive.google.com/file/d/112fO_9lmIR-UqpsgitKDGs53deezQST9/view?usp=sharing
> Click the thumbnail above to see READMEGEN.AI in action.

---

## 🧩 Tech Stack

* **Backend:** Python, LangChain, Qdrant, Hugging Face Transformers, Docker
* **Frontend:** React.js, Axios, TailwindCSS
* **LLM:** meta-llama/Llama-3.1-8B-Instruct (via Hugging Face Inference API)

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue to discuss your ideas.

```

---
