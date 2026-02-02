import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np
from ingest_faiss import find_txt, load_doc, chunk_documents
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


DATA_DIR = "data/clean"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"



def build_faiss_index(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    return vectorstore

def main():
    print("building faiss vector begins")
    file_path = find_txt(DATA_DIR)
    if not file_path:
        print("no file found")
        return
    documents = load_doc(file_path)
    documents = documents * 10
    chunks = chunk_documents(documents)
    print(f"loaded documents {len(documents)}")
    print(f"loade chunks {(len(chunks))}")


    vectorstore = build_faiss_index(chunks)
    print("vector store set succefully")
    print(vectorstore)


    retriever = vectorstore.as_retriever()
    index = vectorstore.index
    # vectors = np.zeros((index.ntotal, index.d), dtype="float32")
    # index.reconstruct_n(0,index.ntotal, vectors)
    # tsne = TSNE(n_components=2, perplexity=4, random_state=42)
    # vectors_2d = tsne.fit_transform(vectors)    
    # labels = []
    # texts=[]

    # for i in range (index.ntotal):
    #     doc_id = vectorstore.index_to_docstore_id[i]
    #     doc = vectorstore.docstore.search(doc_id)
    #     labels.append(doc.metadata.get("topic", "unknown"))
    #     texts.append(doc.page_content[:100])    
        
    # pca = PCA(n_components=3)
    # vectors_pca = pca.fit_transform(vectors)
    
    # import matplotlib.pyplot as plt

    # plt.figure(figsize=(10, 7))

    # unique_labels = list(set(labels))
    # colors = plt.cm.tab10(range(len(unique_labels)))

    # for label, color in zip(unique_labels, colors):
    #     idxs = [i for i, l in enumerate(labels) if l == label]
    #     plt.scatter(
    #         vectors_2d[idxs, 0],
    #         vectors_2d[idxs, 1],
    #         label=label,
    #         color=color,
    #         alpha=0.7
    #     )

    # plt.legend()
    # plt.title("PCA visualization of document embeddings")
    # plt.xlabel("PC1")
    # plt.ylabel("PC2")
    # plt.show()






    querry = "is day trading effective?"
    results = retriever.invoke(querry)
    
    print("\n test querry:", querry,"?")
    r = results[1]

    print(r.page_content)
    print("==============\n=============\n===============")
    for key,value in r.metadata.items():
        print(f"{key} : {value}")
    
    
    
    
if __name__ == "__main__":
    main()