from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

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


class KakaoLoginView(APIView):
    def post(self, request):
        kakao_access_token = request.data.get('access_token')
        age = request.data.get('age')
        region = request.data.get('region')
        subregion = request.data.get('subregion')

        if not kakao_access_token:
            return Response({'error': 'No access token provided'}, status=status.HTTP_400_BAD_REQUEST)

        # 카카오 사용자 정보 요청
        kakao_user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {kakao_access_token}"}
        kakao_response = requests.get(kakao_user_info_url, headers=headers)
        if kakao_response.status_code != 200:
            return Response({'error': 'Invalid Kakao token'}, status=status.HTTP_400_BAD_REQUEST)

        kakao_data = kakao_response.json()
        kakao_id = kakao_data.get('id')
        kakao_account = kakao_data.get('kakao_account', {})
        email = kakao_account.get('email', f'kakao_{kakao_id}@kakao.com')

        try:
            # 기존 유저라면 바로 JWT 발급
            user = User.objects.get(email=email)
            # 필요시 정보 업데이트
            updated = False
            if age is not None and user.age != age:
                user.age = age
                updated = True
            if region is not None and user.region != region:
                user.region = region
                updated = True
            if subregion is not None and user.subregion != subregion:
                user.subregion = subregion
                updated = True
            if updated:
                user.save()
        except User.DoesNotExist:
            # 신규 유저인데 추가 정보가 없으면 404 반환
            if age is None or region is None or subregion is None:
                return Response(
                    {'message': '추가 정보가 필요합니다. (age, region, subregion)'},
                    status=status.HTTP_404_NOT_FOUND
                )
            # 추가 정보가 있으면 유저 생성
            user = User.objects.create(
                email=email,
                age=age,
                region=region,
                subregion=subregion
            )

        # JWT 토큰 발급
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'age': user.age,
                'region': user.region,
                'subregion': user.subregion,
            }
        })