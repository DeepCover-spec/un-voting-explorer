import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).parent / "src"))
from votes import load_data, pair_agreement, closest_partners

st.set_page_config(page_title="UN Voting Explorer", layout="wide")


@st.cache_data
def get_data():
    return load_data()


M, res, countries = get_data()
names = countries.set_index("ms_code")["name"].str.title()
codes = sorted(M.index, key=lambda c: names.get(c, c))


def label(c):
    return f"{names.get(c, c)} ({c})"


PERIODS = [(y, y + 4) for y in range(1950, 2025, 5)]


@st.cache_data
def agreement_over_time(a, b, soft):
    rows = []
    for s, e in PERIODS:
        score, n = pair_agreement(M, res, a, b, f"{s}-01-01", f"{e}-12-31", soft=soft)
        # The dataset uses one code for the Chinese seat, which changed
        # governments in 1971, so earlier periods are hidden.
        if "CHN" in (a, b) and s < 1972:
            score = float("nan")
        rows.append({"period": f"{s}-{str(e)[2:]}", "agreement": score, "shared_votes": n})
    return pd.DataFrame(rows)


@st.cache_data
def partners(country, start, end, soft):
    df = closest_partners(M, res, country, start, end, soft=soft, top=10)
    df.insert(0, "country", [names.get(c, c) for c in df.index])
    return df


st.title("UN General Assembly Voting Explorer")
st.caption("How similarly do two countries vote on General Assembly resolutions "
           "that were adopted by recorded vote?")

with st.sidebar:
    st.header("Choose")
    a = st.selectbox("Country A", codes, index=codes.index("IND"), format_func=label)
    b = st.selectbox("Country B", codes, index=codes.index("CHN"), format_func=label)
    y0, y1 = st.slider("Years", 1946, 2025, (2000, 2024))
    soft = st.checkbox("Soft scoring (yes against abstain counts as half agreement)")

if a == b:
    st.warning("Pick two different countries.")
    st.stop()

start, end = f"{y0}-01-01", f"{y1}-12-31"
score, n = pair_agreement(M, res, a, b, start, end, soft=soft)

left, right = st.columns(2)
with left:
    st.subheader(f"{label(a)} and {label(b)}, {y0}-{y1}")
    if pd.isna(score):
        st.info(f"Not enough shared votes in this period ({n}; at least 20 are needed).")
    else:
        st.metric("Agreement", f"{score:.0%}", help=f"Based on {n:,} shared votes")
        st.caption(f"{n:,} resolutions on which both countries voted.")

with right:
    st.subheader("Agreement by five-year period")
    df = agreement_over_time(a, b, soft)
    fig = px.line(df, x="period", y="agreement", markers=True,
                  hover_data=["shared_votes"], range_y=[0, 1])
    fig.update_layout(yaxis_tickformat=".0%", xaxis_title="", yaxis_title="Agreement")
    fig.update_xaxes(type="category")   # treat labels like "2000-04" as text, not dates
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Gaps mean fewer than 20 shared votes in that period. "
               "China is hidden before 1972 because the seat changed governments in 1971.")

st.subheader(f"Closest voting partners, {y0}-{y1}")
c1, c2 = st.columns(2)
with c1:
    st.write(f"Most like {label(a)}")
    st.dataframe(partners(a, start, end, soft), use_container_width=True)
with c2:
    st.write(f"Most like {label(b)}")
    st.dataframe(partners(b, start, end, soft), use_container_width=True)

st.caption("Data: United Nations Dag Hammarskjöld Library, General Assembly Voting Data, "
           "version 5 (February 2026). Non-commercial use with attribution. "
           "Agreement reflects similar votes on recorded-vote resolutions, not alliances.")