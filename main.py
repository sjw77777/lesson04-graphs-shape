import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "해당 기간에 개봉한 216편의 데이터를 살펴봅니다."
)


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(
        DATA_URL,
        dtype={"movieCd": str, "openDt": str}
    )

    required_columns = [
        "movieCd", "movieNm", "openDt", "genre", "nation",
        "first_scrn", "first_show", "first_week_audi",
        "total_audi", "days_in_top10"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "데이터에 필요한 열이 없습니다: "
            + ", ".join(missing)
        )

    # 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
        .replace("", "미분류")
    )

    # 총 관객 수를 숫자로 변환
    df["total_audi"] = pd.to_numeric(
        df["total_audi"],
        errors="coerce"
    ).fillna(0)

    return df


try:
    df = load_data()
except Exception as error:
    st.error(
        "영화 데이터를 불러오지 못했습니다. "
        "데이터 주소와 인터넷 연결을 확인해 주세요."
    )
    st.caption(f"오류 내용: {error}")
    st.stop()

st.caption(f"불러온 영화 데이터: {len(df):,}편")


# ---------------------------------
# 그래프 1. 장르별 영화 편수 도넛 그래프
# ---------------------------------

st.divider()
st.header("1. 장르별 영화 편수")
st.write(
    "각 장르에 해당하는 영화가 전체에서 "
    "어느 정도를 차지하는지 확인합니다."
)

genre_counts = (
    df["genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

genre_counts["비율"] = (
    genre_counts["영화 편수"]
    / genre_counts["영화 편수"].sum()
    * 100
)

fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.48,
    custom_data=["비율"]
)

fig1.update_traces(
    textposition="inside",
    textinfo="label",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{customdata[0]:.1f}%"
        "<extra></extra>"
    )
)

fig1.update_layout(
    showlegend=True,
    legend_title_text="장르",
    margin=dict(t=20, b=20, l=10, r=10)
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "알게 된 점을 한 문장으로 적어 보세요.",
    placeholder="예: 전체 영화 중 ○○ 장르가 가장 많은 비중을 차지한다.",
    key="genre_observation",
    label_visibility="collapsed"
)

with st.expander("장르별 편수 표 보기"):
    display_counts = genre_counts.copy()
    display_counts["비율"] = display_counts["비율"].map(
        lambda value: f"{value:.1f}%"
    )

    st.dataframe(
        display_counts,
        hide_index=True,
        use_container_width=True
    )


# ---------------------------------
# 그래프 2. 장르별 영화 트리맵
# ---------------------------------

st.divider()
st.header("2. 장르별 영화 총 관객 트리맵")
st.write(
    "장르 안에 개별 영화를 표시합니다. "
    "각 영화의 칸 크기는 총 관객 수에 비례합니다."
)

treemap_df = df.copy()

treemap_df["영화명"] = (
    treemap_df["movieNm"]
    .fillna("영화명 없음")
    .astype(str)
)

# 총 관객 수가 0보다 큰 영화만 표시
treemap_df = treemap_df[
    treemap_df["total_audi"] > 0
].copy()

# 영화명이 중복되는 경우에도 각 영화를 구분
treemap_df["영화 항목"] = (
    treemap_df["영화명"]
    + " ("
    + treemap_df["movieCd"].astype(str)
    + ")"
)

if treemap_df.empty:
    st.warning(
        "트리맵을 그릴 수 있는 총 관객 데이터가 없습니다."
    )

