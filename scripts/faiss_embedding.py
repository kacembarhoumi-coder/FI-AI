import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np
from ingest_faiss import find_txt, load_doc, chunk_documents
from prompting import create_basic_prompt, create_shot_prompts, create_chat_prompt
from langchain_ollama import OllamaLLM





DATA_DIR = "data/clean"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

USE_FEW_SHOT = True
if USE_FEW_SHOT:
    few_shot_promt, examples, example_prompt = create_shot_prompts()
    print("using the prompts")
    prompt = create_chat_prompt()
    print("using basic chat prompt for user")
else:
    prompt = create_chat_prompt


llm = OllamaLLM(model="qwen2:7b-instruct", temperature=0.3)


def build_faiss_index(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vectorstore



def format_context(documents, max_docs=2):  # Limit to top 2 results
    context_parts = []
    for i, doc in enumerate(documents[:max_docs]):  # Only use first 2 docs
        source = doc.metadata.get('filename', 'unknown')
        topic = doc.metadata.get('topic', 'unknown')
        context_parts.append(f"[{source} (Topic: {topic})]\n{doc.page_content[:500]}")  # Limit content
    
    return "\n\n".join(context_parts)





def main():
    print("building faiss vector begins")
    file_path = find_txt(DATA_DIR)
    if not file_path:
        print("no file found")
        return
    documents = load_doc(file_path)
    documents = documents
    chunks = chunk_documents(documents)
    print(f"loaded documents {len(documents)}")
    print(f"loade chunks {(len(chunks))}")


    vectorstore = build_faiss_index(chunks)
    print("vector store set succefully")
    print(vectorstore)


    retriever = vectorstore.as_retriever()
    index = vectorstore.index
    

    querry = "what is yassin?"
    results = retriever.invoke(querry)
    
    print("\n test querry:", querry,"?")
    r = results[0]

    print(r.page_content)
    print("==============\n=============\n===============")
    for key,value in r.metadata.items():
        print(f"{key} : {value}")
    
    context = format_context(results)

    messages = prompt.format(
        context= context,
        question= querry
    )

    print("\n🤔 Generating answer...")
    print("Sending prompt to Ollama...\n")
    
    try:
        response = llm.invoke(messages, timeout=120)  # 2 minute timeout
        print("\n📝 ANSWER:")
        print("=" * 60)
        print(response)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Tip: Try a smaller model like 'qwen2:7b-instruct'")
    


if __name__ == "__main__":
    main()