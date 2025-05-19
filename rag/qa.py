from langchain_openai import OpenAIEmbeddings
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
import os

CHROMA_PATH = "rag/chroma_documents"

# ----------- 상세내용 API 호출 로직 -----------
def fetch_detail_content(service_id: str, source: str) -> str:
    SERVICE_KEY = os.getenv("BOKJIRO_API_KEY")

    if source == "central":
        url = "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001/NationalWelfaredetailedV001"
        params = {
            "serviceKey": SERVICE_KEY,
            "callTp": "D",
            "servId": service_id,
            "_type": "xml"
        }
    elif source == "local":
        url = "http://apis.data.go.kr/B554287/LocalGovernmentWelfareInformations/LcgvWelfaredetailed"
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

        if source == "central":
                detail = root.find("wantedDtl")
        else:
            detail = root
        return ET.tostring(detail, encoding="unicode", method="xml") if detail is not None else ""
    except Exception as e:
        print(f"❌ 상세 API 호출 실패: {service_id}, {e}")
        return ""

# ----------- 벡터스토어 초기화 -----------
def get_retriever(k=1):
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY),
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})


# ----------- RAG QA 실행 -----------
def run_qa(query: str) -> str:
    retriever = get_retriever()
    docs = retriever.invoke(query)

    # 관련 문서들의 상세 내용을 동적으로 가져옴
    extended_docs = []
    for doc in docs:
        try:
            service_id = doc.metadata.get("service_id")
            db_doc = Document.objects.get(service_id=service_id)
            source = db_doc.source
            detail = fetch_detail_content(service_id, db_doc.source)
            extended_content = f"[출처: {source}]\n[요약]\n{doc.page_content}\n\n[상세설명]\n{detail}"
            extended_docs.append(LCDocument(page_content=extended_content, metadata={"service_id": service_id}))
        except Exception as e:
            print(f"❌ 문서 확장 실패: {doc.metadata.get('service_id')}, {e}")
            extended_docs.append(doc)
    print("docs: ",extended_docs)
    # Prompt + LLM chain 구성
    prompt = ChatPromptTemplate.from_template("""
너는 대한민국 정부 및 지자체의 복지 정책을 안내하는 AI 어시스턴트야.

아래 정보는 복지 서비스에 대한 요약 정보와, XML 형식의 상세 설명을 포함하고 있어.
각 문서에는 "[출처: central]" 또는 "[출처: local]"로 출처가 명시되어 있으며, 이에 따라 XML 구조가 달라.
출처에 따라 다음과 같은 주요 태그들이 포함되어 있으니, 이를 참고하여 해석해줘:

---

✅ 중앙정부 XML (출처: central):
- servNm: 서비스명
- wlfareInfoOutlCn: 서비스 요약
- tgtrDtlCn: 지원 대상 설명
- slctCritCn: 선정 기준
- alwServCn: 급여/지원 내용
- applmetList, inqplCtadrList, inqplHmpgReldList, baslawList, basfrmList 등 추가 정보 포함

✅ 지자체 XML (출처: local):
- servNm: 서비스명
- servDgst: 요약 설명
- sprtTrgtCn: 지원 대상
- slctCritCn: 선정 기준
- alwServCn: 지원/급여 내용
- aplyMtdCn, bizChrDeptNm, 문의처, 링크, 서식 등 포함

---

답변 작성 시 다음을 지켜줘:

1. 질문에 나이/지역/소득 등의 조건이 없으면, 일반적인 예시 정책을 안내하거나 조건에 따라 달라질 수 있음을 설명해.
2. 서비스별로 지원 내용, 신청 방법, 문의처, 관련 링크까지 가능한 한 구체적으로 포함해.
3. 태그를 그대로 복사하지 말고 자연어로 알기 쉽게 정리해줘.
4. 질문과 무관한 문서는 제외하거나 관련 없음을 알려줘.

---

📌 아래는 참고할 답변 예시야:

질문: "제가 받을 수 있는 복지정책이 있을까요?"

답변:
현재 전라북도 전주시 거주자라면 다음과 같은 복지 서비스를 확인해볼 수 있어요.

1. **독거노인 목욕비 지원**
- **지원 내용**: 65세 이상 국민기초생활수급자 또는 차상위계층 독거노인에게 경로목욕권(6,000원권) 연 12매 지급
- **신청 방법**: 읍면동 주민센터 방문 신청
- **문의처**: 전주시 노인복지과 (063-281-2025)
- **관련 서식**: [2023년 경로목욕권 지원 계획.pdf](https://www.bokjiro.go.kr/ssis-tbu/CmmFileUtil/siteQnaInfoDownload.do?atcflId=...)

이 외에도 연령, 소득, 가족 구성에 따라 다른 정책이 적용될 수 있으니 주민센터나 복지로(www.bokjiro.go.kr)에서 확인해보세요.

---

이제 아래 문서를 참고해 질문에 맞는 복지 정보를 구체적으로 안내해줘:

-----------
{context}
-----------

질문: {question}
답변 (자연어로, 구체적으로, 태그 복사 없이):
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
