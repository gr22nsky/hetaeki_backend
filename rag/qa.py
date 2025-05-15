from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document as LCDocument
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from django.conf import settings
from documents.models import Document
import requests
import xml.etree.ElementTree as ET

CHROMA_PATH = "rag/chroma_documents"

# ----------- 상세내용 API 호출 로직 -----------
def fetch_detail_content(service_id: str, source: str) -> str:
    SERVICE_KEY = settings.BOKJIRO_API_KEY

    if source == "central":
        url = "https://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfaredetailedV001"
        params = {
            "serviceKey": SERVICE_KEY,
            "callTp": "D",
            "servId": service_id,
            "_type": "xml"
        }
    elif source == "local":
        url = "https://apis.data.go.kr/B554287/LocalGovernmentWelfareInformations/LcgvWelfaredetailed"
        params = {
            "serviceKey": SERVICE_KEY,
            "servId": service_id,
            "_type": "xml"
        }
    else:
        return ""

    try:
        res = requests.get(url, params=params)
        res.encoding = "utf-8"
        root = ET.fromstring(res.text)
    except Exception as e:
        print(f"❌ 상세 API 호출 실패: {service_id}, {e}")
        return ""

    if source == "central":
        return root.findtext("wantedDtl/alwServCn") or ""
    else:
        return root.findtext("alwServCn") or ""


# ----------- 벡터스토어 초기화 -----------
def get_retriever(k=5):
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY),
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})


# ----------- RAG QA 실행 -----------
def run_qa(query: str) -> str:
    retriever = get_retriever()
    docs = retriever.get_relevant_documents(query)

    # 관련 문서들의 상세 내용을 동적으로 가져옴
    extended_docs = []
    for doc in docs:
        try:
            service_id = doc.metadata.get("service_id")
            db_doc = Document.objects.get(service_id=service_id)
            detail = fetch_detail_content(service_id, db_doc.source)
            extended_content = (doc.page_content or "") + "\n" + (detail or "")
            extended_docs.append(LCDocument(page_content=extended_content, metadata={"service_id": service_id}))
        except Exception as e:
            print(f"❌ 문서 확장 실패: {doc.metadata.get('service_id')}, {e}")
            extended_docs.append(doc)

    # Prompt + LLM chain 구성
    prompt = ChatPromptTemplate.from_template("""
    너는 정부 복지 서비스에 대해 대답해주는 어시스턴트야.
    다음 정보들을 바탕으로 사용자의 질문에 정확히 답해줘:

    -----------
    {context}
    -----------

    {question}
    답변:
    """)

    chain = (
        {
            "context": lambda x: "\n\n".join([d.page_content for d in extended_docs]),
            "question": lambda x: x["question"]
        }
        | prompt
        | ChatOpenAI(temperature=0.3)
        | StrOutputParser()
    )

    return chain.invoke({"question": query})
