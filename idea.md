# 1. 프로젝트 개요

### 프로젝트명

> **혜택이 (Hetaeki)**
> 

---

### 한 줄 소개

> “나이, 지역, 상황에 따라 내가 받을 수 있는 복지 혜택을 AI가 자동으로 추천해주는 서비스”
> 

---

### 프로젝트 목적

> 사용자의 **나이 / 지역 / 질문** 정보를 바탕으로
> 

> 중앙정부 및 지자체의 복지 정책을 **자동 분석**하고
> 

> **GPT 기반 RAG 시스템**으로 관련 정보를 **정확하게 안내**
> 

> 사회적 약자, 청년, 고령층, 이민자 등에게 **정책 접근성을 높이는 것**이 핵심 목표
> 

---

### 핵심 기능 요약

| 기능 | 설명 |
| --- | --- |
| 복지 정책 자동 수집 | 정부24, 복지로 등에서 중앙/지자체 복지 API 호출하여 정책 정보 수집 및 DB/벡터 저장 |
| 질문 기반 Q&A | 자연어 질문 → GPT 기반 RAG → 정책 추천 및 상세 안내 |
| 상세 정보 실시간 호출 | 벡터 검색 후, 정책의 상세 API 정보를 **실시간으로 호출**하여 답변 생성에 반영 |
| 인기 주제 분석 | 연령대별 사용자 질문 기반으로 **Top 5 핫토픽 자동 생성** |
| 보상형 광고 연동 예정 | 질문 또는 핫토픽 조회 전 **광고 시청 유도**를 통해 수익화 |

---

### 주요 기술 스택

| 영역 | 기술 |
| --- | --- |
| 백엔드 | Python, Django, Django REST Framework |
| AI 처리 | LangChain (Runnable API), OpenAI GPT (gpt-4o), Chroma DB |
| 벡터 저장 | Chroma + OpenAI Embeddings (→ 추후 HuggingFace 전환 예정) |
| 데이터 저장 | PostgreSQL |
| 비동기 처리 | Celery + Redis |
| 외부 연동 | 공공데이터포털 중앙/지자체 복지 API, Kakao Login 예정 |
| 배포 인프라 | AWS EC2 (Docker 기반), GitHub + GitHub Actions 예정 |

---

### 타깃 사용자

> 10대~60대 일반 시민
> 

> 고령층, 청년, 저소득층, 1인 가구
> 

> 이민자, 정보 접근이 어려운 계층
> 

---

### MVP 완료 상태

> 중앙/지자체 복지 수집기 완료
> 

> RAG 기반 질문 응답 기능 완료
> 

> 연령별 HotTopic 생성 완료
> 

> 사용자 인증/프로필 기능 완료
> 

> 보상형 광고 설계 및 수익화 전략 수립
> 

---

# 2. 시스템 아키텍처

### 시스템 구성도

```
사용자 (앱)
  │
  ├─ 질문, 나이, 지역
  ▼
Query API (Django REST)
  │
  ├─ 사용자 정보 기반 context 구성
  ▼
RAG Pipeline (rag/qa.py)
  ├─ 질문 벡터화 → 관련 정책 검색 (Chroma)
  ├─ 정책 상세내용 실시간 API 호출
  ├─ LangChain Document 생성
  └─ GPT 기반 응답 생성 (ChatOpenAI)
  ▼
최종 답변 반환
```

---

### 전체 구성 요약

| 구성 요소 | 설명 |
| --- | --- |
| `query` 앱 | 사용자 질문 처리, 나이/지역 기반 context 생성, RAG 호출 |
| `rag` 앱 | 벡터 검색, 상세 API 호출, LangChain QA 실행 |
| `documents` 앱 | 중앙/지자체 복지 정책 저장 및 관리 |
| `accounts` 앱 | 사용자 인증, 나이/지역 프로필 저장 |
| `queries` 앱 | 사용자 질문 기록, 연령별 인기 주제 분석 (HotTopic) |
| `celery tasks` | 주기적 정책 수집 및 핫토픽 생성 비동기 처리 |

---

### 핵심 처리 흐름

### 질문 → 답변까지

