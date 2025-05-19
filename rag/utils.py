from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_documents")
os.makedirs(CHROMA_PATH, exist_ok=True)

def store_to_vectorstore(service_id: str, text: str):
    # 1. Document 생성
    document = Document(
        page_content=text,
        metadata={"service_id": service_id}
    )

    # 2. 문서 분할
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    split_docs = splitter.split_documents([document])

    # 3. 벡터스토어 저장
    vectorstore = Chroma.from_documents(
        split_docs,
        embedding=OpenAIEmbeddings(),
        persist_directory=CHROMA_PATH,
    )
    vectorstore.persist()
    print(f"✅ Vector 저장 완료: {service_id}")