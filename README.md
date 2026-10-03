# UN General Assembly Voting Explorer

An exploration of how countries vote at the UN General Assembly: a data pipeline over roughly 947,000 recorded votes, a measure of voting similarity between countries, and clustering of countries into voting blocs. Work in progress.

## Status

- [x] Data download, validation, and preparation (`src/prepare.py`)
- [x] Exploratory analysis of the vote data
- [x] Country-to-country agreement measure
- [x] First clustering of countries (2000-2024)
- [ ] Compare scoring choices for abstentions
- [ ] Track how blocs shift over time
- [ ] Interactive app: compare any two countries

## Data

UN Digital Library recorded votes on General Assembly resolutions (version 5, February 2026): 947,434 country votes on 5,694 resolutions adopted by recorded vote, from January 1946 to December 2025, covering 203 country codes.

* Only resolutions adopted by a recorded vote are included. Most resolutions pass without a vote, and votes on paragraphs or on drafts that failed are not in this dataset.
* Vote codes: Y (yes), N (no), A (abstain), X (non-voting).
* The raw file is 364 MB and is not stored in this repository.

Source: United Nations Dag Hammarskjöld Library, *General Assembly Voting Data*, United Nations, version 5 (February 2026), downloaded from the [UN Digital Library](https://digitallibrary.un.org/record/4060887). Non-commercial use with attribution.

## Method

1. **Prepare** (`src/prepare.py`): split the raw file into three tables (votes, resolutions, countries). Votes are coded yes = 1, abstain = 0, no = -1; non-voting is treated as missing, not as a neutral position.
2. **Agreement**: for each pair of countries, the share of resolutions both voted on where they cast the same vote. Pairs with fewer than 20 shared votes are ignored.
3. **Cluster**: convert agreement to distance, place countries on a two-dimensional map with multidimensional scaling, and group them with Ward hierarchical clustering. Only countries that voted on at least 70% of the resolutions in a window are included.

Country codes (`ms_code`) are treated as continuous across renames and changes of government. Predecessor and successor states (for example the USSR and Russia) are linked in a separate lookup column and are not merged.

## Findings so far

**2025 has an unusual number of recorded votes.** Session 80 contains 159 recorded-vote resolutions, against 113 in session 79. In 2025 as a whole, 124 of 192 recorded-vote resolutions had three or fewer "no" votes, up from 33 of 95 in 2024. The United States cast a "no" vote on 114 of those 124 (92%), Argentina on 45, and Israel on 44. The increase is spread across many subjects and is not tied to Middle East resolutions, whose yearly count stayed between 9 and 16 from 2015 to 2025. I report this as an observed pattern and did not investigate its causes.

**First clusters (2000-2024, 176 countries, six groups).** The groups include a Western and European bloc (50 countries), a Latin American-centred group (28), a large group of mostly African, Arab, and Asian states (86), the United States with Israel, and a small group of Pacific states that vote with the US (Micronesia, Marshall Islands, Palau). A seven-country group contains China, India, Pakistan, Iran, Russia, Syria, and North Korea. [Add the result of the abstention comparison here.]

<!-- After saving the map, add: ![Countries by voting similarity](reports/voting_map_2000_2024.png) -->

## Limitations

* Recorded votes are not a random sample of all resolutions, because most pass by consensus without a vote.
* The agreement measure treats yes against abstain as full disagreement, which may exaggerate similarity between frequent abstainers. [Update after comparing with the soft version.]
* Clusters depend on the number of groups chosen and on the time window, and voting similarity may be a continuum, not clean blocs.
* Country-code continuity across renames is an assumption; Yemen's code spans North Yemen and the unified state after 1990.

## How to run

```bash
git clone https://github.com/DeepCover-spec/un-voting-explorer.git
cd un-voting-explorer
python -m venv .venv
.venv\Scripts\activate        # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Download `2026_02_06_ga_voting.csv` from the [UN Digital Library](https://digitallibrary.un.org/record/4060887) into `data/raw/`, then:

```bash
python src/prepare.py
```

Run the notebooks in `notebooks/` in order.