1. 사용자가 질문 (예: “전주 사는 청년인데 받을 수 있는 지원금 있어요?”)
2. 사용자 정보 + 질문 → LangChain RAG 호출
3. 관련 정책 벡터 검색
4. 각 정책의 상세 내용을 실시간 API로 가져옴
5. GPT가 context + 질문을 바탕으로 최종 답변 생성
6. 응답을 사용자에게 전달

---

### 데이터 흐름

| 순서 | 설명 |
| --- | --- |
| 1. 수집기 | `collector_central.py` / `collector_local.py`를 통해 정책 수집 |
| 2. 저장소 | 수집한 정책은 `Document` 모델에 저장 + `Chroma`에 벡터화 |
| 3. 사용자 질문 | `QueryAnswerView`에서 질문 수신 및 사용자 context 구성 |
| 4. GPT 호출 | RAG pipeline → GPT로 context + 질문 전달 |
| 5. 결과 저장 | 질문과 응답을 `UserQuery`에 저장 |

---

### 운영 구조

| 구성 | 설명 |
| --- | --- |
| Web API 서버 | Django + Gunicorn |
| 백그라운드 처리 | Celery + Redis |
| DB | PostgreSQL |
| 벡터 검색 | ChromaDB (로컬) |
| AI 모델 | OpenAI GPT (`gpt-4o`) |
| 배포 | AWS EC2 + Docker |
| 정기작업 | Celery Beat (정책 수집, HotTopic 생성 등) |

---

### 인증/보안

- JWT 기반 인증
- 사용자 나이, 지역 등은 `accounts.User` 프로필에 저장
- 향후 카카오 로그인 + 인앱결제 연동 예정

---

# 3. 데이터 모델 설계

### 주요 모델 요약

| 앱 | 모델명 | 설명 |
| --- | --- | --- |
| `accounts` | `User` | 사용자 정보 (`age`, `region`, `subregion`, `email`, `auth`) |
| `documents` | `Document` | 수집한 중앙/지자체 복지 정책 (벡터 저장 대상) |
| `queries` | `UserQuery` | 사용자가 한 질문과 GPT의 응답 기록 |
| `queries` | `HotTopic` | 최근 1주일 질문 기준 연령별 인기 키워드 top 5 |
| `tasks` | (예정) | 향후 보상형 광고 unlock, 리포트 생성 관련 기능 확장 시 사용 예정 |

---

### `accounts.User`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `email` | CharField | 사용자 이메일 (username 대체) |
| `age` | IntegerField | 나이 |
| `region` | CharField | 시도명 |
| `subregion` | CharField | 시군구명 |
| `date_joined` | DateTimeField | 가입일 |

---

### `documents.Document`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `service_id` | CharField | 고유 정책 ID (예: `WLF00012345`) |
| `title` | CharField | 정책명 |
| `description` | TextField | 요약 설명 (벡터 저장용) |
| `source` | CharField | `"central"` 또는 `"local"` |
| `created_at` | DateTimeField | 수집일 |

> 💡 상세 내용(alwServCn 등)은 저장하지 않음. 질문 시 API로 실시간 조회.
> 

---

### `queries.UserQuery`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `user` | ForeignKey → User | 질문한 사용자 |
| `question` | TextField | 사용자가 입력한 질문 |
| `answer` | TextField | GPT가 생성한 응답 |
| `created_at` | DateTimeField | 질문 시각 |

---

### `queries.HotTopic`

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `age_group` | CharField | `"청소년"`, `"청년"`, `"장년"`, `"노년"` |
| `topics` | JSONField | `{ "1위": "...", "2위": "...", ..., "5위": "..." }` |
| `created_at` | DateTimeField | 생성 시각 (매일 1회 생성) |

---

### 향후 추가 가능 모델 (예정)

| 모델 | 용도 |
| --- | --- |
| `UserUnlock` | 보상형 광고 시 기능 해제 기록 |
| `Purchase` | 프리미엄 구독/인앱결제 연동 시 사용 |
| `Feedback` | 사용자 피드백 수집 |
| `ReportRequest` | 리포트 생성 요청 기록 (PDF 등) |

---

# 4. API 명세서

### [인증 및 사용자]

---

