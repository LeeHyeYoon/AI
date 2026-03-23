import streamlit as st

# 📌 안티그래비티 기반 백엔드 아키텍처 (Streamlit 버전)
# 이 스크립트는 기존 FastAPI 서버를 대체하여 UI와 백엔드 로직을 동시에 제공합니다.

st.set_page_config(page_title="Simulink Verification AI", page_icon="🚀", layout="centered")

def get_bot_response(text: str) -> str:
    """
    임시로 DB와 LLM 추론 결과를 반환하는 목업(Mock-up) 엔진입니다.
    """
    q = text.lower()
    
    if "라이브러리" in q or "안 보여" in q:
        return """
            <div style="display: inline-block; background: #334155; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; margin-bottom: 8px;">🛠️ MATLAB Env 연동 (서버)</div>
            <p>Model Verification 라이브러리가 안 보이시는군요.</p>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-top: 8px;">
                <strong style="color: #0284c7;">[해결 방법]</strong>
                <ol style="margin-top: 8px; margin-bottom: 0; padding-left: 20px;">
                    <li>MATLAB 상단 <b>Home</b> 탭에서 <b>Add-Ons</b>를 클릭하세요.</li>
                    <li><b>Simulink Check</b> 또는 <b>Simulink Design Verifier</b> 툴박스가 설치되어 있는지 확인합니다.</li>
                    <li>설치되어 있다면 Library Browser에서 우클릭 후 <b>Refresh Library Browser</b>를 선택해 보세요.</li>
                </ol>
            </div>
        """
    elif "데드 로직" in q or "check_brake" in q:
         return """
            <div style="display: inline-block; background: #0284c7; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; margin-bottom: 8px;">📊 Issue DB 연동 (서버)</div>
            <p>네, <code>Check_Brake_Pressure</code> 모듈에서 <b>과거에 발견된 데드 로직 이력</b>이 서버 DB에서 조회되었습니다.</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 10px; font-size: 14px;">
                <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1; text-align: left;">
                    <th style="padding: 8px;">발생 일자</th>
                    <th style="padding: 8px;">원인 (Root Cause)</th>
                    <th style="padding: 8px;">해결 방법</th>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px;"><b>2024-02</b></td>
                    <td style="padding: 8px;">입력 압력 한도가 80인데, 검증 분기조건이 &gt;100으로 설정됨</td>
                    <td style="padding: 8px; color: #047857;"><b>임계값을 80으로 하향 조정</b></td>
                </tr>
            </table>
            
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 12px;">
                <strong style="color: #047857; font-size: 13px;">💡 추천 액션</strong>
                <p style="margin: 4px 0 0 0; font-size: 13px;">현재 수정된 임계값 파라미터가 Data Dictionary 영역에 정상 링크되어 있는지 추가로 확인해 보시길 권장합니다.</p>
            </div>
        """
    elif "요구사항" in q and ("calc" in q or "바뀐" in q):
        return """
            <div style="display: inline-block; background: #7c3aed; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; margin-bottom: 8px;">🔗 Requirement DB 조회 완료 (서버)</div>
            <p>네, <code>Calc_Speed</code> 관련 변경된 상태 코드 1건이 서버에서 확인되었습니다.</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 15px; font-size: 14px;">
                <tr style="background: #f1f5f9; border-bottom: 2px solid #cbd5e1; text-align: left;">
                    <th style="padding: 8px;">Req ID</th>
                    <th style="padding: 8px;">변경 내용</th>
                    <th style="padding: 8px; color: #e11d48;">검증 상태</th>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px; font-family: monospace;"><b>REQ-001</b></td>
                    <td style="padding: 8px;">속도 제한 로직 완화 (120→130km/h)</td>
                    <td style="padding: 8px; color: #e11d48;"><b>⚠️ 재검증 요망</b></td>
                </tr>
            </table>

            <div style="border-left: 3px solid #7c3aed; padding-left: 12px; margin-bottom: 12px;">
                <strong style="color: #7c3aed; font-size: 14px;">📊 영향도 파악 통계</strong>
                <ul style="margin-top: 4px; margin-bottom: 0; padding-left: 20px; font-size: 13px;">
                    <li>관련 링크 블록: <code>Saturation</code></li>
                    <li>리스크: 기존 120km/h 경계값 분석 TC <span style="color: #e11d48; font-weight: bold;">100% FAILED 처리</span> 예상됨.</li>
                </ul>
            </div>
            
            <button style="background: #7c3aed; color: white; border: none; padding: 6px 16px; border-radius: 6px; font-weight: bold; cursor: pointer;">🚀 TC 자동 업데이트 요청</button>
        """
    else:
        return """
            <p style="margin: 0;">
                [서버 응답 - Fallback] 죄송해요. 아직 해당 질문을 분석할 서버 로직이나 문서(RAG)가 연결되지 않았습니다.<br><br>
                다른 키워드(예: <b>'요구사항'</b>, <b>'데드 로직'</b>, <b>'라이브러리'</b> 등)로 백엔드 응답을 테스트해보세요.
            </p>
        """

st.title("🚀 Simulink Verification AI")
st.caption("안티그래비티 기반 백엔드 아키텍처 (Streamlit 프로토타입)")

# 채팅 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! Simulink Verification AI 입니다. 무엇을 도와드릴까요? (예: 데드 로직, 요구사항)"}
    ]

# 이전 채팅 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 봇 응답 생성 및 표시
    with st.chat_message("assistant"):
        response_html = get_bot_response(prompt)
        st.markdown(response_html, unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": response_html})