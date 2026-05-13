## 🛡️ V&V 통합 관리 시스템 v3.1 (README.md)

📌 Project Overview
본 프로젝트는 MATLAB/Simulink 기반 제어로직의 검증(Verification) 및 확인(Validation) 프로세스를 효율적으로 관리하기 위한 Streamlit 기반 통합 대시보드입니다. 
엔지니어별 검증 진척도, 요구사항 대응 현황 파악 및 RAG(Retrieval-Augmented Generation) 개념을 응용한 지식 기반 챗봇을 통해 실무에서 발생하는 기술적 문제에 대한 즉각적인 솔루션을 제공합니다.

🚀 Key Features
1. 📊 통합 대시보드 (Integrated Dashboard)
KPI 시각화: 총 할당 요구사항 대비 검증 완료율을 실시간 메트릭으로 표시.
현황 그래프: Plotly를 활용하여 담당자별 검증 수행 현황 및 일자별 사양서 수정 추이를 시각화.
데이터 투명성: 전체 검증 히스토리를 데이터프레임 형태로 상시 확인 가능.

2. 📥 데이터 관리 시스템 (Data Management)
검증 결과 입력: 모델 버전, 서브시스템별 요구사항 달성 개수 등 세부 검증 데이터 저장.
사양서 작업 기록: 신규 생성, 수정, 삭제된 요구사양 개수를 트래킹하여 사양서의 성숙도 관리.
Session State 유지: 입력된 데이터는 세션 내에서 즉각적으로 대시보드에 반영.

3. 💬 지식 기반 스마트 챗봇 (V&V Expert Chatbot)
RAG 스타일 엔진: 키워드 매칭 및 유사도 분석 알고리즘을 통해 실무 지식 베이스(Knowledge Base) 검색.
전문 도메인 지식:
MATLAB 경로 및 라이선스 오류 해결.
MCDC 커버리지 향상 전략 및 리포트 분석 가이드.
Simulink 주요 블록(Edge Detect, LPF, Rate Limiter) 검증 방법론 제공.
C-Compiler(MEX) 빌드 오류 및 환경 설정 가이드.

🛠 Tech Stack
Frontend/Backend: Streamlit
Data Analysis: Pandas
Visualization: Plotly
Knowledge Base: Custom RAG Logic



# 1. 필수 패키지 설치
pip install streamlit pandas plotly

# 2. 애플리케이션 실행
/antigravity/scratch 경로 이동 후
python -m streamlit run advanced_app.py

* server.py 파일은 데모 버전입니다
