import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

def get_duration(df, start_col, end_col):
    return (pd.to_datetime(df[end_col], errors='coerce') - pd.to_datetime(df[start_col], errors='coerce')).dt.total_seconds() // 60

def process_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df['이름(원래 이름)'] = df['이름(원래 이름)'].str.replace(r"\s*\([^)]*\)", "", regex=True).str.strip()

    # 시간 컬럼
    time_cols = [
        '1차시 시작', '1차시 종료',
        '2차시 시작', '2차시 종료',
        '3차시 시작', '3차시 종료',
        '4차시 시작', '4차시 종료'
    ]
    for col in time_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # 그룹 통합: 최소 시작, 최대 종료
    grouped = df.groupby('이름(원래 이름)').agg({
        '1차시 시작': 'min', '1차시 종료': 'max',
        '2차시 시작': 'min', '2차시 종료': 'max',
        '3차시 시작': 'min', '3차시 종료': 'max',
        '4차시 시작': 'min', '4차시 종료': 'max',
        '기간(분):'sum'
    }).reset_index()

    # 접속 시간 계산
    grouped['1교시 접속시간'] = get_duration(grouped, '1차시 시작', '1차시 종료')
    grouped['2교시 접속시간'] = get_duration(grouped, '2차시 시작', '2차시 종료')
    grouped['3교시 접속시간'] = get_duration(grouped, '3차시 시작', '3차시 종료')
    grouped['4교시 접속시간'] = get_duration(grouped, '4차시 시작', '4차시 종료')
    grouped['통합 접속시간'] = grouped[['1교시 접속시간', '2교시 접속시간', '3교시 접속시간', '4교시 접속시간']].sum(axis=1)

    # 열 순서 정리
    final_cols = [
        '이름(원래 이름)',
        '1차시 시작', '1차시 종료',
        '2차시 시작', '2차시 종료',
        '3차시 시작', '3차시 종료',
        '4차시 시작', '4차시 종료',
        '1교시 접속시간', '2교시 접속시간', '3교시 접속시간', '4교시 접속시간',
        '통합 접속시간'
    ]
    return grouped[final_cols]

def convert_df_to_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    return buffer

# ✅ Streamlit UI
st.set_page_config(page_title="Zoom 교시별 접속시간", layout="wide")
st.title("📊 Zoom 교시별 접속 요약")
st.markdown("**시작/종료 시간 → 접속시간 4개 → 통합 접속시간** 순으로 표시됩니다.")

uploaded_file = st.file_uploader("✅ CSV 파일 업로드", type=["csv"])

if uploaded_file:
    try:
        result_df = process_csv(uploaded_file)
        st.success("✅ 분석 성공! 아래 결과를 확인하세요.")
        st.dataframe(result_df)

        now_str = datetime.now().strftime('%Y%m%d_%H%M')
        st.download_button(
            label="📥 분석 결과 CSV 다운로드",
            data=convert_df_to_csv(result_df),
            file_name=f"zoom_접속시간_분석_{now_str}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
