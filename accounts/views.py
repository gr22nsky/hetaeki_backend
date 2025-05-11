from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 성공!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "회원 탈퇴 처리되었습니다."}, status=status.HTTP_204_NO_CONTENT)