import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# ✅ 접속 시간 계산 함수
def get_duration(df, start_col, end_col):
    return (pd.to_datetime(df[end_col], errors='coerce') - pd.to_datetime(df[start_col], errors='coerce')).dt.total_seconds() // 60

# ✅ 전체 처리 함수
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

    # 접속시간 계산
    df['1교시 접속시간'] = get_duration(df, '1차시 시작', '1차시 종료')
    df['2교시 접속시간'] = get_duration(df, '2차시 시작', '2차시 종료')
    df['3교시 접속시간'] = get_duration(df, '3차시 시작', '3차시 종료')
    df['4교시 접속시간'] = get_duration(df, '4차시 시작', '4차시 종료')

    # 통합 접속시간
    df['통합 접속시간'] = df[['1교시 접속시간', '2교시 접속시간', '3교시 접속시간', '4교시 접속시간']].sum(axis=1)

    # ✅ 원하는 순서로 컬럼 정렬
    final_cols = [
        '이름(원래 이름)',
        '1교시 접속시간', '2교시 접속시간', '3교시 접속시간', '4교시 접속시간',
        '1차시 시작', '1차시 종료',
        '2차시 시작', '2차시 종료',
        '3차시 시작', '3차시 종료',
        '4차시 시작', '4차시 종료',
        '통합 접속시간'
    ]
    return df[final_cols]

# ✅ CSV 변환
def convert_df_to_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    return buffer

# ✅ Streamlit UI
st.set_page_config(page_title="Zoom 교시별 접속시간", layout="wide")
st.title("📊 Zoom 교시별 접속 요약")
st.markdown("교시별 접속 시간 → 차시별 시작/종료 시간 → 통합 접속시간 순으로 표시됩니다.")

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
            file_name=f"zoom_교시별_접속요약_{now_str}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
