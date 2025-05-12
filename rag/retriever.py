from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

CHROMA_PATH = "chroma_bokjiro"

def get_age_group(age: int) -> str:
    if age < 20:
        return "10대"
    elif age < 30:
        return "20대"
    elif age < 40:
        return "30대"
    elif age < 50:
        return "40대"
    elif age < 60:
        return "50대"
    else:
        return "60대 이상"

def get_bokjiro_retriever(age: int, region: str):
    age_group = get_age_group(age)
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=OpenAIEmbeddings()
    ).as_retriever(search_kwargs={
        "k": 5,
        "filter": {
            "지역": region,
            "지원대상": age_group
        }
    })
