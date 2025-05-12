from rag.retriever import get_bokjiro_retriever
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
너는 사용자의 상황과 지역에 맞는 복지서비스를 안내해주는 전문가야.

아래는 사용자의 질문과 관련된 문서 내용이야:

질문: {question}

문서 요약:
{context}

이 문서를 참고해서 사용자가 어떤 복지서비스를 받을 수 있는지 설명해줘.
""")

llm = ChatOpenAI(model="gpt-4o")

def run_bokjiro_rag(question: str, age: int, region: str) -> str:
    retriever = get_bokjiro_retriever(age, region)

    chain = (
        RunnableParallel({
            "context": retriever,
            "question": RunnablePassthrough()
        }) | prompt | llm
    )

    response = chain.invoke(question)
    return response.content
