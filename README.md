# 혜택이(Hetaeki) 백엔드

> "나이, 지역, 상황에 따라 내가 받을 수 있는 복지 혜택을 AI가 자동으로 추천해주는 서비스"

---

## 📝 프로젝트 개요

- **중앙정부/지자체 복지 정책**을 자동 수집·분석하여, 사용자의 나이/지역/질문에 맞는 복지 혜택을 AI가 안내합니다.
- **GPT-4o 기반 RAG 파이프라인**으로 자연어 질문에 대해 맞춤형 정책 정보를 제공합니다.
- 사회적 약자, 청년, 고령층, 이민자 등 정보 접근이 어려운 계층의 정책 접근성을 높이는 것이 목표입니다.

---

## 🚀 주요 기능

- **복지 정책 자동 수집**: 정부24, 복지로 등 공공 API에서 중앙/지자체 복지 정책을 주기적으로 수집
- **문서 임베딩/벡터스토어**: Hugging Face SBERT(ko-sroberta-multitask)로 임베딩, Chroma DB에 벡터 저장
- **질문 기반 Q&A**: 자연어 질문 → RAG → GPT-4o로 정책 추천 및 상세 안내
- **정책 상세 실시간 호출**: 벡터 검색 후, 정책 상세 API를 실시간 호출해 최신 정보 반영
- **연령별 인기 주제 분석**: 최근 1주일 질문을 바탕으로 연령대별 Top 5 핫토픽 자동 생성
- **JWT 인증/프로필**: 사용자 나이, 지역 등 프로필 기반 맞춤 추천
- **비동기 작업**: Celery로 정책 수집/핫토픽 생성 등 주기적 자동화

---

## 📁 폴더 구조 및 역할

```
hetaeki_backend/
├── accounts/         # 사용자 인증/프로필 (User 모델, JWT, 회원가입 등)
├── documents/        # 복지 정책 수집/저장 (Document 모델, 수집기, 임베딩)
│   └── scripts/      # 정책 수집/임베딩 자동화 스크립트 (collector.py 등)
├── queries/          # 질문/답변, 쿼리 기록, 핫토픽 (UserQuery, HotTopic)
│   └── scripts/      # 핫토픽 생성 등 배치 스크립트
├── rag/              # RAG 파이프라인, 벡터 검색, QA, 임베딩 유틸
│   └── chroma_documents/ # Chroma 벡터스토어 데이터 (자동 생성)
├── hetaeki_backend/  # Django 설정, URL, WSGI, Celery 등
├── requirements.txt  # Python 의존성 목록
├── manage.py         # Django 관리 명령어
└── ...
```

---

## ⚙️ 설치 및 실행 방법

1. **레포 클론 & 진입**
   ```bash
   git clone https://github.com/your-org/hetaeki_backend.git
   cd hetaeki_backend
   ```
2. **가상환경 생성 & 패키지 설치**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **환경 변수(.env) 설정**
   - `.env` 파일 예시:
     ```env
     OPENAI_API_KEY=sk-...
     SECRET_KEY=your-django-secret
     DEBUG=True
     ALLOWED_HOSTS=localhost,127.0.0.1
     BOKJIRO_API_KEY=...
     ACCESS_TOKEN_LIFETIME_MINUTES=30
     REFRESH_TOKEN_LIFETIME_DAYS=7
     ```
4. **DB 마이그레이션**
   ```bash
   python manage.py migrate
   ```
5. **정책 데이터 수집 및 벡터스토어 생성**
   ```bash
   python documents/scripts/collector.py
   ```
   - 최초 실행 시 Hugging Face 모델이 자동 다운로드됨 (인터넷 필요)
   - 기존 `rag/chroma_documents` 폴더는 삭제 후 재생성 필요
6. **서버 실행**
   ```bash
   python manage.py runserver
   ```
7. **(선택) Celery 워커/비트 실행**
   ```bash
   celery -A hetaeki_backend worker --loglevel=info
   celery -A hetaeki_backend beat --loglevel=info
   ```

---

## 🔍 주요 기능 상세

