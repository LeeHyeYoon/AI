import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="Simulink 실무 검증 대시보드", page_icon="⚙️", layout="wide")

# ==========================================
# 1. State Management (초기 데이터 설정)
# ==========================================
def init_data():
    if 'req_df' not in st.session_state:
        st.session_state.req_df = pd.DataFrame({
            '담당자명': ['이혜윤', '김철수', '박영희', '최동훈', '정민수'],
            '서브시스템명': ['Brake_Control', 'Speed_Limit', 'Sensor_Filter', 'Battery_Mng', 'Fail_Safe'],
            '난이도': ['상', '중', '하', '상', '상'],
            '할당된 사양서(Total)': [120, 80, 50, 150, 90],
            '하루 목표(Target)': [10, 8, 15, 12, 10],
            '누적 처리량(Cumul)': [40, 30, 45, 60, 20],
        })
        st.session_state.req_df['진행률(%)'] = (st.session_state.req_df['누적 처리량(Cumul)'] / st.session_state.req_df['할당된 사양서(Total)'] * 100).round(1)
        
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "검증 대시보드"
        
    if 'chat_msgs' not in st.session_state:
        st.session_state.chat_msgs = []

init_data()

# ==========================================
# 2. 지식 베이스 정의 (RAG Data Source)
# ==========================================
KNOWLEDGE_BASE = [
    {
        "keywords": ["matlab", "경로", "setpath", "환경변수", "폴더"],
        "question": "MATLAB 경로 설정 문제",
        "answer": {
            "root_cause": "MATLAB 실행 시 검증에 필요한 외부 툴박스 폴더나 하위 라이브러리를 찾지 못해 모델 빌드가 실패하는 경우가 많습니다.",
            "solution": "1. MATLAB 상단 **Home** 탭 > **Environment** 영역의 **Set Path**를 클릭합니다.<br>2. **Add with Subfolders...**를 클릭하고 작업 중인 최상위 폴더를 선택합니다.<br>3. 목록에 경로가 추가되면 **Save** 후 **Close** 합니다.",
            "tip": "프로젝트마다 독립적인 경로 관리를 위해 `startup.m` 스크립트를 활용하면 충돌을 방지할 수 있습니다."
        }
    },
    {
        "keywords": ["matlab", "라이선스", "라이센스", "만료", "연장"],
        "question": "MATLAB 라이선스 확인 및 갱신",
        "answer": {
            "root_cause": "현재 MATLAB 기본 라이선스는 유효하나, 갱신이 필요해 Warning이 발생했을 가능성이 높습니다.",
            "solution": "1. 커맨드 창에 `license('inuse')` 명령어를 입력해 할당 상태를 확인하세요.<br>2. 만료 기한 점검: 상단 **Help** 메뉴 > **Licensing** > **Update Current Licenses...**를 누르시면 만료일을 볼 수 있습니다.",
            "tip": "동글(Network) 라이선스의 경우 사내 VPN 연결 상태를 먼저 점검하는 것이 좋습니다."
        }
    },
    {
        "keywords": ["mv", "라이선스", "라이센스", "설정", "초기"],
        "question": "Model Verification (MV) 초기 세팅",
        "answer": {
            "root_cause": "Simulink Design Verifier 라이선스 누락 또는 올바른 C 컴파일러가 매핑되지 않으면 MV 실행이 불가합니다.",
            "solution": "1. `ver('sldv')` 입력 후 모듈이 설치되어 있는지 확인합니다.<br>2. `mex -setup C++`를 입력하여 Visual Studio / MinGW 컴파일러를 연동시킵니다.<br>3. 모델 설정(Ctrl+E) > **Design Verifier** 탭 오픈 시 에러 팝업이 뜨지 않아야 정상입니다.",
            "tip": "폴더명에 한글이 존재하면 C 컴파일러가 모델 빌드를 거부하므로 영문 경로를 생활화합시다."
        }
    },
    {
        "keywords": ["coverage", "라이선스", "라이센스", "초기", "설정"],
        "question": "Coverage 환경 세팅 문제",
        "answer": {
            "root_cause": "Coverage 측정 실패의 가장 흔한 원인은 Coverage 툴박스 부재 및 모델 설정에서의 Error/Warning 옵션 누락입니다.",
            "solution": "1. `ver('slcoverage')` 명령어로 패키지를 체크하세요.<br>2. 모델 설정(Ctrl+E) > **Coverage** 탭에서 **Record coverage for this model** 항목을 반드시 선택합니다.<br>3. 컴파일러 점검을 위해 `mex -setup C++`를 다시 한번 통과시킵니다.",
            "tip": "MCDC 같은 엄격한 검증을 요구받을 때는 Structural Coverage Levels를 반드시 설정해두어야 합니다."
        }
    },
    {
        "keywords": ["edgedetect", "에지디텍트", "개념", "설명"],
        "question": "Edge Detect 블록 파악 및 검증",
        "answer": {
            "root_cause": "Edge Detect 블록은 입력파의 상승/하강 조건 시에만 1-Step 펄스를 방출하므로 단일 상수 입력으로는 검증이 불가능합니다.",
            "solution": "1. 블록 파라미터가 'Rising'인지 'Falling'인지 우선 확인하세요.<br>2. Rising Edge 검증의 경우, Signal Builder에서 신호가 0에서 1로 명확히 변환되는 계단 함수(Step)를 포함하도록 디자인합니다.",
            "tip": "연속 시간(Continuous-time) 모델에서는 에지가 모호하므로 Sample Time = 0.01s 등의 이산 시간(Discrete) 모드로 디버깅하세요."
        }
    },
    {
        "keywords": ["lowpassfilter", "lpf", "개념", "설명", "필터"],
        "question": "Low Pass Filter (LPF) 로직 검증",
        "answer": {
            "root_cause": "고주파 노이즈를 깎아내는 물리적 필터이므로 단순 Step 또는 Constant 신호로는 내부 코드를 100% 자극할 수 없습니다.",
            "solution": "1. 시계열 데이터 TC 입력 시 계단 함수(Step)뿐만 아니라 고주파 사인파(Sine Wave)를 혼합하여 주입합니다.<br>2. 스코프를 열고 해당 컷오프 주파수 이상의 신호가 모델 출력단에서 진폭 감소(Smoothing)를 이뤄냈는지 확인합니다.",
            "tip": "Frequency Response(Bode Plot) 커버리지를 함께 제출하여 동적 건전성을 리포팅하세요."
        }
    },
    {
        "keywords": ["ratelimiter", "변화율제한", "개념", "설명"],
        "question": "Rate Limiter 블록 개념 및 검증",
        "answer": {
            "root_cause": "단위 시간당 신호의 급격한 상승/하강 속도(Slew Rate)를 제한하는 블록으로, 제한 임계값 이상의 가파른 입력이 주어져야만 Saturation 분기가 실행됩니다.",
            "solution": "1. 블록 내부 파라미터(Rising/Falling Slew Rate)를 파악합니다.<br>2. TC 구성 시 한계값보다 '훨씬 가파른 기울기'로 Ramp 신호를 찔러 넣습니다.<br>3. 기대 출력(Expected Output) 쪽에서 기울기가 제한값 기울기대로 꺾여 나오는지를 확인하세요.",
            "tip": "Slew rate 계산 기준이 시간차 기준인지 스텝 수 기준인지 모델 샘플타임을 보며 세밀하게 조정해야 합니다."
        }
    },
    {
        "keywords": ["tc", "테스트케이스", "요구사양", "작성"],
        "question": "요구 사양서 기반 TC 도출 자동화",
        "answer": {
            "root_cause": "자연어로 쓰인 요구 사양서를 명확한 T/F나 임계치 숫자로 정량화(Formalize)하여 입력으로 구성하지 못하면 커버리지가 비게 됩니다.",
            "solution": "1. **경계값 분석(BVA)**: 사양서가 'V > 100' 이면, TC는 99, 100, 101 값을 반드시 자극해야 합니다.<br>2. **분기(Branch) 대응**: Stateflow 분기가 존재한다면, 모든 State 전이 조건이 한 번씩 활성화되는 동적 시나리오를 구성합니다.<br>3. Coverage HTML을 뽑아보고 빨간색으로 나오는 Missing 부분을 채울 신호를 역추적해 할당하세요.",
            "tip": "Simulink Test Manager (STM) 모듈에서 엑셀 기반 TC를 로드하면 일괄 실행 및 비교가 압도적으로 편해집니다."
        }
    },
    {
        "keywords": ["coverage", "커버리지", "전략", "높이", "달성"],
        "question": "Coverage (MCDC 등) 100% 향상 전략",
        "answer": {
            "root_cause": "100% 커버리지가 뜨지 않는 주요 원인은 '구조상 도달 불가한 데드 로직', '과도한 예외 방어 코드', '일부 논리곱 시나리오 미발생' 입니다.",
            "solution": "1. 리포트의 **MCDC 표(T/F 조합표)**를 열어서 정확히 어떤 논리를 빼먹었는지 역산출해냅니다.<br>2. 도달 자체가 안되는 방어 코드는 설계 부서에 알리고 사양서 수정 및 로직 제거를 협의하세요.<br>3. Calibratable (상수 제어) 파라미터 때문에 진입을 못 하는 블록은 Workspace 오버라이드를 써서 임시로 우회 테스트합니다.",
            "tip": "MCDC 분석 시에는 꼬여있는 Boolean 시그널 중 어떤 입력이 Decision 결과에 직접적 변화를 줬는지 중점적으로 봅니다."
        }
    },
    {
        "keywords": ["실행오류", "matlab오류", "뻗음", "멈춤", "크래시"],
        "question": "MATLAB / Simulink 프로세스 응답 없음(뻗음)",
        "answer": {
            "root_cause": "무거운 모델을 돌리거나 백그라운드 메모리 누수, 이전 시뮬레이션의 `slprj` 폴더 찌꺼기로 인해 엔진 실행이 정지됩니다.",
            "solution": "1. 메모리 강제 정리: 커맨드 창에 `clear all; close all; bdclose('all');`를 쳐서 열린 객체를 전부 닫아줍니다.<br>2. 모델과 동일한 위치에 있는 (또는 설정된 캐시 경로의) `slprj` 폴더를 완전히 삭제하고 재빌드합니다.<br>3. 모델 설정(Ctrl+E) > **Diagnostics** 솔버 메모리 한계 옵션을 상향 조절하세요.",
            "tip": "Fast Restart 모드를 켜둔 상태라면 잦은 오류가 발생하므로, 디버깅 시에는 Normal 상태로 돌려두세요."
        }
    },
    {
        "keywords": ["컴파일러오류", "빌드에러", "컴파일실패", "mex"],
        "question": "C/C++ 빌드 타임 오류 분석",
        "answer": {
            "root_cause": "생성되는 C 코드가 타겟 Toolchain(MinGW, MSVC)을 찾지 못하거나, 작업 경로에 비정상적인 문자열이 존재하기 때문입니다.",
            "solution": "1. **가장 흔한 에러**: 작업 경로 중 어느 하나라도 **한글 폴더명, 띄어쓰기, 특수기호**가 있으면 C 빌드 시스템은 타겟 코드를 빌드하지 않습니다. 100% 영문 경로로 바꾸세요.<br>2. 커맨드 창에 `mex -setup C++`를 재설정하여 올바른 링커를 명시적으로 잡습니다.<br>3. 특정 백신이 `.mexw64` 바이너리 생성 과정을 랜섬웨어 행위로 오탐지하는 경우 예외 처리합니다.",
            "tip": "가장 C 드라이브 루트(C:/Project/.)에 가깝고 얕은 깊이의 전용 폴더 체계를 사용하시는 것이 제일 깔끔합니다."
        }
    }
]

