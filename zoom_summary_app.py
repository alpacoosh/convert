import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

def process_csv(uploaded_file):
    # CSV 읽기
    df = pd.read_csv(uploaded_file)

    # 필요한 컬럼만 추출
    df_selected = df[['이름(원래 이름)', '참가 시간', '나간 시간', '기간(분)']].copy()

    # 문자열 → datetime 변환
    df_selected['참가 시간'] = pd.to_datetime(df_selected['참가 시간'])
    df_selected['나간 시간'] = pd.to_datetime(df_selected['나간 시간'])

    # 그룹 요약 계산
    summary_df = df_selected.groupby('이름(원래 이름)').agg({
        '기간(분)': 'sum',
        '참가 시간': 'min',
        '나간 시간': 'max'
    }).reset_index()

    return summary_df

def convert_df_to_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    return buffer

# --- Streamlit UI ---
st.set_page_config(page_title="Zoom 참가자 요약", layout="centered")

st.title("📊 Zoom 참가자 이수 요약")
st.markdown("CSV 파일을 업로드하면 참가자별 총 이수 시간과 시간 범위를 계산해줍니다.")

uploaded_file = st.file_uploader("✅ CSV 파일 업로드", type=["csv"])

if uploaded_file:
    try:
        summary_df = process_csv(uploaded_file)
        st.success("요약 성공! 아래에서 결과 확인 및 다운로드 가능합니다.")
        st.dataframe(summary_df)

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
