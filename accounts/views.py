from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated

class SignupView(APIView):
    """회원가입 처리 뷰."""
    def post(self, request):
        # 회원가입 요청 처리
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 성공!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyProfileView(APIView):
    """내 프로필 조회/수정/탈퇴 뷰."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 내 프로필 정보 반환
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        # 내 프로필 정보 수정
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        # 회원 탈퇴(soft delete)
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "회원 탈퇴 처리되었습니다."}, status=status.HTTP_204_NO_CONTENT)