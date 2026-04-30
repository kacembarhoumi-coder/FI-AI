import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np
from ingest_faiss import find_txt, load_doc, chunk_documents
from prompting import create_basic_prompt, create_shot_prompts, create_chat_prompt, format_examples
from langchain_ollama import OllamaLLM





DATA_DIR = "data/clean"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

USE_FEW_SHOT = True
if USE_FEW_SHOT:
    few_shot_prompt, examples, example_prompt = create_shot_prompts()
    formatted_examples = format_examples(examples, example_prompt)
    
    print("using the few shot prompts")
else:
    prompt = create_chat_prompt()
    formatted_examples = []
    


llm = OllamaLLM(model="qwen2:7b-instruct", temperature=0.3, timeout=120)


def build_faiss_index(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vectorstore

SIMILARITY_THRESHOLD = 0.5

def format_context(vectorestore,querry, documents, max_docs=2):
    """
    Returns context only if retrieved chunks are actually relevant.
    If nothing scores above the threshold, returns None.
    """
    results_with_scoring = vectorestore.similarity_search_with_score(querry, k=4)    
    relevant = [(doc, score)
    for doc, score in results_with_scoring
    if score < SIMILARITY_THRESHOLD
    ]
    if not relevant:
        return None

    

    context_parts = []
    for i, doc in enumerate(documents[:max_docs]):  
        source = doc.metadata.get('filename', 'unknown')
        topic = doc.metadata.get('topic', 'unknown')
        context_parts.append(f"[{source} (Topic: {topic})]\n{doc.page_content[:500]}") 
    return "\n\n".join(context_parts)


INDEX_DIR = "db/faiss"
def load_or_build_index(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )
    if os.path.exists(INDEX_DIR):
        print("loading existing index")
        vectorstore =FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(INDEX_DIR)
    return vectorstore



def main(prompt, formatted_examples):
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


    vectorstore = load_or_build_index(chunks)
    print("vector store set succefully")
    print(vectorstore)


    retriever = vectorstore.as_retriever()
    index = vectorstore.index
    

    print("\n" + "="*60)
    print("Finance Education Chatbot — ready!")
    print("Type your question below. Type 'exit' to quit.")
    print("="*60 + "\n")
    while True:
        querry = input("You: ").strip()
        if querry.lower() in ["exit","quit","bye"]:
            print("Goodbye!")
            break

        if not querry:
            print("Please enter a valid question.")
            continue

        
        results = retriever.invoke(querry)
        context = format_context(vectorstore, querry, documents)


        if context is None:
            print("no relevant context found")
            continue
            
        



        messages = prompt.format(
            examples = formatted_examples,
            context= context,
            question= querry
        )

        print("\n🤔 Generating answer...")
        print("Sending prompt to Ollama...\n")
        
        try:
            response = llm.invoke(messages)  # 2 minute timeout
            print("\n📝 ANSWER:")
            print("=" * 60)
            print(response)
        except Exception as e:
            print(f"Error generating response: {e}")
        
        
        print()

if __name__ == "__main__":
    if USE_FEW_SHOT:
        prompt, examples, example_prompt = create_shot_prompts()
        formatted_examples = format_examples(examples, example_prompt)
    else:
        prompt = create_chat_prompt()
        formatted_examples = []
    
    main(prompt, formatted_examples)    