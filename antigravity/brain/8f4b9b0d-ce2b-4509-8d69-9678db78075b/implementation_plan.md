# Implementation Plan: Simulink Verification Dashboard & AI Chatbot

## Overview
The goal is to develop an integrated Streamlit web application that serves as a Simulink dynamic verification dashboard, a data entry tool, and a smart troubleshooting chatbot. 

## UI/UX Architecture
Instead of using a traditional sidebar for navigation, the app will utilize a **Top Menu with Card-style Buttons** (using `st.columns` and `st.button`) to mimic a wide, clean web layout. Navigating between modes will be controlled via `st.session_state.current_page`.

The three main pages will be:
1. **검증 대시보드 (Dashboard)**
2. **데이터 입력 (Data Input)**
3. **💬 AI 챗봇 (Chatbot)**

## State Management
We will use `st.session_state` to store a Pandas DataFrame containing the mock verification progress data. This allows updates from the "데이터 입력" tab to instantaneously reflect in the "검증 대시보드" tab.

### Data Schema
- `Name`: 담당자 이름
- `Subsystem`: 서브시스템명
- `Difficulty`: 난이도 (상/중/하)
- `Total_Reqs`: 할당된 요구 사양서 개수
- `Daily_Target`: 하루 목표 처리량
- `Cumulative`: 누적 처리량
- `Progress_Pct`: 진행률 (%)

## Proposed Changes

### `/Users/leehyeyoon/.gemini/antigravity/scratch/simulink_assistant/server.py`
#### [MODIFY] `server.py`
- **Session State Initialization**: Pre-populate a DataFrame into `st.session_state.df` if it doesn't exist.
- **Menu Router**: Render three horizontal buttons. Update `st.session_state.current_page` upon click.
- **Page: Data Input**: 
  - Form taking inputs for 'Today's Processed Count' (오늘 처리량) for a specific user/subsystem.
  - Logic to update `Cumulative` (+ Today's count) and re-calculate `Progress_Pct` (`Cumulative / Total_Reqs * 100`).
- **Page: Dashboard**:
  - Top Metrics using `st.metric`.
  - Data Table using `st.dataframe`.
  - Plotly Bar Chart showing `Progress_Pct` by `Name`.
- **Page: Chatbot**:
  - Expanded Keyword Matching Logic.
  - New Topics: Simulink blocks (Edge Detect, LPF, Rate Limiter), Requirements to TC strategies, Coverage enhancement strategies, Error troubleshooting (MATLAB/Simulink/Compiler/License).
  - Enforce "Root Cause -> Step-by-Step Solution" formatting.

## Verification Plan
### Automated Tests
*None for this prototype.*

### Manual Verification
1. Run `python -m streamlit run server.py`.
2. Ensure top navigation buttons work and swap views seamlessly.
3. In "데이터 입력", add 5 to the processed count for a specific user.
4. Go to "검증 대시보드" and verify the Progress (%) and Cumulative chart correctly reflect the new input.
5. In "💬 AI 챗봇", ask about "Edge Detect 블록 설명해줘" or "컴파일러 오류 해결방법" to verify the structured NLP responses.
