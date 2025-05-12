from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

EMBEDDING = OpenAIEmbeddings(model="text-embedding-3-small")

def index_pdf(filepath: str, persist_dir: str = "./chroma_db"):
    loader = PyPDFLoader(filepath)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(pages)

    db = Chroma.from_documents(
        documents=docs,
        embedding=EMBEDDING,
        persist_directory=persist_dir,
    )
    db.persist()
    return db