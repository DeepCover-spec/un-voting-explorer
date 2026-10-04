# UN General Assembly Voting Explorer

An exploration of how countries vote at the UN General Assembly: a data pipeline over about 947,000 recorded votes, a measure of voting similarity between countries, and a first look at voting blocs. Work in progress.

## Status

- [x] Data download, validation, and preparation (`src/prepare.py`)
- [x] Exploratory analysis of the vote data
- [x] Country-to-country agreement measure, with two ways of scoring abstentions
- [x] First clustering of countries (2000-2024)
- [ ] Choose the number of clusters with evidence
- [ ] Track how blocs shift over time
- [ ] Interactive app: compare any two countries

## Data

UN Digital Library recorded votes on General Assembly resolutions (version 5, February 2026): 947,434 country votes on 5,694 resolutions adopted by recorded vote, from January 1946 to December 2025, covering 202 country codes.

* Only resolutions adopted by a recorded vote are included. Most resolutions pass without a vote, and votes on paragraphs or on drafts that failed are not in this dataset.
* Vote codes: Y (yes), N (no), A (abstain), X (non-voting).
* The raw file is 364 MB and is not stored in this repository.

Source: United Nations Dag Hammarskjöld Library, *General Assembly Voting Data*, United Nations, version 5 (February 2026), downloaded from the [UN Digital Library](https://digitallibrary.un.org/record/4060887). Non-commercial use with attribution.

## Method

1. **Prepare** (`src/prepare.py`): split the raw file into three tables (votes, resolutions, countries). Votes are coded yes = 1, abstain = 0, no = -1; non-voting is treated as missing, not as a neutral position.
2. **Agreement**: for each pair of countries, a score over the resolutions both voted on. Pairs with fewer than 20 shared votes are ignored. Two versions:
   * **Strict:** the share of shared votes where both cast the same vote (yes against abstain counts as disagreement).
   * **Soft:** yes against abstain counts as half agreement; yes against no counts as full disagreement.
3. **Cluster**: convert agreement to distance, place countries on a two-dimensional map with multidimensional scaling, and group them with Ward hierarchical clustering. Only countries that voted on at least 70% of the resolutions in the window are included (176 countries for 2000-2024).

Country codes (`ms_code`) are treated as continuous across renames and changes of government. Predecessor and successor states (for example the USSR and Russia) are linked in a separate lookup column and are not merged.

## Findings so far

### 2025 has an unusual number of recorded votes
Session 80 contains 159 recorded-vote resolutions, against 113 in session 79. In 2025 as a whole, 124 of 192 recorded-vote resolutions had three or fewer "no" votes, up from 33 of 95 in 2024. The United States cast a "no" vote on 114 of those 124 (92%), Argentina on 45, and Israel on 44. The increase is spread across many subjects and is not tied to Middle East resolutions, whose yearly count stayed between 9 and 16 from 2015 to 2025. I report this as an observed pattern and did not investigate its causes.

### Pairwise agreement is more reliable than cluster labels
For 2000-2024, agreement between selected pairs (about 2,000 shared votes each; rank is among 175 other countries, 1 = closest):

| Pair | Agreement (strict / soft) | Rank (strict / soft) |
| :--- | :---: | :---: |
| India - Pakistan | 0.86 / 0.92 | 1 / 1 |
| India - Sri Lanka | 0.82 / 0.89 | 4 / 4 |
| Pakistan - China | 0.87 / 0.93 | 2 / 5 |
| India - China | 0.79 / 0.88 | 39 / 20 |
| China - Russia | 0.76 / 0.86 | 106 / 100 |
| India - Russia | 0.68 / 0.81 | 116 / 115 |
| India - France | 0.43 / 0.61 | 167 / 167 |
| India - USA | 0.16 / 0.28 | 175 / 175 |

### Clusters (2000-2024, 176 countries, six groups)
The groups include a Western and European bloc (50 countries), a Latin American-centred group (28), a large group of mostly African, Arab, and Asian states (86), the United States with Israel, and a small group of Pacific states that vote with the US (Micronesia, Marshall Islands, Palau). Under strict scoring a seven-country group also appeared (China, India, Pakistan, Iran, Russia, Syria, North Korea), but direct comparison shows it is not a tight bloc: China ranks 39th among India's partners and Russia 116th. Under soft scoring, Russia separates from China and India. Cluster boundaries therefore depend on how abstentions are scored.

![Countries by voting similarity, strict and soft scoring](reports/voting_map_strict_vs_soft.png)

*Voting map, 2000-2024. Axes have no meaning; only distances between countries do. The two panels cannot be compared by position.*

On the map, a compact Western and European group sits apart from one dense mass of other countries, with the US and Israel far out on their own. Most of the structure inside the dense mass looks like a continuum, not separate blocs.

## Limitations

* Recorded votes are not a random sample of all resolutions, because most pass by consensus without a vote.
* Agreement reflects similar votes on recorded-vote resolutions, not alliances or relations.
* Clusters depend on the number of groups chosen, the time window, and how abstentions are scored. Most countries outside the Western group and the US-Israel pair form a continuous cloud, so cluster boundaries within it are somewhat arbitrary.
* Country-code continuity across renames is an assumption; Yemen's code spans North Yemen and the unified state after 1990.
* No significance tests have been run, and 2025 is unusual enough that windows including it should be read with care.

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