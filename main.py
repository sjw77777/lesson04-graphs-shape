import streamlit as st
import pandas as pd
import plotly.express as px

DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 해당 기간에 개봉한 "
    "216편의 데이터를 살펴봅니다."
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, dtype={"movieCd": str, "openDt": str})

    required_columns = [
        "movieCd", "movieNm", "openDt", "genre", "nation",
        "first_scrn", "first_show", "first_week_audi",
        "total_audi", "days_in_top10",
    ]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError("데이터에서 필요한 열을 찾을 수 없습니다: " + ", ".join(missing))

    # 장르가 '드라마|코미디'처럼 여러 개면 첫 번째 장르만 사용합니다.
    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
        .replace("", "미분류")
    )
    return df

try:
    df = load_data()
except Exception as error:
    st.error("영화 데이터를 불러오지 못했습니다. 데이터 주소와 인터넷 연결을 확인해 주세요.")
    st.caption(f"오류 내용: {error}")
    st.stop()

st.caption(f"불러온 영화 데이터: {len(df):,}편")

# 그래프 1: 장르별 영화 편수
st.divider()
st.header("1. 장르별 영화 편수")
st.write("각 장르에 해당하는 영화가 전체에서 어느 정도를 차지하는지 확인합니다.")

genre_counts = (
    df["genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)
genre_counts["비율"] = genre_counts["영화 편수"] / genre_counts["영화 편수"].sum() * 100

fig = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.48,
    custom_data=["비율"],
)
fig.update_traces(
    textposition="inside",
    textinfo="label",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{customdata[0]:.1f}%<extra></extra>"
    ),
)
fig.update_layout(
    showlegend=True,
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=10, r=10),
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("이 그래프로 알 수 있는 것")
st.text_area(
    "알게 된 점을 한 문장으로 적어 보세요.",
    placeholder="예: 전체 영화 중 ○○ 장르가 가장 많은 비중을 차지한다.",
    key="genre_observation",
    label_visibility="collapsed",
)

with st.expander("장르별 편수 표 보기"):
    display_counts = genre_counts.copy()
    display_counts["비율"] = display_counts["비율"].map(lambda value: f"{value:.1f}%")
    st.dataframe(display_counts, hide_index=True, use_container_width=True)
