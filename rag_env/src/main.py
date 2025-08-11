from src.hr_policy_rag import HRPolicyRAG
from src.paths_config import HR_POLICY_FILE_1, HR_POLICY_FILE_2, INDEX_DIR

if __name__ == "__main__":
    # Initialize RAG system
    rag = HRPolicyRAG(
        file_paths=[HR_POLICY_FILE_1, HR_POLICY_FILE_2],
        index_path=INDEX_DIR
    )

    # Build FAISS index (only once)
    docs = rag.load_documents()
    chunks = rag.split_documents(docs)
    rag.build_vectorstore(chunks)

    # Load index and answer questions
    rag.load_vectorstore()

    while True:
        question = input("\nAsk a question (or 'exit'): ")
        if question.lower() == "exit":
            break

        result = rag.generate_adaptive_answer(question)

        print("\nAnswer:")
        print(result['result'])

        print("\nSources:")
        for doc in result['source_documents'][:3]:
            print(f"- {doc.page_content[:150]}...")