> POST `/api/accounts/signup/`
> 
- 회원가입
- 필드: `email`, `password`, `age`, `region`, `subregion`
- 응답: 사용자 정보 + 토큰

---

> POST `/api/accounts/login/`
> 
- 이메일 로그인
- 필드: `email`, `password`
- 응답: `access`, `refresh` 토큰

---

> POST `/api/accounts/token/refresh/`
> 
- 토큰 리프레시
- 필드: `refresh` 토큰
- 응답: `access` 토큰

---

> GET `/api/accounts/me/`
> 
- 현재 로그인된 사용자 정보 조회

---

> PUT `/api/accounts/me/`
> 
- 사용자 프로필 수정 (나이, 지역 등)

---

> DELETE `/api/accounts/me/`
> 
- 회원탈퇴(softdelete)

---

### [질문 응답(RAG)]

---

> POST `/api/queries/`
> 
- 사용자의 질문에 대한 GPT 기반 응답 반환
- 필드: `question`
- 응답: `question`, `answer`

---

> GET `/api/hottopics/?age_group=청년`
> 
- 사용자의 질문에 대한 GPT 기반 응답 반환
- 응답: `age_group`, `topics`, `created_at`

---

# 5. 주요 기능 설명

### 1. 사용자 질문 기반 맞춤 복지 추천 (RAG + GPT)

- 사용자가 자연어로 질문을 입력 (예: “청년인데 전주 살아요. 뭐 받을 수 있어요?”)
- 사용자 정보(나이, 지역)와 질문 내용을 기반으로 **LangChain RAG** 수행
    - 벡터 검색 → 관련 복지 `service_id` 리스트 확보
    - 각 서비스의 **상세 내용을 실시간 API로 호출**
    - GPT에 전달할 **임시 context 문서** 구성
- `ChatOpenAI` (gpt-4o)를 통해 최종 응답 생성
- 응답 예시는 마크다운 스타일로 구성됨 (제목, 내용, 신청 방법, 링크 등 포함)

---

### 2. 중앙/지자체 복지 정책 자동 수집기

- 공공데이터포털 API 연동
    - 중앙정부: `/NationalWelfareInformationsV001/NationalWelfarelistV001`
    - 지자체: `/LocalGovernmentWelfareInformations/LcgvWelfarelist`
- 정책명, 요약설명, 지역정보 등 요약 데이터를 `Document`로 저장
- 저장된 description은 벡터로 변환해 Chroma에 저장
- 상세 설명(`alwServCn` 등)은 저장하지 않음 → 질문 시 실시간 호출

> ❗ DB 업데이트 시 create_or_update 로직 사용
> 

---

### 3. RAG 기반 벡터 검색 + API 실시간 호출

- 사용자의 질문을 임베딩 → 벡터 검색으로 관련 문서 검색
- 문서마다 `service_id`, `source` 기반으로 상세 API 호출
- XML을 그대로 문자열로 GPT에 넘겨 context 구성

> 예: [출처: local]\n[요약]\n...\n[상세설명]\n<xml>...</xml>
> 

---

### 4. 연령대별 인기 질문 주제 분석 (HotTopic)

- Celery 비동기 태스크로 매일 새벽 3시에 실행
- 최근 7일간 질문을 연령대별로 그룹핑
- 각 연령 그룹당 **GPT에게 인기 주제 5개 추출 요청**
- `HotTopic` 모델에 저장
- `/api/hottopics/?age_group=청년` 형식으로 제공

---

### 5. 보상형 광고를 통한 기능 잠금 해제 (수익화 설계)

- 기본적으로 모든 질문/HotTopic은 잠금 처리 가능
- 광고 시청 완료 후 → 백엔드에 unlock 기록 저장
- 기록 기반으로 질문 가능 여부 결정 or 리포트 열람 허용
- 광고 플랫폼: **Google AdMob (보상형 광고)** 기반 적용 예정

---

### 6. 상세 정책 리포트 생성 (예정 기능)

- 질문 결과를 요약해서 **PDF or 요약 리포트로 제공**
- 정책명 / 대상 / 신청 방법 / 링크 정리
- GPT 기반 요약 → HTML → PDF 변환
- 리포트 다운로드 전 광고 or 프리미엄 기능 연동 가능

