import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# ✅ 차시별 접속시간 계산 함수
def calc_total_minutes(df, start_col, end_col):
    df = df.dropna(subset=[start_col, end_col]).copy()
    df['차시_접속시간'] = (pd.to_datetime(df[end_col]) - pd.to_datetime(df[start_col])).dt.total_seconds() / 60
    return df.groupby('이름(원래 이름)')['차시_접속시간'].sum().reset_index()

# ✅ 통합 분석 함수
def process_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)

    df['이름(원래 이름)'] = df['이름(원래 이름)'].str.replace(r"\s*\([^)]*\)", "", regex=True).str.strip()
    
    # 시간 컬럼 정리
    time_cols = [
        '1차시 시작', '1차시 종료',
        '2차시 시작', '2차시 종료',
        '3차시 시작', '3차시 종료',
        '4차시 시작', '4차시 종료'
    ]
    for col in time_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 각 차시 접속시간 계산
    g1 = calc_total_minutes(df, '1차시 시작', '1차시 종료').rename(columns={'차시_접속시간': '1교시 접속시간'})
    g2 = calc_total_minutes(df, '2차시 시작', '2차시 종료').rename(columns={'차시_접속시간': '2교시 접속시간'})
    g3 = calc_total_minutes(df, '3차시 시작', '3차시 종료').rename(columns={'차시_접속시간': '3교시 접속시간'})
    g4 = calc_total_minutes(df, '4차시 시작', '4차시 종료').rename(columns={'차시_접속시간': '4교시 접속시간'})

    # 시간 정보 요약 (가장 빠른 시작 ~ 가장 늦은 종료)
    time_info = df.groupby('이름(원래 이름)')[time_cols].agg(['min', 'max'])
    time_info.columns = ['_'.join(col).strip() for col in time_info.columns.values]
    time_info = time_info.reset_index()

    # 접속시간 병합
    result = g1.merge(g2, on='이름(원래 이름)', how='outer') \
               .merge(g3, on='이름(원래 이름)', how='outer') \
               .merge(g4, on='이름(원래 이름)', how='outer') \
               .merge(time_info, on='이름(원래 이름)', how='left')

    # NaN → 0
    for col in ['1교시 접속시간', '2교시 접속시간', '3교시 접속시간', '4교시 접속시간']:
        result[col] = result[col].fillna(0).astype(int)

    # 통합 접속시간 = 전체 차시 합
    result['통합 접속시간'] = result[['1교시 접속시간', '2교시 접속시간', '3교시 접속시간', '4교시 접속시간']].sum(axis=1)

    return result

def convert_df_to_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Zoom 교시별 접속 분석", layout="wide")
st.title("📊 Zoom 교시별 접속 시간 + 시간정보 요약")
st.markdown("중복 접속 포함한 교시별 접속시간 및 시작/종료시간 확인 가능")

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
            file_name=f"zoom_접속시간_포함_{now_str}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"❌ 처리 중 오류 발생: {e}")
