import json
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

JSON_PATH = "data/bokjiro_services.json"
CHROMA_PATH = "chroma_bokjiro"

def ingest_bokjiro():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        services = json.load(f)

    docs = []
    for item in services:
        content = f"{item['title']}\n\n{item.get('내용', '')}"
        metadata = {
            "지역": item.get("지역"),
            "제공주체": item.get("제공주체"),
            "지원대상": item.get("지원대상"),
            "신청방법": item.get("신청방법"),
            "문의처": item.get("문의처"),
            "원문링크": item.get("원문링크"),
        }
        docs.append(Document(page_content=content, metadata=metadata))

    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    splits = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
        persist_directory=CHROMA_PATH
    )
    vectorstore.persist()

    print(f"✅ 벡터 저장 완료: {len(splits)} chunks @ {CHROMA_PATH}")
