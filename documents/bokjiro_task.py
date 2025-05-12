import os
import json
from documents.bokjiro_crawler import crawl_bokjiro
from rag.ingest_bokjiro import CHROMA_PATH
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

OLD_PATH = "data/bokjiro_services.json"
NEW_PATH = "data/bokjiro_services_latest.json"

def bokjiro_update():
    print("🔁 복지로 크롤링 시작...")
    new_data = crawl_bokjiro()
    os.makedirs("data", exist_ok=True)

    with open(NEW_PATH, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    # 기존 파일 없으면 전체 저장
    if not os.path.exists(OLD_PATH):
        os.rename(NEW_PATH, OLD_PATH)
        print("🆕 최초 데이터 저장 완료")
        return

    with open(OLD_PATH, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    old_titles = set(x["title"] for x in old_data)
    new_items = [item for item in new_data if item["title"] not in old_titles]

    if not new_items:
        print("✅ 변경된 서비스 없음")
        return

    print(f"📦 새로운 서비스 {len(new_items)}건 벡터화 시작...")

    docs = []
    for item in new_items:
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

    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=OpenAIEmbeddings()
    )
    vectorstore.add_documents(splits)
    print("✅ 벡터 추가 완료")

    # 최신 버전 저장
    os.replace(NEW_PATH, OLD_PATH)