# ==========================================
# 3. Chatbot Logic (RAG 유사 처리 엔진)
# ==========================================
def preprocess_text(text: str) -> str:
    """질문 전처리 (소문자, 공백제거, 동의어 치환)"""
    t = text.lower().replace(" ", "")
    
    t_map = {
        "매트랩": "matlab",
        "커버리지": "coverage",
        "커버": "coverage",
        "엠브이": "mv",
        "모델베리피케이션": "mv",
        "티씨": "tc",
        "테스트케이스": "tc",
        "로우패스필터": "lowpassfilter",
        "엘피에프": "lpf",
        "레이트리미터": "ratelimiter",
        "변화율제한": "ratelimiter",
        "로우패스": "lowpassfilter"
    }
    
    for kr, en in t_map.items():
        t = t.replace(kr, en)
        
    return t

def calculate_similarity(preprocessed_question: str, keywords: list) -> int:
    """단일 질문에 매칭되는 키워드 스코어 산출"""
    score = 0
    for kw in keywords:
        if kw in preprocessed_question:
            score += 1
    return score

def generate_rag_response(raw_question: str) -> str:
    """유사도 점수를 판단하여 응답 문구를 포매팅하는 함수"""
    prep_q = preprocess_text(raw_question)
    
    scored_knowledge = []
    
    # 지식 베이스 스캐닝
    for item in KNOWLEDGE_BASE:
        score = calculate_similarity(prep_q, item["keywords"])
        if score > 0:
            scored_knowledge.append((score, item))
            
    # 매칭 실패 (Fallback)
    if not scored_knowledge:
        return """
        <div style='background-color:#fff1f2; padding: 15px; border-radius: 8px; border-left: 5px solid #f43f5e;'>
            <b>⚠️ [매칭 실패]</b><br>
            질문하신 내용과 일치하는 실무 솔루션을 찾지 못했습니다.<br>
            질문의 상황이나 오류 문구를 조금 더 구체적으로 적어주시겠어요?<br><br>
            💡 <b>이런 키워드가 포함되면 좋습니다:</b><br>
            - MATLAB 경로 설정 방법<br>
            - Coverage / 컴파일러 오류<br>
            - TC 작성 관련 요구사항<br>
            - Edge Detect 블록의 원리
        </div>
        """
        
    # 점수 내림차순 정렬
    scored_knowledge.sort(key=lambda x: x[0], reverse=True)
    max_score = scored_knowledge[0][0]
    
    matched_items = []
    for score, item in scored_knowledge:
        if score >= max_score - 1: # 최대점수와 1점 차이까지는 연관 질문(복합의도)으로 판단하여 반환
            matched_items.append(item)
        if len(matched_items) >= 3: # 너무 길지 않도록 3개 답변으로 컷
            break

    # 출력 포맷 구성 (RAG 응답 생성)
    final_response = f"**[💡 질문 분석 요약]**<br>요청하신 문맥을 분석하여 연관된 **{len(matched_items)}가지** 실무 지식을 가져왔습니다. ({', '.join([i['question'] for i in matched_items])})<br><br>"
    
    for idx, item in enumerate(matched_items):
        final_response += f"<h5 style='color:#1d4ed8; font-weight:bold;'>🔹 {item['question']}</h5>"
        final_response += f"**[원인 분석]**<br>{item['answer']['root_cause']}<br><br>"
        final_response += f"**[해결 방법]**<br>{item['answer']['solution']}<br><br>"
        final_response += f"**[실무 팁]**<br><span style='color:#047857; font-weight:600;'>{item['answer']['tip']}</span><br>"
        
        if idx < len(matched_items) - 1:
            final_response += "<hr style='margin: 15px 0; border-top: 1px dashed #cbd5e1;'>"
            
    return final_response


