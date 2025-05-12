from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import UserQuery
from .serializers import UserQuerySerializer
from rag.rag_chain import run_bokjiro_rag

class UserQueryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queries = request.user.queries.order_by("-created_at")
        serializer = UserQuerySerializer(queries, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        question = request.data.get("question")
        if not question:
            return Response({"error": "질문을 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.age or not user.region:
            return Response({"error": "프로필에 나이와 지역 정보를 먼저 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = run_bokjiro_rag(
                question=question,
                age=user.age,
                region=user.region
            )

            UserQuery.objects.create(
                user=user,
                question=question,
                answer=answer
            )

            return Response({
                "question": question,
                "answer": answer
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"RAG 응답 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
