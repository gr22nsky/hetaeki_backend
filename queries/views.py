# query/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from queries.models import UserQuery, HotTopic
from accounts.models import User
from rag.qa import run_qa

class QueryAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get("question", "").strip()
        if not question:
            return Response({"error": "질문을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 사용자 정보 가져오기
        try:
            profile = request.user
            age = profile.age
            region = profile.region
            subregion = profile.subregion
        except Exception:
            return Response({"error": "사용자 프로필 정보가 누락되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 질문에 사용자 정보를 추가
        system_context = f"[사용자정보] 나이: {age}, 지역: {region} {subregion}. "
        full_query = f"{system_context}\n[질문]: {question}"

        try:
            answer = run_qa(full_query)
        except Exception as e:
            return Response({"error": f"답변 생성 중 오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        UserQuery.objects.create(user=request.user, question=question, answer=answer)
        return Response({"question": question, "answer": answer})


class HotTopicView(APIView):
    def get(self, request):
        age_group = request.query_params.get("age_group")

        if not age_group:
            return Response({"error": "age_group 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        topic = HotTopic.objects.filter(age_group=age_group).order_by("-created_at").first()

        if not topic:
            return Response({"message": f"{age_group}에 대한 주제를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "age_group": topic.age_group,
            "topics": topic.topics,
            "created_at": topic.created_at
        })