### 1. 문서 수집 및 임베딩
- `documents/scripts/collector.py`에서 중앙/지자체 복지 정책을 API로 수집
- 수집한 정책을 DB(`Document` 모델)와 Chroma 벡터스토어에 저장
- 임베딩: Hugging Face SBERT(`jhgan/ko-sroberta-multitask`) 사용

### 2. RAG 기반 질문 응답
- `rag/qa.py`에서 LangChain 기반 RAG 파이프라인 구현
- 사용자 질문 → 벡터 검색 → 정책 상세 API 호출 → GPT-4o로 답변 생성
- context 확장, 자연어 요약, 태그 제거 등 맞춤형 프롬프트 적용

### 3. 연령별 핫토픽 자동 생성
- `queries/scripts/generate_hottopic.py`에서 최근 1주일 질문을 분석
- 연령대별 Top 5 관심 주제를 자동 추출 및 저장

### 4. 사용자 인증/프로필
- `accounts` 앱에서 JWT 기반 인증, 나이/지역 등 프로필 관리

### 5. 비동기/스케줄러
- Celery + Redis로 정책 수집, 핫토픽 생성 등 주기적 자동화

---

## 🗂️ 주요 모델 요약

| 앱         | 모델명      | 설명                                  |
|------------|-------------|---------------------------------------|
| accounts   | User        | 사용자 정보 (age, region, email 등)   |
| documents  | Document    | 복지 정책 정보 (중앙/지자체)         |
| queries    | UserQuery   | 질문/답변 기록                        |
| queries    | HotTopic    | 연령별 인기 주제                      |

---

## 🌐 API/엔드포인트 예시

- `/api/auth/` : 회원가입/로그인/프로필
- `/api/documents/` : 정책 목록/상세
- `/api/queries/` : 질문/답변 기록
- `/api/hottopic/` : 연령별 인기 주제

(상세 엔드포인트는 각 앱의 `urls.py` 참고)

---

## 📝 환경 변수 정리

| 변수명                      | 설명                        |
|-----------------------------|-----------------------------|
| OPENAI_API_KEY              | OpenAI GPT API 키           |
| SECRET_KEY                  | Django 시크릿 키            |
| DEBUG                       | 디버그 모드(True/False)     |
| ALLOWED_HOSTS               | 허용 호스트(쉼표 구분)      |
| BOKJIRO_API_KEY             | 복지로 API 키               |
| ACCESS_TOKEN_LIFETIME_MINUTES| JWT 액세스 토큰 만료(분)    |
| REFRESH_TOKEN_LIFETIME_DAYS | JWT 리프레시 토큰 만료(일)  |

---

## 💡 참고/운영 팁

- 최초 임베딩/벡터스토어 생성 시 모델 다운로드로 시간이 다소 소요될 수 있습니다.
- Chroma 0.4.x 이상에서는 `vectorstore.persist()` 호출 없이 자동 저장됩니다.
- 네트워크 이슈로 일부 문서 임베딩이 누락될 경우, 스크립트를 한 번 더 실행하면 됩니다.
- 운영 DB는 PostgreSQL을 권장하며, 개발/테스트는 SQLite로도 충분합니다.
- Celery/Beat는 운영 환경에서만 실행해도 무방합니다.

---

## 📚 참고 자료

- [LangChain 공식 문서](https://python.langchain.com/)
- [Chroma DB 공식 문서](https://docs.trychroma.com/)
- [Hugging Face SBERT](https://huggingface.co/jhgan/ko-sroberta-multitask)
- [OpenAI GPT-4o](https://platform.openai.com/docs/models/gpt-4o)

---

## 🏷️ 라이선스

- 본 프로젝트는 MIT 라이선스를 따릅니다.

---

## 🛠️ 기술 스택

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/>
  <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white" alt="Celery"/>
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/Chroma-4B0082?style=for-the-badge" alt="ChromaDB"/>
  <img src="https://img.shields.io/badge/LangChain-000000?style=for-the-badge" alt="LangChain"/>
  <img src="https://img.shields.io/badge/HuggingFace-FFD21F?style=for-the-badge&logo=huggingface&logoColor=black" alt="HuggingFace"/>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
</p>