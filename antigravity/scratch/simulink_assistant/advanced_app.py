import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ==========================================
# 0. Page Configuration & Professional CSS
# ==========================================
st.set_page_config(
    page_title="V&V 통합 관리 시스템 v3.1",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
/* 전체 배경 */
.main { background-color: #f8fafc; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #0f172a; color: white; }

/* 버튼 디자인 */
.stButton > button {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid #334155 !important;
    height: 45px;
    font-weight: 600;
    width: 100%;
}
.stButton > button:hover {
    border: 1px solid #3b82f6 !important;
    background-color: #1e40af !important;
}

/* KPI 카드 스타일 */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
    text-align: center;
}

/* 챗봇 타이틀 */
.chat-title { color:#1e293b; font-weight:800; font-size:28px; margin-bottom:10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. Session State (데이터 초기화 및 데이터프레임 선언)
# ==========================================
if "init_v3" not in st.session_state:
    st.session_state.users = ["주해원 선임", "김재강 선임", "황지원 전임", "이혜윤 전임"]
    st.session_state.subsys_master = {
        'Brake_Control': {'owner': '이혜윤', 'req_total': 120},
        'Speed_Limit': {'owner': '김철수', 'req_total': 80},
        'Sensor_Filter': {'owner': '박영희', 'req_total': 50},
        'Battery_Mng': {'owner': '최동훈', 'req_total': 150},
        'Fail_Safe': {'owner': '정민수', 'req_total': 90}
    }
    
    # [수정] 대시보드에 표시될 데이터프레임 초기화 로직 추가
if "dv_history" not in st.session_state:

    st.session_state.dv_history = pd.DataFrame(columns=[
        'Date',
        'Engineer',
        'Model Version',
        'Subsystem',
        'Allocated Requirements',
        'Verified Subsystems',
        'Verified Requirements'
    ])


if "spec_history" not in st.session_state:

    st.session_state.spec_history = pd.DataFrame(columns=[
        'Date',
        'Engineer',
        'Model Version',
        'Subsystem',
        'Allocated Requirements',
        'Modified',
        'Newly Created'
        'Deleted'
    ])
    
    st.session_state.current_menu = "통합 대시보드"
    st.session_state.chat_msgs = []
    st.session_state.init_v3 = True

# ==========================================
# 2. RAG Knowledge Base & Engine
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
        "매트랩": "matlab", "커버리지": "coverage", "커버": "coverage",
        "엠브이": "mv", "모델베리피케이션": "mv", "티씨": "tc",
        "테스트케이스": "tc", "로우패스필터": "lowpassfilter", "엘피에프": "lpf",
        "레이트리미터": "ratelimiter", "변화율제한": "ratelimiter", "로우패스": "lowpassfilter"
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
    
    for item in KNOWLEDGE_BASE:
        score = calculate_similarity(prep_q, item["keywords"])
        if score > 0:
            scored_knowledge.append((score, item))
            
    if not scored_knowledge:
        return """
        <div style='background-color:#fff1f2; padding: 15px; border-radius: 8px; border-left: 5px solid #f43f5e;'>
            <b>⚠️ [매칭 실패]</b><br>
            질문하신 내용과 일치하는 실무 솔루션을 찾지 못했습니다.<br><br>
            💡 <b>추천 키워드:</b> MATLAB 경로, Coverage, TC 작성, Rate Limiter
        </div>
        """
        
    scored_knowledge.sort(key=lambda x: x[0], reverse=True)
    max_score = scored_knowledge[0][0]
    
    matched_items = []
    for score, item in scored_knowledge:
        if score >= max_score - 1:
            matched_items.append(item)
        if len(matched_items) >= 3:
            break

    final_response = f"**[💡 질문 분석 요약]**<br>연관된 **{len(matched_items)}가지** 실무 지식을 찾았습니다. ({', '.join([i['question'] for i in matched_items])})<br><br>"
    
    for idx, item in enumerate(matched_items):
        final_response += f"<h5 style='color:#1d4ed8; font-weight:bold;'>🔹 {item['question']}</h5>"
        final_response += f"**[원인 분석]**<br>{item['answer']['root_cause']}<br><br>"
        final_response += f"**[해결 방법]**<br>{item['answer']['solution']}<br><br>"
        final_response += f"**[실무 팁]**<br><span style='color:#047857; font-weight:600;'>{item['answer']['tip']}</span><br>"
        if idx < len(matched_items) - 1:
            final_response += "<hr style='margin: 15px 0; border-top: 1px dashed #cbd5e1;'>"
            
    return final_response

# ==========================================
# 4. Sidebar Menu
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🛡️ V&V Control</h2>", unsafe_allow_html=True)
    st.write("---")
    if st.button("📊 통합 대시보드"): st.session_state.current_menu = "통합 대시보드"
    if st.button("📥 검증 데이터 입력"): st.session_state.current_menu = "검증 데이터 입력"
    if st.button("📄 사양서 데이터 입력"): st.session_state.current_menu = "사양서 데이터 입력"
    if st.button("💬 스마트 챗봇"): st.session_state.current_menu = "스마트 챗봇"

# ==========================================
# 5. Main Contents Logic
# ==========================================

# --- A. 통합 대시보드 ---
if st.session_state.current_menu == "통합 대시보드":
    st.title("📊 V&V 통합 대시보드")
    
    tab1, tab2 = st.tabs(["🛡️ 검증 현황", "📄 사양서 현황"])

    with tab1:
        df_dv = st.session_state.dv_history
        if not df_dv.empty:
            c1, c2, c3 = st.columns(3)
            # 수치 데이터 타입 보장
            df_dv['Allocated Requirements'] = pd.to_numeric(df_dv['Allocated Requirements'])
            df_dv['Verified Requirements'] = pd.to_numeric(df_dv['Verified Requirements'])
            
            total_req = df_dv['Allocated Requirements'].sum()
            total_done = df_dv['Verified Requirements'].sum()
            ratio = (total_done / total_req * 100) if total_req > 0 else 0
            
            c1.metric("총 할당 요구사항", f"{total_req}개")
            c2.metric("검증 완료", f"{total_done}개")
            c3.metric("평균 달성률", f"{ratio:.1f}%")
            
            fig = px.bar(df_dv, x='Engineer', y='Verified Requirements', color='Subsystem', title="담당자별 검증 수행 현황")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_dv, use_container_width=True)
        else:
            st.info("데이터를 먼저 입력해 주세요 (좌측 '검증 데이터 입력' 메뉴)")

    with tab2:
        df_sp = st.session_state.spec_history
        if not df_sp.empty:
            # 일자별 차트 생성을 위해 날짜 정렬
            df_sp = df_sp.sort_values('Date')
            fig2 = px.line(df_sp, x='Date', y='Modified Specs', color='Engineer', title="일자별 사양서 수정 추이")
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df_sp, use_container_width=True)
        else:
            st.info("사양서 작업 내역이 없습니다.")

