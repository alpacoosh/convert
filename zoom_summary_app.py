import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import re

# ✅ CSV 처리 함수
def process_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)

    # 필요한 컬럼만 추출
    df = df[['이름(원래 이름)', '참가 시간', '참가 시간(2)', '나간 시간(2)', '나간 시간', '기간(분)']].copy()

    # 괄호 제거 (예: 홍길동 (00초/홍길동) → 홍길동)
    df['이름(원래 이름)'] = df['이름(원래 이름)'].apply(lambda x: re.sub(r'\s*\([^)]*\)', '', str(x)).strip())

    # 문자열 → datetime 변환
    time_cols = ['참가 시간', '참가 시간(2)', '나간 시간(2)', '나간 시간']
    for col in time_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # 그룹 요약
    grouped = df.groupby('이름(원래 이름)').agg({
        '기간(분)': 'sum',
        '참가 시간': 'min',
        '참가 시간(2)': 'min',
        '나간 시간(2)': 'max',
        '나간 시간': 'max'
    }).reset_index()

    # 시간 차이 계산 (분 단위)
    grouped['참가시간(3)'] = (grouped['참가 시간(2)'] - grouped['참가 시간']).dt.total_seconds() // 60
    grouped['나간시간(3)'] = (grouped['나간 시간'] - grouped['나간 시간(2)']).dt.total_seconds() // 60

    # 컬럼 정렬
    result = grouped[['이름(원래 이름)', '기간(분)', '참가 시간', '참가 시간(2)', '나간 시간(2)', '나간 시간', '참가시간(3)', '나간시간(3)']]
    return result

# ✅ CSV 변환 함수
def convert_df_to_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    return buffer

# ✅ Streamlit 앱 구성
st.set_page_config(page_title="Zoom 참가자 요약", layout="centered")
st.title("📊 Zoom 참가자 이수 요약")
st.markdown("CSV 파일을 업로드하면 참가자별 총 이수 시간과 시간 범위를 계산하고, 추가 시간 분석 결과를 보여줍니다.")

# ✅ CSS로 표 스타일 조정 (스크롤 제거, 글씨 작게)
st.markdown("""
    <style>
    .dataframe td, .dataframe th {
        font-size: 13px !important;
        padding: 4px 8px !important;
    }
    .element-container:has(.dataframe) {
        max-width: 100% !important;
        overflow-x: auto;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ 파일 업로드
uploaded_file = st.file_uploader("✅ CSV 파일 업로드", type=["csv"])

if uploaded_file:
    try:
        summary_df = process_csv(uploaded_file)

        st.success("요약 성공! 아래에서 결과 확인 및 다운로드 가능합니다.")
        st.dataframe(summary_df)

        # ✅ 다운로드 버튼
        now_str = datetime.now().strftime('%Y%m%d_%H%M')
        file_name = f"zoom_summary_{now_str}.csv"
        st.download_button(
            label="📥 요약 CSV 다운로드",
            data=convert_df_to_csv(summary_df),
            file_name=file_name,
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ 처리 중 오류 발생: {e}")