# ==========================================
# 4. View Components
# ==========================================
def render_dashboard():
    st.markdown("<h3 style='color: #1e293b; font-weight: 800;'>🎯 검증 워크플로우 대시보드 (진행 현황)</h3>", unsafe_allow_html=True)
    st.markdown("현재 각 실무 인원의 동적 검증 현황을 실시간으로 추적/관리합니다. (데이터 모델링: 서브시스템 & 요구 사양 단위)")
    
    df = st.session_state.req_df
    
    st.markdown("##### 📌 팀 종합 성과 매트릭스")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**총 할당 사양서**\n### {df['할당된 사양서(Total)'].sum()} 건")
    with col2:
        st.success(f"**총 누적 처리량**\n### {df['누적 처리량(Cumul)'].sum()} 건")
    with col3:
        avg_prog = df['진행률(%)'].mean()
        st.warning(f"**팀 평균 진행률**\n### {avg_prog:.1f} %")
    with col4:
        remains = df['할당된 사양서(Total)'].sum() - df['누적 처리량(Cumul)'].sum()
        st.error(f"**잔여 검증 업무**\n### {remains} 건")
        
    st.divider()

    st.markdown("##### 📋 인원별 검증 상세 대장")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "진행률(%)": st.column_config.ProgressColumn(
                "달성률 (%)", format="%.1f%%", min_value=0, max_value=100
            ),
            "난이도": st.column_config.TextColumn("업무 난이도")
        }
    )
    
    st.divider()
    
    st.markdown("##### 📊 사람별 업무 달성 현황 (Bar Chart)")
    fig = px.bar(
        df, 
        x='담당자명', 
        y='진행률(%)', 
        color='서브시스템명',
        text_auto='.1f',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(
        textfont_size=15, textangle=0, textposition="outside", cliponaxis=False, width=0.5
    )
    fig.update_layout(
        yaxis=dict(range=[0, 110], title='진행률 (%)', gridcolor='#f1f5f9'),
        xaxis=dict(title='실무 담당자'),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=20),
        legend=dict(title="분배 서브시스템")
    )
    st.plotly_chart(fig, use_container_width=True)