else:
    fig2 = px.treemap(
        treemap_df,
        path=[
            px.Constant("전체 영화"),
            "genre",
            "영화 항목"
        ],
        values="total_audi",
        custom_data=[
            "영화명",
            "total_audi"
        ]
    )

    fig2.update_traces(
        textinfo="label",
        hovertemplate=(
            "영화명: %{customdata[0]}<br>"
            "총 관객: %{customdata[1]:,.0f}명"
            "<extra></extra>"
        )
    )

    fig2.update_layout(
        margin=dict(t=20, b=20, l=10, r=10)
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

st.subheader("이 그래프로 알 수 있는 것")

st.text_area(
    "트리맵을 보고 알게 된 점을 한 문장으로 적어 보세요.",
    placeholder="예: 총 관객 수가 많은 영화는 ○○ 장르에 속한다.",
    key="treemap_observation",
    label_visibility="collapsed"
)
# ---------------------------------
# 그래프 3. 총 관객 수 히스토그램
# ---------------------------------

st.divider()
st.header("3. 영화별 총 관객 수 분포")
st.write(
    "영화별 총 관객 수가 어느 구간에 많이 분포하는지 확인합니다."
)

# 총 관객 수 데이터 준비
hist_df = df.copy()
hist_df["total_audi"] = pd.to_numeric(
    hist_df["total_audi"],
    errors="coerce"
)

hist_df = hist_df.dropna(subset=["total_audi"])

if hist_df.empty:
    st.warning("히스토그램을 그릴 관객 데이터가 없습니다.")

else:
    audience = hist_df["total_audi"].to_numpy()

    # 관객 수가 가장 많은 영화 찾기
    max_index = hist_df["total_audi"].idxmax()
    top_movie = hist_df.loc[max_index, "movieNm"]
    max_audience = hist_df.loc[max_index, "total_audi"]

    # 히스토그램의 구간과 각 구간의 영화 수 계산
    counts, edges = np.histogram(audience, bins=20)

    # 영화가 가장 많이 몰린 구간
    max_bin = int(np.argmax(counts))
    lower = edges[max_bin]
    upper = edges[max_bin + 1]
    most_common_count = int(counts[max_bin])

    # 구간별 막대그래프 생성
    midpoints = (edges[:-1] + edges[1:]) / 2
    bin_labels = [
        f"{edges[i]:,.0f}~{edges[i + 1]:,.0f}명"
        for i in range(len(counts))
    ]

    fig3 = go.Figure(
        data=[
            go.Bar(
                x=midpoints,
                y=counts,
                width=np.diff(edges) * 0.95,
                customdata=np.array(bin_labels).reshape(-1, 1),
                hovertemplate=(
                    "관객 수 구간: %{customdata[0]}<br>"
                    "영화 편수: %{y}편"
                    "<extra></extra>"
                ),
            )
        ]
    )

    fig3.update_layout(
        xaxis_title="총 관객 수 (명)",
        yaxis_title="영화 편수",
        bargap=0.05,
        margin=dict(t=20, b=20, l=10, r=10),
    )

    fig3.update_xaxes(
        tickformat=",",
        rangemode="tozero"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # 그래프 아래 자동 분석 문구
    st.subheader("이 그래프로 알 수 있는 것")

    st.info(
        f"전체 영화 중 {most_common_count}편이 "
        f"총 관객 수 {lower:,.0f}명 이상 "
        f"{upper:,.0f}명 미만 구간에 몰려 있습니다."
    )

    st.info(
        f"분석 대상 중 총 관객 수가 가장 많은 영화는 "
        f"「{top_movie}」이며, 총 관객 수는 "
        f"{max_audience:,.0f}명입니다."
    )
    # ---------------------------------
# 그래프 4. 개봉일 스크린 수와 총 관객의 관계
# ---------------------------------

st.divider()
st.header("4. 개봉일 스크린 수와 총 관객의 관계")
st.write(
    "개봉일에 확보한 스크린 수와 영화의 총 관객 수 사이에 "
    "어떤 관계가 있는지 살펴봅니다."
)

scatter_df = df.copy()

# 필요한 열을 숫자로 변환
scatter_df["first_scrn"] = pd.to_numeric(
    scatter_df["first_scrn"],
    errors="coerce"
)

scatter_df["total_audi"] = pd.to_numeric(
    scatter_df["total_audi"],
    errors="coerce"
)

# 필요한 데이터가 없는 행 제거
scatter_df = scatter_df.dropna(
    subset=["first_scrn", "total_audi", "movieNm", "genre"]
)

if scatter_df.empty:
    st.warning("산점도를 그릴 수 있는 데이터가 없습니다.")

else:
    fig4 = px.scatter(
        scatter_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "first_scrn": ":,.0f",
            "total_audi": ":,.0f",
            "genre": True
        },
        labels={
            "first_scrn": "개봉일 스크린 수",
            "total_audi": "총 관객 수 (명)",
            "genre": "장르"
        },
        opacity=0.75
    )

    fig4.update_traces(
        marker=dict(size=9),
        hovertemplate=(
            "영화명: %{hovertext}<br>"
            "장르: %{fullData.name}<br>"
            "개봉일 스크린 수: %{x:,.0f}개<br>"
            "총 관객 수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    fig4.update_layout(
        xaxis_title="개봉일 스크린 수 (개)",
        yaxis_title="총 관객 수 (명)",
        legend_title_text="장르",
        margin=dict(t=20, b=20, l=10, r=10)
    )

    fig4.update_xaxes(rangemode="tozero")
    fig4.update_yaxes(rangemode="tozero", tickformat=",")

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    st.subheader("이 그래프로 알 수 있는 것")

    st.text_area(
        "산점도를 보고 알게 된 점을 한 문장으로 적어 보세요.",
        placeholder=(
            "예: 개봉일 스크린 수가 많은 영화일수록 "
            "총 관객 수도 많은 경향이 나타난다."
        ),
        key="scatter_observation",
        label_visibility="collapsed"
    )
    # ---------------------------------
# 그래프 5. 장르별 총 관객 수 상자 그림
# ---------------------------------

st.divider()
st.header("5. 장르별 총 관객 수 분포 (박스플롯)")
st.write(
    "영화가 10편 이상인 장르만 골라 "
    "장르별 총 관객 수의 분포와 이상치를 비교합니다."
)

box_df = df.copy()

# 총 관객 수를 숫자로 변환
box_df["total_audi"] = pd.to_numeric(
    box_df["total_audi"],
    errors="coerce"
)

# 영화명, 장르, 총 관객 수가 있는 데이터만 사용
box_df = box_df.dropna(
    subset=["movieNm", "genre", "total_audi"]
)

# 영화가 10편 이상인 장르만 선택
genre_counts_box = box_df["genre"].value_counts()

valid_genres = genre_counts_box[
    genre_counts_box >= 10
].index

box_df = box_df[
    box_df["genre"].isin(valid_genres)
].copy()

if box_df.empty:
    st.warning(
        "영화가 10편 이상인 장르가 없어 "
        "박스플롯을 그릴 수 없습니다."
    )

else:
    fig5 = px.box(
        box_df,
        x="genre",
        y="total_audi",
        color="genre",
        points="outliers",
        hover_name="movieNm",
        hover_data={
            "genre": True,
            "total_audi": ":,.0f"
        },
        labels={
            "genre": "장르",
            "total_audi": "총 관객 수 (명)"
        }
    )

    fig5.update_traces(
        boxmean=False,
        hovertemplate=(
            "영화명: %{hovertext}<br>"
            "장르: %{x}<br>"
            "총 관객 수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    fig5.update_layout(
        showlegend=False,
        xaxis_title="장르",
        yaxis_title="총 관객 수 (명)",
        margin=dict(t=20, b=20, l=10, r=10)
    )

    fig5.update_yaxes(
        rangemode="tozero",
        tickformat=","
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    st.subheader("이 그래프로 알 수 있는 것")

    st.text_area(
        "박스플롯을 보고 알게 된 점을 한 문장으로 적어 보세요.",
        placeholder=(
            "예: ○○ 장르는 총 관객 수의 분포가 넓고, "
            "다른 영화보다 관객 수가 많은 이상치가 나타난다."
        ),
        key="boxplot_observation",
        label_visibility="collapsed"
    )
    # ---------------------------------
# 그래프 6. 첫 주 관객 수를 반영한 버블 그래프
# ---------------------------------

st.divider()
st.header("6. 개봉일 스크린 수와 총 관객의 관계 (버블 그래프)")

st.write(
    "가로축은 개봉일 스크린 수, 세로축은 총 관객 수이며, "
    "버블 크기는 개봉 첫 주 관객 수를 나타냅니다."
)

bubble_df = df.copy()

# 숫자 데이터 변환
numeric_columns = [
    "first_scrn",
    "total_audi",
    "first_week_audi"
]

for column in numeric_columns:
    bubble_df[column] = pd.to_numeric(
        bubble_df[column],
        errors="coerce"
    )

# 필요한 데이터가 있는 행만 사용
bubble_df = bubble_df.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
)

# 음수 관객 수 및 스크린 수 제외
bubble_df = bubble_df[
    (bubble_df["first_scrn"] >= 0)
    & (bubble_df["total_audi"] >= 0)
    & (bubble_df["first_week_audi"] >= 0)
].copy()

if bubble_df.empty:
    st.warning(
        "버블 그래프를 그릴 수 있는 데이터가 없습니다."
    )

else:
    fig6 = px.scatter(
        bubble_df,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "first_scrn": ":,.0f",
            "total_audi": ":,.0f",
            "first_week_audi": ":,.0f",
            "genre": True
        },
        size_max=55,
        labels={
            "first_scrn": "개봉일 스크린 수 (개)",
            "total_audi": "총 관객 수 (명)",
            "first_week_audi": "개봉 첫 주 관객 수",
            "genre": "장르"
        },
        opacity=0.7
    )

    fig6.update_traces(
        marker=dict(
            sizemode="area",
            line=dict(width=0.5, color="white")
        ),
        hovertemplate=(
            "영화명: %{hovertext}<br>"
            "장르: %{fullData.name}<br>"
            "개봉일 스크린 수: %{x:,.0f}개<br>"
            "총 관객 수: %{y:,.0f}명<br>"
            "개봉 첫 주 관객 수: %{marker.size:,.0f}명"
            "<extra></extra>"
        )
    )

    fig6.update_layout(
        xaxis_title="개봉일 스크린 수 (개)",
        yaxis_title="총 관객 수 (명)",
        legend_title_text="장르",
        margin=dict(t=20, b=20, l=10, r=10)
    )

    fig6.update_xaxes(
        rangemode="tozero",
        tickformat=","
    )

    fig6.update_yaxes(
        rangemode="tozero",
        tickformat=","
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

    st.subheader("이 그래프로 알 수 있는 것")

    st.text_area(
        "버블 그래프를 보고 알게 된 점을 한 문장으로 적어 보세요.",
        placeholder=(
            "예: 개봉 첫 주 관객 수가 많은 영화는 "
            "총 관객 수도 많은 경향이 나타난다."
        ),
        key="bubble_observation",
        label_visibility="collapsed"
    )
    # ---------------------------------
# 그래프 7. 제작 국가에서 장르로 내려가는 선버스트 그래프
# ---------------------------------

st.divider()
st.header("7. 제작 국가별 장르 분포 (선버스트)")
st.write(
    "제작 국가에서 장르로 이어지는 구조를 보여 줍니다. "
    "각 영역의 크기는 해당하는 영화 편수를 나타냅니다."
)

sunburst_df = df.copy()

# 국가와 장르 데이터 정리
sunburst_df["nation"] = (
    sunburst_df["nation"]
    .fillna("미분류")
    .astype(str)
    .str.strip()
    .replace("", "미분류")
)

sunburst_df["genre"] = (
    sunburst_df["genre"]
    .fillna("미분류")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
    .replace("", "미분류")
)

# 영화별 한 행을 사용하여 영화 편수 계산
sunburst_counts = (
    sunburst_df
    .groupby(["nation", "genre"], as_index=False)
    .size()
    .rename(columns={"size": "영화 편수"})
)

if sunburst_counts.empty:
    st.warning("선버스트 그래프를 그릴 데이터가 없습니다.")

else:
    fig7 = px.sunburst(
        sunburst_counts,
        path=["nation", "genre"],
        values="영화 편수",
        color="nation",
        custom_data=["영화 편수"],
    )

    fig7.update_traces(
        hovertemplate=(
            "항목: %{label}<br>"
            "영화 편수: %{value}편"
            "<extra></extra>"
        ),
        insidetextorientation="auto",
    )

    fig7.update_layout(
        margin=dict(t=20, b=20, l=10, r=10),
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )

    st.subheader("이 그래프로 알 수 있는 것")

    st.text_area(
        "선버스트 그래프를 보고 알게 된 점을 한 문장으로 적어 보세요.",
        placeholder=(
            "예: 특정 제작 국가에서는 ○○ 장르의 영화가 "
            "상대적으로 많이 나타난다."
        ),
        key="sunburst_observation",
        label_visibility="collapsed",
    )
   # 8번째 그래프: 개봉 시기와 누적 관객 수의 관계
st.header("8. 나만의 질문 — 만들어서 분석하기")

question = "영화의 개봉 시기와 누적 관객 수 사이에는 어떤 관계가 있을까?"
st.subheader(question)

# 개봉일 데이터 정리
df["openDt"] = pd.to_datetime(
    df["openDt"], format="%Y%m%d", errors="coerce"
)

df["total_audi"] = pd.to_numeric(
    df["total_audi"], errors="coerce"
)

# 개봉 월 추출
df["개봉 월"] = df["openDt"].dt.month

# 그래프에 사용할 데이터 정리
season_df = df.dropna(
    subset=["movieNm", "개봉 월", "total_audi"]
).copy()

# 산점도 생성
fig8 = px.scatter(
    season_df,
    x="개봉 월",
    y="total_audi",
    hover_name="movieNm",
    labels={
        "개봉 월": "개봉 월",
        "total_audi": "누적 관객 수"
    },
    title=question
)

fig8.update_layout(
    xaxis=dict(
        tickmode="linear",
        dtick=1,
        title="개봉 월"
    ),
    yaxis=dict(
        title="누적 관객 수",
        tickformat=","
    )
)

st.plotly_chart(fig8, use_container_width=True)

st.markdown("### 이 그래프로 알 수 있는 것")
st.write(
    "영화가 개봉한 월에 따라 누적 관객 수가 어떻게 분포하는지 "
    "비교할 수 있다. 특정 월에 관객 수가 많은 영화가 집중되는지 "
    "확인하고, 개봉 시기와 누적 관객 수 사이의 관계를 분석할 수 있다."
)
