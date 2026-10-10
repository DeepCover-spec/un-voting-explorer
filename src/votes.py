from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

MIN_COMMON = 20   # ignore country pairs with fewer shared votes than this

# Founding Western members, present for the whole period.
# The USA is left out on purpose so the 2025 pattern cannot distort the anchor.
ANCHORS = ["GBR", "FRA", "CAN", "AUS", "NLD", "BEL", "NOR", "DNK"]


def load_data():
    """Return the country-by-resolution vote matrix, the resolutions, and the countries."""
    votes = pd.read_csv(PROCESSED / "votes.csv")
    res = pd.read_csv(PROCESSED / "resolutions.csv", parse_dates=["date"])
    countries = pd.read_csv(PROCESSED / "countries.csv")
    M = votes.pivot(index="ms_code", columns="undl_id", values="vote")
    return M, res, countries


def window(M, res, start, end):
    """Votes on resolutions between two dates, without countries that never voted."""
    ids = res.loc[(res["date"] >= start) & (res["date"] <= end), "undl_id"]
    sub = M[M.columns.intersection(ids)]
    return sub.dropna(how="all")


def agreement_matrix(M, soft=False, min_common=MIN_COMMON):
    """Agreement between every pair of countries.

    strict: share of shared votes where both cast the same vote.
    soft:   yes against abstain counts as half agreement.
    Returns the agreement matrix and the matrix of shared-vote counts.
    """
    A = M.to_numpy()
    valid = (~np.isnan(A)).astype(float)
    common = valid @ valid.T
    onehot = {v: (A == v).astype(float) for v in (1.0, 0.0, -1.0)}

    if soft:
        dist = np.zeros_like(common)
        for u in onehot:
            for v in onehot:
                dist += abs(u - v) * (onehot[u] @ onehot[v].T)
        with np.errstate(invalid="ignore", divide="ignore"):
            S = 1 - dist / (2 * common)
    else:
        agree = np.zeros_like(common)
        for v in onehot:
            agree += onehot[v] @ onehot[v].T
        with np.errstate(invalid="ignore", divide="ignore"):
            S = agree / common

    S[common < min_common] = np.nan
    S = pd.DataFrame(S, index=M.index, columns=M.index)
    C = pd.DataFrame(common, index=M.index, columns=M.index)
    return S, C


def pair_agreement(M, res, a, b, start, end, soft=False):
    """Agreement between two countries in one period: (score, shared votes)."""
    sub = window(M, res, start, end)
    if a not in sub.index or b not in sub.index:
        return np.nan, 0
    x, y = sub.loc[a], sub.loc[b]
    both = x.notna() & y.notna()
    n = int(both.sum())
    if n < MIN_COMMON:
        return np.nan, n
    d = (x[both] - y[both]).abs()
    score = 1 - d.mean() / 2 if soft else float((d == 0).mean())
    return float(score), n


def closest_partners(M, res, country, start, end, soft=False, top=10):
    """The countries that vote most like `country` in a period."""
    sub = window(M, res, start, end)
    S, C = agreement_matrix(sub, soft=soft)
    if country not in S.index:
        return pd.DataFrame(columns=["agreement", "shared_votes"])
    s = S.loc[country].drop(country).dropna().sort_values(ascending=False).head(top)
    return pd.DataFrame({"agreement": s.round(3),
                         "shared_votes": C.loc[country, s.index].astype(int)})


def anchor_agreement(M, res, start, end, soft=False):
    """Each country's mean agreement with the anchor group in a period."""
    sub = window(M, res, start, end)
    S, _ = agreement_matrix(sub, soft=soft)
    cols = [a for a in ANCHORS if a in S.columns]
    s = S[cols].copy()
    for a in cols:
        s.loc[a, a] = np.nan          # ignore each anchor's agreement with itself
    return s.mean(axis=1)