def render_data_input():
    st.markdown("<h3 style='color: #1e293b; font-weight: 800;'>📝 일일 데이터 입력 폼</h3>", unsafe_allow_html=True)
    st.markdown("오늘 작업한 <b>테스트 케이스 결과 및 사양서 완료 건수</b>를 입력해 주세요.<br>대시보드 상의 누적 건수 및 진행률에 즉시 자동 반영됩니다.", unsafe_allow_html=True)
    
    df = st.session_state.req_df
    
    with st.container(border=True):
        st.subheader("업데이트 정보 기입")
        
        with st.form("progress_form", clear_on_submit=True):
            user_list = df['담당자명'].tolist()
            selected_user = st.selectbox("업무 보고자(담당자) 선택", user_list)
            
            curr_data = df[df['담당자명'] == selected_user].iloc[0]
            st.info(f"**[{curr_data['서브시스템명']}]** | 작업 난이도: {curr_data['난이도']} | 하루 권장 목표량: {curr_data['하루 목표(Target)']}건")
            
            today_count = st.number_input("오늘 신규로 처리 완료한 요구 사양서(Test+Coverage 완료) 개수", min_value=0, max_value=100, value=0, step=1)
            
            submit_btn = st.form_submit_button("✅ 대시보드에 업데이트 적용 + 누적 재계산", use_container_width=True)
            
            if submit_btn:
                if today_count > 0:
                    idx = df.index[df['담당자명'] == selected_user][0]
                    
                    new_cumul = df.at[idx, '누적 처리량(Cumul)'] + today_count
                    total = df.at[idx, '할당된 사양서(Total)']
                    
                    if new_cumul > total: 
                        new_cumul = total
                    
                    st.session_state.req_df.at[idx, '누적 처리량(Cumul)'] = new_cumul
                    st.session_state.req_df.at[idx, '진행률(%)'] = round((new_cumul / total) * 100, 1)
                    
                    st.success(f"🎉 성공적으로 처리되었습니다! **{selected_user}** 님의 최종 누적률이 **{st.session_state.req_df.at[idx, '진행률(%)']}%** 로 변경되었습니다.")
                else:
                    st.error("처리 개수를 1건 이상 올바르게 입력해 주세요.")

