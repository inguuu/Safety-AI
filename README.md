
## 📌 1. 프로젝트 개요

### ✅ 문제 정의
- 기존 건강검진 AI 에이전트는 **형식적이고 키워드 기반**으로만 작동하며 **자연어 질의 해석 불가**
- 사용자 입장에서 검사항목, 센터 정보, 위험 요인 등 **실질적인 질의 응답이 어려움**
- 관련 자료는 **PDF, DB, 웹 등 다양한 포맷**에 흩어져 있어 검색 접근이 어려움

### 🎯 대상 사용자
- **건강검진 정보 제공자** (센터 담당자, 기업 보건관리자)
- **건강검진 대상자** (일반 직원, 수검자)

### 💡 솔루션 개요
- 자연어로 건강검진에 대한 질의를 입력하면, AI가 유사어 치환 및 전처리를 통해 관련 정보를 검색하고, 필요시 GPT로 직접 응답
- **RAG 기반 챗봇**으로 정확하고 근거 기반의 답변 제공

---



## 📊 2. 시스템 아키텍처


<img width="1653" height="701" alt="image" src="https://github.com/user-attachments/assets/d6886ff8-d3ad-45ba-a4c6-5c203242bae0" />


```plaintext
┌────────────┐
│ 사용자 질문 │
└─────┬──────┘
      ▼
┌──────────────────────────────┐
│ 🔁 전처리: 유사어 치환 GPT 호출 │
└─────┬────────────────────────┘
      ▼
┌──────────────────────────────┐
│ 🔎 Azure AI Search 호출      │
└─────┬────────────────────────┘
      │          └─(없으면)
      ▼                         ▼
┌────────────┐         ┌────────────────────┐
│ 문서 검색 결과 │         │  GPT 직접 응답 생성    │
└─────┬──────┘         └─────────┬──────────┘
      ▼                         ▼
┌────────────────────────────────────────┐
│ 💬 근거 기반 답변 생성 및 응답 반환     │
└────────────────────────────────────────┘
```

### ✅ 주요 구성 요소
- **Azure AI Search** (Indexer, Skillset, Index)  
- **Azure OpenAI (GPT-4.1-mini)**  
- **Streamlit UI (ChatGPT 스타일)**  
- **Blob Storage(Text, OCR)**
- **Azure Database for MySQL(Text, OCR)**

---

### 📂 프로젝트 구조 요약

```plaintext
📁 ai-health-agent/
├── app.py                  # app
├── config.py               # 환경 변수 또는 공통 설정 관리
├── preprocess.py           # 유저 입력 전처리
├── search_handler.py       # Azure Search 쿼리 핸들링
├── llm_handler.py          # OpenAI or Azure OpenAI LLM 호출 관리
├── ui_components.py        # UI, CSS 분리 
├── index_setup.py          # Azure Search Index 구성
├── datasource_indexer.py   # DataSource, Skillset, Indexer 자동화
├── run_indexer.py          # 인덱서 수동 실행
├── UploadDocs.cmd          # 문서 업로드 스크립트
├── .env                    # 환경변수 설정
└── README.md               # 💬 현재 문서
```

## 🧠 3. 핵심 기술 포인트

### ✅ 전처리 기반 유사어 치환 (Prompt Engineering)
- `"진료항목" → "검사항목"`, `"기관" → "센터"` 등의 치환을 **GPT를 활용한 자연스러운 문장 재구성** 방식으로 처리

### ✅ 커스텀 프롬포트 제공(Custom Prompt)

| 스타일명       | `temperature` | `top_p` | `max_tokens` | 특성 설명                    |
| ---------- | ------------- | ------- | ------------ | ------------------------ |
| **정확도 우선** | `0.2`         | `0.7`   | `600`        | 신뢰도 높은 단정적인 응답, 불확실성 최소화 |
| **빠르게**    | `0.2`         | `0.6`   | `350`        | 핵심만 빠르게 전달, 간결한 문장 위주    |
| **간략하게**   | `0.3`         | `0.7`   | `400`        | 요점 정리형 응답, 불필요한 배경 설명 제거 |
| **상세하게**   | `0.7`         | `0.9`   | `800`        | 친절하고 자세한 설명, 예시 및 배경 포함  |

### ✅ RAG 구조 구현
- Azure Search → 근거 문서 검색  
- GPT는 문서 기반으로만 응답 (`GROUNDED_PROMPT`)  
- 검색 실패 시 GPT가 **유연하게 직접 응답**

### ✅ Azure AI Search Skillset
- PDF 문서 내 이미지에서 텍스트 추출하는 **OCR Skill** 포함
- 자동 Indexer 생성 → Blob 내 신규 문서 자동 색인화

### ✅ 운영 자동화 스크립트 구성
- `UploadDocs.cmd` : 문서 업로드  
- `index_setup.py` : 인덱스 초기 세팅  
- `datasource_indexer.py` : DataSource, Skillset, Indexer 자동 생성 및 실행  
- `run_indexer.py` : 수동 실행용 스크립트

---





## 🖥️ 4. 라이브 데모

<img width="1419" height="935" alt="image" src="https://github.com/user-attachments/assets/3b05a274-e075-4a7e-bf7e-9d0b88e2c7f9" />



[👉 웹 서비스 시연 바로가기](https://igigwebapp-d2bcajc4fyfwagbp.koreacentral-01.azurewebsites.net)

[🎥 데모 영상 보기](https://drive.google.com/file/d/1_WNDX4MQNysxOT_uG1zzxDhMtWODmJwM/view?usp=drive_link)

---


## 🔭 5. 향후 개선 및 확장 계획

| 개선 항목                | 설명 |
|-------------------------|------|
| ✅ 유사어 DB 확장         | 산업군 및 의료기관별 다양한 사용자 언어 반영 |
| ✅ 시스템 간 DB 연동      | 검진신청 및 검진결과를 활용하여 개발 범위 확장 |
| ✅ 다운로드 기능 추가     | 검색 결과 기반 제안서, 리포트 다운로드 기능 제공 |
| ✅ 보안 및 인증 강화      | Apa GW, KeyVault, EntraId 연결 |

---


## ✅ 결론

- 기존 건강검진 챗봇은 자연어 해석이 불가능하고, 단순 키워드 매칭에 의존
- 본 프로젝트는 **자연어 기반 질의 해석 + 근거 문서 기반 응답**이 가능한 **AI Agent** 구조를 구현
- 실제 건강검진 PDF 문서, DB 기반 정보를 AI Search와 GPT가 연결하여 사용자에게 실질적인 정보를 제공

> ⚡ **KT 건강검진 AI 알림이는** 단순한 챗봇이 아닌,  
> 현업 검진자료를 기반으로 한 **정확하고 근거 있는 의료 정보 에이전트**입니다.

