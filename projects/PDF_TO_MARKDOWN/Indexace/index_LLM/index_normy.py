import os
import sys
import markdown
import re
from pathlib import Path
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import DirectoryLoader

# 📍 Cesta k vašim souborům
FOLDER_PATH = r"C:\Users\GercakD\OneDrive - pvs.cz\H\_NORMY\AI_priprava"
VECTOR_DB_PATH = r"C:\Users\GercakD\OneDrive - pvs.cz\H\_NORMY\AI_priprava\vectorstore"

def clean_markdown(text: str) -> str:
    """Odstraní HTML tagy z markdownu a normalizuje whitespace."""
    text = markdown.markdown(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    print("🔍 Kontrola cesty...")
    if not os.path.exists(FOLDER_PATH):
        print(f"❌ Cesta nenalezena: {FOLDER_PATH}")
        sys.exit(1)
    
    md_files = list(Path(FOLDER_PATH).rglob("*.md"))
    if not md_files:
        print("⚠️  Žádné .md soubory nenalezeny.")
        return

    print(f"📄 Načítám {len(md_files)} souborů...")
    loader = DirectoryLoader(FOLDER_PATH, glob="**/*.md", show_progress=True)
    docs = loader.load()
    
    # Filtr prázdných dokumentů
    docs = [d for d in docs if d.page_content.strip()]
    print(f"✅ Načteno {len(docs)} platných dokumentů")

    # 🔪 Rozdělení na chunky s zachováním nadpisů
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "H1"), ("##", "H2"), ("###", "H3")]
    )
    chunks = []
    for doc in docs:
        split_docs = splitter.split_text(doc.page_content)
        for sd in split_docs:
            sd.page_content = clean_markdown(sd.page_content)
            chunks.append(sd)
    
    print(f"📊 Vytvořeno {len(chunks)} chunků")

    # 🧠 Embedding model pro češtinu
    print("⏳ Načítání embedding modelu (první spuštění stáhne ~400MB)...")
    embeddings = SentenceTransformerEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    # 🗃️ Vytvoření/načtení vector store
    if os.path.exists(VECTOR_DB_PATH):
        print("🔄 Načítám existující vector store...")
        db = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        db.merge_from(chunks)
    else:
        print("🆕 Vytvářím nový vector store...")
        db = FAISS.from_documents(chunks, embeddings)

    # 💾 Uložení
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    db.save_local(VECTOR_DB_PATH)
    print(f"✅ Indexování hotovo! Vector store uloženo do: {VECTOR_DB_PATH}")
    print(f"📈 Počet vektorů: {db.index.ntotal}")

if __name__ == "__main__":
    main()