def render_chatbot():
    st.markdown("<h3 style='color: #1e293b; font-weight: 800;'>💬 지식 기반 V&V 전문 챗봇 (RAG 유사 모델)</h3>", unsafe_allow_html=True)
    st.markdown("자체 지식 베이스(Knowledge Base)를 활용하여 오류 문구를 검색하고 해결책을 추론하여 응답합니다. (API 연동 없이 동작)")
    
    # API 입력 받는 부분 제거됨.
    chat_container = st.container(border=True, height=550)
    
    if len(st.session_state.chat_msgs) == 0:
        st.session_state.chat_msgs.append({
            "role": "assistant", 
            "content": "안녕하세요! <b>Simulink 동적 검증 및 트러블슈팅 전용 지식 챗봇</b>입니다. 무엇을 도와드릴까요?"
        })
        
    with chat_container:
        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)
                
    if prompt := st.chat_input("에러나 이론 관련 질문을 편하게 남겨주세요..."):
        st.session_state.chat_msgs.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                # RAG 검색 로직 수행
                resp = generate_rag_response(prompt)
                st.markdown(resp, unsafe_allow_html=True)
                
        st.session_state.chat_msgs.append({"role": "assistant", "content": resp})

# ==========================================
# 5. Main App Routing (상단 메뉴 바)
# ==========================================
def main():
    st.markdown("""
        <style>
        .stButton > button {
            width: 100%;
            height: 70px;
            font-size: 18px !important;
            font-weight: bold;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            background-color: #ffffff;
            border: 2px solid #e2e8f0;
            color: #334155;
            transition: all 0.2s ease-in-out;
        }
        .stButton > button:hover {
            border-color: #2563eb;
            color: #2563eb;
            background-color: #f8fafc;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }
        .stButton > button:focus {
            background-color: #eff6ff !important;
            color: #1d4ed8 !important;
            border-color: #2563eb !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 검증 대시보드"):
            st.session_state.current_page = "검증 대시보드"
    with col2:
        if st.button("📝 데이터 입력"):
            st.session_state.current_page = "데이터 입력"
    with col3:
        if st.button("💬 스마트 챗봇"):
            st.session_state.current_page = "챗봇"
            
    st.write("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    
    page = st.session_state.current_page
    if page == "검증 대시보드":
        render_dashboard()
    elif page == "데이터 입력":
        render_data_input()
    elif page == "챗봇":
        render_chatbot()

if __name__ == "__main__":
    main()