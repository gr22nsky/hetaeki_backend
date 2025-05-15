import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_documents")
os.makedirs(CHROMA_PATH, exist_ok=True)

def store_to_vectorstore(service_id: str, text: str):
    # 1. 파일 경로 생성
    filename = f"{service_id}.txt"
    filepath = os.path.join(CHROMA_PATH, filename)

    # 2. 텍스트 저장
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text.strip())

    # 3. 문서 로드
    loader = TextLoader(filepath, encoding="utf-8")
    documents = loader.load()

    # 4. 문서 분할
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    split_docs = splitter.split_documents(documents)

    # 5. 임베딩 및 벡터스토어 저장
    vectorstore = Chroma.from_documents(
        split_docs,
        embedding=OpenAIEmbeddings(),
        persist_directory=CHROMA_PATH,
    )
    vectorstore.persist()
    print(f"✅ Vector 저장 완료: {filename}")