---

# 6. 외부 연동 정보

### 1. 공공 데이터 포털 API

### 중앙정부 복지 서비스

- **API 명**: NationalWelfareInformationsV001
- **리스트 API**: `/NationalWelfarelistV001`
- **상세 API**: `/NationalWelfaredetailedV001`
- **설명**:
    - 전국 단위 중앙부처 복지 정책 수집
    - `callTp=L`, `srchKeyCode=001` 사용
- **상세 응답 구조**: XML (`wantedDtl` 루트)

### 지자체 복지 서비스

- **API 명**: LocalGovernmentWelfareInformations
- **리스트 API**: `/LcgvWelfarelist`
- **상세 API**: `/LcgvWelfaredetailed`
- **설명**:
    - 시도, 시군구 단위 정책 수집
    - 지역명을 포함한 정책 요약 수집
- **상세 응답 구조**: XML (단일 루트)

### 공통사항

- 인증 방식: API Key (`serviceKey=...`)
- API Key는 `.env` 파일에 `BOKJIRO_API_KEY`로 저장
- 상세 내용은 질문 시 실시간 호출로만 사용
- 요청 시 `_type=xml` 고정 사용

---

### 2. 인증 시스템 (JWT)

- 로그인/회원가입 완료 시, `access`, `refresh` 토큰 발급
- 인증 헤더:

```
Authorization: Bearer <access_token>
```

- JWT Payload에는 `user_id`, `email` 포함
- 사용자 정보(`age`, `region`, `subregion`)는 프로필에서 분리 관리
- 향후 **카카오 로그인** 연동 예정

---

### 3. OpenAI GPT API (응답 생성용)

- 사용 모델: `gpt-4o` (`gpt-3.5-turbo`도 옵션으로 사용 가능)
- 연동 라이브러리: `langchain_openai.ChatOpenAI`
- 사용 기능:
    - 질문 + 문서 context → 자연어 답변 생성
    - HotTopic 주제 생성
- 인증: `.env`에 `OPENAI_API_KEY` 저장

---

### 4. Vector DB: Chroma

- 저장 대상: 정책 description (요약만)
- 임베딩: `OpenAIEmbeddings` 사용 중 → 추후 HuggingFace로 전환 예정
- 디렉토리: `rag/chroma_documents/`
- 검색 시 `service_id`를 메타데이터로 함께 저장

---

### 5. Celery + Redis 연동 (비동기 작업)

- 주요 태스크:
    - 매일 정책 수집 (`collector_central.py`, `collector_local.py`)
    - HotTopic 생성 (`daily_generate_hot_topics`)
- 실행 시간:
    - 04:00 중앙정책
    - 04:30 지역정책
    - 03:00 핫토픽 생성
- 결과는 PostgreSQL DB에 저장됨

---

### 6. 향후 연동 예정

| 항목 | 설명 |
| --- | --- |
| Kakao Login | 앱용 카카오 SDK → JWT 발급 |
| Google/Apple In-App Purchase | 프리미엄 기능 결제 검증 (구매 인증 API 필요) |
| Firebase | 푸시 알림, Crashlytics 등 추후 도입 가능 |

---

# 7. 배포 및 운영 정보

### 서버 인프라 개요

| 항목 | 설정 |
| --- | --- |
| 운영 환경 | AWS EC2 (Ubuntu 20.04) |
| 배포 방식 | Docker Compose |
| 도메인 | `https://api.hetaeki.kr` |
| 인증서 | Let's Encrypt (Certbot 자동 갱신) |
| 웹서버 | Nginx (SSL reverse proxy) |
| 애플리케이션 서버 | Gunicorn |
| DB | PostgreSQL (도커 컨테이너 내부) |
| 메시지 브로커 | Redis (Celery 용) |

---

### 주요 컨테이너 구성 (Docker Compose)

```yaml
services:
  web:
    build: .
    command: gunicorn hetaeki_backend.wsgi:application
    ports: ["8000:8000"]
    depends_on: [db, redis]

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: hetaeki
      POSTGRES_USER: ...

  redis:
    image: redis:7

  celery:
    command: celery -A hetaeki_backend worker -l info

  beat:
    command: celery -A hetaeki_backend beat -l info
```

