import os
from langchain_community.document_loaders import TextLoader
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path


DATA_DIR = "data/clean"


def find_txt(base_dir):
    text_file = []
    for root,_,files in os.walk(base_dir):
        for file in files:
            if file.endswith(".txt"):
                full_path = os.path.join(root,file)
                text_file.append(full_path)

    return text_file



def find_topic(path : str) -> str:
    parts = Path(path).parts
    try:
        topic = parts.index("clean") + 1
        return parts[topic]
    except (ValueError, IndexError):
        return "unknown"





    
def load_doc(file_path: list[str]) -> list[Document]:
    documents = []
    for path in file_path:
        loader = TextLoader(path)
        try:
            docs = loader.load()
        except UnicodeDecodeError as e:
            print(f"encoding error {path} is {e}")
            loader = TextLoader(path, encoding="cp1252")
            docs = loader.load()

        topic = find_topic(path)
        filename = os.path.basename(path)

        for doc in docs:
            doc.metadata["source"] = path
            doc.metadata["topic"] = topic
            doc.metadata["filename"] = filename
            documents.append(doc) 
    return documents


def chunk_documents(documents : List[Document]) -> List[Document] :
    splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100)
    chunks = splitter.split_documents(documents)
    return chunks






def main():
    print('ingestating pipline starting...')
    file_path = find_txt(DATA_DIR)
    if not file_path:
        print("!!!!!NO DOCUMENTS FOUND!!!!")
        return
    
    documents = load_doc(file_path)
    print(f"loaded{len(documents)} documents")
    print("====sample preview====")
    # for s in documents:
    #     print("content:\t")
    #     print(s.page_content[:200], "...\n")
    chunks = chunk_documents(documents)
    print(f"==the chunks created== {len(chunks)} chunks \n")
    sample = chunks[3]
    print("```sample chunck preview```")
    print(sample.page_content[:100],"...\n")
    print("metadata\n")
    for key, value in sample.metadata.items():
        print(f"{key} : {value}")


    print("=========")

if __name__ == "__main__":
    main()
