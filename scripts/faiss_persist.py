from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from ingest_faiss import find_txt, load_doc, chunk_documents

DATA_DIR = "data/clean"
INDEX_DIR = "db/faiss"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def main ():
    path = find_txt(DATA_DIR)
    if not path:
        print("no documents found")
        return
    doc = load_doc(path)
    chunks = chunk_documents(doc)
    embeddings = HuggingFaceBgeEmbeddings(model_name = EMBEDDING_MODEL)
    vectordb = FAISS.from_documents(chunks,embeddings)
    vectordb.save_local(INDEX_DIR)
    print(f"vectors saved in {INDEX_DIR}")
if __name__ == "__main__":
    main()