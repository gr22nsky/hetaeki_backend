from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_documents")
os.makedirs(CHROMA_PATH, exist_ok=True)

class SbertEmbeddings(Embeddings):
    def __init__(self, model_name="jhgan/ko-sroberta-multitask"):
        self.model = SentenceTransformer(model_name)
    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()
    def embed_query(self, text):
        return self.model.encode([text], show_progress_bar=False, convert_to_numpy=True)[0].tolist()

def store_to_vectorstore(service_id: str, text: str):
    """주어진 텍스트를 벡터로 변환하여 Chroma 벡터스토어에 저장."""
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
    embedding = SbertEmbeddings()
    vectorstore = Chroma.from_documents(
        split_docs,
        embedding=embedding,
        persist_directory=CHROMA_PATH,
    )
    vectorstore.persist()
    print(f"✅ Vector 저장 완료: {service_id}")