# --- B. 검증 데이터 입력 ---
elif st.session_state.current_menu == "검증 데이터 입력":
    st.title("📥 검증 결과 입력")
    with st.form("dv_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            in_date = st.date_input("Date", date.today())
            in_user = st.selectbox("Engineer", st.session_state.users)
            in_ver = st.text_input("Model Version")
            in_sub = st.selectbox("Subsystem", list(st.session_state.subsys_master.keys()))
        with col2:
            in_total = st.number_input("Allocated Requirements", min_value=1, value=10)
            in_sub_cnt = st.number_input("Verified Subsystems", min_value=0, value=1)
            in_done = st.number_input("Verified Requirements", min_value=0, value=5)
        
        if st.form_submit_button("검증 데이터 저장"):
            new_row = pd.DataFrame([{
                'Date': in_date, 'Engineer': in_user, 'Model Version': in_ver, 'SubSystem': in_sub,
                'Allocated Requirements': in_total, 'Verified Subsystems': in_sub_cnt, 'Verified Requirements': in_done
            }])
            # 데이터 저장 및 세션 반영
            st.session_state.dv_history = pd.concat([st.session_state.dv_history, new_row], ignore_index=True)
            st.success(f"{in_user}님의 데이터가 저장되었습니다!")
            # [수정] 데이터 즉시 반영을 위한 rerun
            st.rerun()

# --- C. 사양서 데이터 입력 ---
elif st.session_state.current_menu == "사양서 데이터 입력":
    st.title("📄 사양서 작업 입력")
    with st.form("spec_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            s_date = st.date_input("Date", date.today())
            s_user = st.selectbox("Engineer", st.session_state.users)
            s_ver = st.text_input("Model Version")
            s_sub = st.selectbox("SubSystem", list(st.session_state.subsys_master.keys()))
        with c2:
            s_assign = st.number_input("Allocated Requirements", min_value=0)
            s_mod = st.number_input("Modified", min_value=0)
            s_gen = st.number_input("Newly Created", min_value=0)
            s_del = st.number_input("Deleted", min_value=0)
            
        if st.form_submit_button("사양서 데이터 저장"):
            new_spec = pd.DataFrame([{
                'Date': s_date, 'Engineer': s_user, 'Model Version': s_ver, 'SubSystem': s_sub,
                'Allocated Requirements': s_assign, 'Modified': s_mod, 'Newly Created': s_gen, 'Deleted': s_del
            }])
            st.session_state.spec_history = pd.concat([st.session_state.spec_history, new_spec], ignore_index=True)
            st.success("사양서 작업 기록이 저장되었습니다.")
            # [수정] 데이터 즉시 반영을 위한 rerun
            st.rerun()

# --- D. 스마트 챗봇 ---
elif st.session_state.current_menu == "스마트 챗봇":
    st.markdown("<h3 style='color: #1e293b; font-weight: 800;'>💬 지식 기반 V&V 전문 챗봇 (RAG 유사 모델)</h3>", unsafe_allow_html=True)
    st.markdown("자체 지식 베이스(Knowledge Base)를 활용하여 오류 문구를 검색하고 해결책을 추론합니다.")
    
    chat_container = st.container(border=True, height=550)
    
    if not st.session_state.chat_msgs:
        st.session_state.chat_msgs.append({"role": "assistant", "content": "안녕하세요! <b>Simulink 동적 검증 전용 지식 챗봇</b>입니다. 무엇을 도와드릴까요?"})
        
    with chat_container:
        for msg in st.session_state.chat_msgs:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)
                
    if prompt := st.chat_input("에러나 이론 관련 질문을 남겨주세요..."):
        st.session_state.chat_msgs.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"): 
                st.markdown(prompt)
            with st.chat_message("assistant"):
                resp = generate_rag_response(prompt)
                # [수정] 들여쓰기 오류 해결
                st.markdown(resp, unsafe_allow_html=True)
        st.session_state.chat_msgs.append({"role": "assistant", "content": resp})