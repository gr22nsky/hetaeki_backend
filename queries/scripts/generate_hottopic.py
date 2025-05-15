import json
from datetime import timedelta
from django.utils import timezone

from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from queries.models import UserQuery
from queries.models import HotTopic

AGE_GROUPS = {
    "청소년": range(0, 20),
    "청년": range(20, 40),
    "장년": range(40, 60),
    "노년": range(60, 200),
}

parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 데이터 분석가야. 지난 7일간 사용자의 질문 내용을 참고해서 이 연령대 사람들이 가장 관심 있는 주제를 5가지로 요약해줘. 주제는 짧고 핵심적으로, 중복 없이 작성하고 반드시 JSON 배열로만 출력해."),
    ("human", "질문들:\n{questions}\n\nJSON으로 top 5 관심 주제를 알려줘."),
])

llm = ChatOpenAI(temperature=0.3)
chain = prompt | llm | parser


def generate_top5_topics():
    one_week_ago = timezone.now() - timedelta(days=7)
    results = []

    for label, age_range in AGE_GROUPS.items():
        queries = UserQuery.objects.filter(
            user__age__gte=min(age_range),
            user__age__lt=max(age_range),
            created_at__gte=one_week_ago,
        ).order_by("-created_at")

        if not queries.exists():
            continue

        questions = "\n".join(q.question for q in queries[:100])

        try:
            topics = chain.invoke({"questions": questions})
            if isinstance(topics, list) and len(topics) >= 1:
                HotTopic.objects.create(
                    age_group=label,
                    topics=topics[:5]
                )
                results.append((label, topics[:5]))
        except Exception as e:
            print(f"❌ [{label}] GPT 호출 실패:", e)
    print('✅ 저장 완료')