---

### 인증서 발급

- 도메인: `api.hetaeki.kr`
- 인증 방식: **Let's Encrypt + Certbot**
- 자동 갱신: `certbot.timer` 또는 `crontab` 등록

---

### 배포 프로세스

1. GitHub에 최신 코드 푸시
2. EC2 접속 → `git pull`
3. Docker 재시작:

```bash
docker-compose down
docker-compose up -d --build
```

1. 마이그레이션:

```bash
docker-compose exec web python manage.py migrate
```

---

### 운영 모니터링

| 항목 | 설명 |
| --- | --- |
| 에러 로그 | `gunicorn.log`, `celery.log` 로 수집 |
| DB 백업 | 수동 or cron 기반 `pg_dump` 활용 예정 |
| 요청 기록 | Django 로깅 or Nginx access log 활용 가능 |
| 모니터링 도입 예정 | Sentry, Grafana, Prometheus 등 확장 가능 |

---

### 정기 태스크 (Celery Beat)

| 태스크 | 시간 | 설명 |
| --- | --- | --- |
| 중앙 정책 수집 | 매일 04:00 | `collector_central.py` |
| 지자체 정책 수집 | 매일 04:30 | `collector_local.py` |
| 연령별 핫토픽 생성 | 매일 03:00 | `daily_generate_hot_topics()` |

---

### 운영 시 유의사항

- GPT 호출은 요금이 발생하므로, 질문 수/빈도에 제한 필요
- 정책 API는 공공데이터포털이므로 가끔 장애 발생 가능 → fallback 대비
- 벡터스토어는 Chroma 로컬 기반 → 장기적으로 DB 백업/복제 고려

---

# 8. 향후 기능 계획 (To-do)

### 1. 프론트엔드 개발 (React Native 기반 앱)

- Figma 디자인 완료 후, 앱 개발 시작
- React Native + Expo로 크로스플랫폼 개발
- Kakao 로그인, 광고 SDK, 푸시 알림 포함 예정
- 앱 배포 대상: **Google Play (우선)** → 이후 Apple App Store

---

### 2. 소셜 로그인 연동 (Kakao)

- 카카오 SDK 연동 (React Native 앱)
- 앱에서 로그인 후 → 백엔드로 `access_token` 전달
- 백엔드는 토큰 검증 후 사용자 정보 등록 및 JWT 발급

---

### 3. 보상형 광고 기능

- Google AdMob 보상형 광고 연동
- 기능 잠금 해제 시 `UserUnlock` 기록 저장
- 잠금 대상:
    - 질문 응답
    - HotTopic 조회
    - 리포트 다운로드

---

### 4. 리포트 생성 기능

- 질문 응답 결과 기반으로 정책 정리 리포트 자동 생성
- 포맷: PDF 또는 HTML 요약
- 항목: 정책명, 요약, 지원 대상, 신청 방법, 관련 링크
- GPT 기반 요약 → 템플릿 적용 → 다운로드 제공
- 수익화 연계 (보상형 광고 or 프리미엄 전용)

---

### 5. HuggingFace Embedding 모델 전환 (벡터 개선)

- 기존 OpenAI 임베딩은 한국어 정책 표현에 약함
- 추후 `bge-m3`, `KoSimCSE` 등 한국어 특화 모델로 교체
- Chroma 벡터스토어 전체 재생성 예정

---

### 6. 사용자 피드백 기능

- 답변 평가: 👍/👎 또는 별점
- 피드백 수집용 모델: `Feedback`
- GPT 개선 학습 or 서비스 개선에 활용

---

### 7. 지자체 제휴용 B2B 확장

- 특정 시/군/구 대상 커스터마이징 버전 개발
- "전주시 전용 복지 AI", "성남시 민원 챗봇" 등 납품 가능
- 브랜딩 + 정책 필터 우선 적용

---

### 8. 프리미엄 구독 기능

- 앱 내 인앱결제 연동 (Google/Apple)
- 프리미엄 유저만:
    - 광고 없이 질문 가능
    - 리포트 무제한 생성
    - 상담 우선 응답 제공 등