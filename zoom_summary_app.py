import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# 올바른 열 이름이 들어간 파일 기준으로 처리
def process_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)

    # 필요한 열
    time_cols = [
        '1차시 시작', '1차시 종료',
        '2차시 시작', '2차시 종료',
        '3차시 시작', '3차시 종료',
        '4차시 시작', '4차시 종료'
    ]
    df = df[['이름(원래 이름)'] + time_cols + ['기간(분)']].copy()

    # 이름 정리
    df['이름(원래 이름)'] = df['이름(원래 이름)'].str.replace(r"\s*\([^)]*\)", "", regex=True).str.strip()

    # 시간 파싱
    for col in time_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # 그룹 요약
    summary = df.groupby('이름(원래 이름)').agg({
        '1차시 시작': 'min', '1차시 종료': 'max',
        '2차시 시작': 'min', '2차시 종료': 'max',
        '3차시 시작': 'min', '3차시 종료': 'max',
        '4차시 시작': 'min', '4차시 종료': 'max',
    }).reset_index()

    # 접속 시간 계산
    summary['1교시 접속시간'] = (summary['1차시 종료'] - summary['1차시 시작']).dt.total_seconds() // 60
    summary['2교시 접속시간'] = (summary['2차시 시작'] - summary['1차시 종료']).dt.total_seconds() // 60
    summary['3교시 접속시간'] = (summary['3차시 시작'] - summary['2차시 종료']).dt.total_seconds() // 60
    summary['4교시 접속시간'] = (summary['4차시 시작'] - summary['3차시 종료']).dt.total_seconds() // 60

    return summary


# ✅ 다운로드용 CSV 변환
def convert_df_to_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    return buffer

# ✅ Streamlit 앱 UI
st.set_page_config(page_title="Zoom 교시별 접속 분석", layout="wide")
st.title("📊 Zoom 교시별 접속 시간 요약")
st.markdown("업로드된 Zoom CSV 파일에서 참가자의 교시별 접속 시간을 자동으로 분석합니다.")

uploaded_file = st.file_uploader("✅ CSV 파일 업로드", type=["csv"])

if uploaded_file:
    try:
        result_df = process_csv(uploaded_file)
        st.success("✅ 분석 성공! 아래 결과를 확인하세요.")
        st.dataframe(result_df)

        # 다운로드 버튼
        now_str = datetime.now().strftime('%Y%m%d_%H%M')
        st.download_button(
            label="📥 분석 결과 CSV 다운로드",
            data=convert_df_to_csv(result_df),
            file_name=f"zoom_접속시간_요약_{now_str}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ 처리 중 오류 발생: {e}")
