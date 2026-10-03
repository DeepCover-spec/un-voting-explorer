import pandas as pd

RAW = "data/raw/2026_02_06_ga_voting.csv"
OUT_VOTES = "data/processed/votes.csv"
OUT_RES = "data/processed/resolutions.csv"
OUT_COUNTRIES = "data/processed/countries.csv"

# Y = yes, N = no, A = abstain. X (non-voting) stays missing on purpose:
# not voting is not the same as taking a neutral position.
VOTE_MAP = {"Y": 1, "N": -1, "A": 0}

# Successor links, used only when tracking a country across time.
# A modelling choice: successor states do not always inherit a
# predecessor's voting position.
SUCCESSOR = {
    "SUN": "RUS",   # Soviet Union -> Russian Federation
    "GER": "DEU",   # West Germany -> unified Germany
    "CSK": "CZE",   # Czechoslovakia -> Czech Republic
    "YUG": "SRB",   # Yugoslavia -> Serbia
    "SCG": "SRB",   # Serbia and Montenegro -> Serbia
}


def prepare():
    cols = ["undl_id", "ms_code", "ms_name", "ms_vote", "date",
            "session", "resolution", "title", "subjects"]
    df = pd.read_csv(RAW, usecols=cols, parse_dates=["date"],
                     dtype={"session": "string"})
    print("Raw rows:", len(df))

    unexpected = set(df["ms_vote"].unique()) - {"Y", "N", "A", "X"}
    assert not unexpected, f"Unexpected vote codes: {unexpected}"

    # votes: one row per country per resolution
    votes = df[["undl_id", "ms_code", "ms_vote"]].copy()
    votes["vote"] = votes["ms_vote"].map(VOTE_MAP)
    votes = votes.drop(columns="ms_vote")

    # resolutions: one row per resolution
    resolutions = (df.drop_duplicates("undl_id")
                     [["undl_id", "date", "session", "resolution",
                       "title", "subjects"]]
                     .sort_values("date"))
    resolutions["year"] = resolutions["date"].dt.year

    # countries: one row per code, latest name plus first and last vote dates
    countries = (df.sort_values("date")
                   .groupby("ms_code")
                   .agg(name=("ms_name", "last"),
                        first_vote=("date", "min"),
                        last_vote=("date", "max"))
                   .reset_index())
    countries["lineage_code"] = (countries["ms_code"].map(SUCCESSOR)
                                 .fillna(countries["ms_code"]))

    votes.to_csv(OUT_VOTES, index=False)
    resolutions.to_csv(OUT_RES, index=False)
    countries.to_csv(OUT_COUNTRIES, index=False)

    print(f"votes: {len(votes)} rows ({votes['vote'].isna().mean():.1%} missing)")
    print(f"resolutions: {len(resolutions)}")
    print(f"countries: {len(countries)}")


if __name__ == "__main__":
    prepare()