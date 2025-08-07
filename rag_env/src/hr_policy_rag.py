from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import numpy as np
from langchain.embeddings.base import Embeddings
from sklearn.metrics.pairwise import cosine_similarity
from langchain.chains import RetrievalQA
from langchain_ollama import ChatOllama
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate\




class HRPolicyRAG:
    def __init__(
        self,
        file_paths,
        model_name="all-MiniLM-L6-v2", #max context window = 128k tokens
        chunk_size=1500,               #old=500
        chunk_overlap=200,             #old=50
        index_path="hr_faiss_index"
    ):
        self.file_paths = file_paths
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.index_path = index_path

        self.embedding = HuggingFaceEmbeddings(model_name=self.model_name)
        self.retriever = None

    def load_documents(self):
        docs = []
        for path in self.file_paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    docs.append({"text": text, "source": os.path.basename(path)})
            else:
                print(f"[!] File not found: {path}")
        return docs

    def split_documents(self, docs):
        splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        all_chunks = []
        for doc in docs:
            splits = splitter.split_text(doc["text"])
            for i, chunk_text in enumerate(splits):
                chunk = Document(
                    page_content=chunk_text,
                    metadata={
                        "source": doc["source"],
                        "page": i
                    }
                )
                all_chunks.append(chunk)

        return all_chunks


    def build_vectorstore(self, chunks):
        if not chunks:
            raise ValueError("[!] No chunks to embed. Check that your documents were loaded and split.")
        print("Building vectorstore...")
        print("Example metadata:", chunks[0].metadata)  # <-- Add this to debug
        vectorstore = FAISS.from_documents(chunks, self.embedding)
        vectorstore.save_local(self.index_path)
        print("Vectorstore saved to:", self.index_path)



    def load_vectorstore(self):
        if not os.path.exists(self.index_path):
            raise ValueError(f"[!] Index path '{self.index_path}' not found. Build it first.")
        vectorstore = FAISS.load_local(
            self.index_path,
            self.embedding,
            allow_dangerous_deserialization=True  # Use only in trusted environments
        )
        self.retriever = vectorstore.as_retriever()
        print(" Vectorstore loaded and retriever ready.")

    def query(self, question, top_k=3):
        if not self.retriever:
            raise ValueError("[!] Retriever not loaded. Call load_vectorstore() first.")
        #docs = self.retriever.get_relevant_documents(question) -> deprecated
        docs = self.retriever.invoke(question)  #new method
        print(f"\n Top {top_k} chunks for: '{question}'")
        for i, doc in enumerate(docs[:top_k], 1):
            print(f"\n--- Chunk {i} ---\n{doc.page_content}")

    def is_simple_question(self, question):
        """Heuristic for checking if question is simple (yes/no, 1-hop, or short)."""
        keywords = ["how many", "when", "is", "does", "can", "are", "was", "who"]
        return any(question.lower().strip().startswith(kw) for kw in keywords) and len(question.split()) < 12

    def select_llm(self, question):
        try:
            if self.is_simple_question(question):
                print(" Using llama3 for simple question.")
                return ChatOllama(model="llama3.2:1b")
            print(" Using llama3 for complex question.")
            return ChatOllama(model="llama3.2:1b")
        except Exception as e:
            print(f"[!] Failed to load model: {e}")
            raise

    def generate_adaptive_answer(self, question):
        if not self.retriever:
            self.load_vectorstore()

        try:
            llm = self.select_llm(question)
        except Exception as e:
            return {
            "result": f"[Error selecting LLM: {e}]",
            "source_documents": []
            }

        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a professional AI assistant designed to help HR professionals and employees accurately understand HR policies.
Answer the question below using only the provided context. Do **not** include unrelated information or speculate. Your response should be:
- Direct and clear
- Formal in tone
- Brief and to the point
- Based strictly on the context
If the answer is not in the context, say: "The provided documents do not contain a clear answer to this question."
Context:
{context}
Question:
{question}
Answer:
"""
        )

        print("Running QA chain...")
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=self.retriever,
                return_source_documents=True
            )
            result = qa_chain.invoke({"query": question})

        # Extract retrieved documents
            source_docs = result.get("source_documents", [])

        # ✅ Calculate confidence score
            try:
                query_embedding = self.embedding.embed_query(question)
                doc_embeddings = [self.embedding.embed_query(doc.page_content) for doc in source_docs]

                if doc_embeddings:
                    similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
                    confidence_score = float(np.mean(similarities))  # You can use np.max(similarities) if you prefer
                else:
                    confidence_score = 0.0

            except Exception as e:
                print(f"[!] Failed to calculate confidence: {e}")
                confidence_score = 0.0

            return {
                "result": result.get("result", "[No answer returned]"),
                "source_documents": source_docs,
                "confidence": round(confidence_score, 3)  # e.g. 0.843
            }

        except Exception as e:
            return {
                "result": f"[Error during QA generation: {e}]",
                "source_documents": [],
                "confidence": 0.0
            }


