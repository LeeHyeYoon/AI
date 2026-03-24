# Simulink Verification Dashboard & Chatbot Walkthrough

## Overview
The V&V Streamlit app has been completely upgraded into a 3-page, integrated platform for tracking verification progress, uploading daily task logs, and troubleshooting with an AI assistant.

## New Features
1. **Button-based Navigation Menu**: Removed the sidebar and introduced wide, card-like buttons ("📊 검증 대시보드", "📝 데이터 입력", "💬 스마트 챗봇") for a modern web application feel.
2. **Dashboard View**: Displays the verification progress of team members using `st.dataframe` and a `plotly` bar chart. Real-time metrics automatically calculate completion percentages.
3. **Data Input Form**: A form where assignees can log their newly handled test cases to automatically progress their tracking indicators. State is saved using `st.session_state`.
4. **Expanded Knowledge Base**: The Chatbot is equipped with an extensive set of inference rules:
   - *Setup & License*: MATLAB/MV/Coverage setup guides.
   - *Core Concepts*: Edge Detect, LPF, Rate Limiter functionality.
   - *V&V Methods*: Writing TC for BVA, Coverage 100% strategies.
   - *Troubleshooting*: Resolving run crashes and C++ Compiler errors.

## Validation Results
- Code structure follows Streamlit best practices (`st.session_state`, `st.columns`, `st.form`).
- The application properly saves progress state between tabs.
- The chatbot responds to a very wide array of domain-specific topics requested by the user, presenting the Root Cause -> Solution paradigm format.
