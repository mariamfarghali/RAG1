from hr_policy_rag import HRPolicyRAG
import os

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")
    index_path = os.path.join(base_dir, "..", "hr_faiss_index")


    files = [
    os.path.join(data_dir, "HR_Policy_Dataset1.txt"),
    os.path.join(data_dir, "HR_Policy_Dataset2.txt")
]
    rag = HRPolicyRAG(file_paths=files, index_path=index_path)

    # Build FAISS index (only once)
    text = rag.load_documents()
    chunks = rag.split_documents(text)
    rag.build_vectorstore(chunks)

    # Load index and answer
    rag.load_vectorstore()

    while True:
        question = input("\n Ask a question (or 'exit'): ")
        if question.lower() == "exit":
            break

        result = rag.generate_adaptive_answer(question)

        print("\n Answer:")
        print(result['result'])

        print("\n Sources:")
        for doc in result['source_documents'][:3]:
            print(f"- {doc.page_content[:150]}...")
