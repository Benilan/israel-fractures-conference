"""Recomputable election and census statistics for the Israel Fractures conference.

Inputs must be obtained lawfully and placed under data/raw. Nothing here
hardcodes slide numbers in place of an analysis. Geographic vote aggregates
are locality-level associations, not individual voter classifications.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ELECTIONS = {
    "K21": "Knesset 21 - 2019 - 1.csv",
    "K22": "Knesset 22 - 2019 - 2.csv",
    "K23": "Knesset 23 - 2020.csv",
    "K24": "Knesset 24 - 2021.csv",
    "K25": "Knesset 25 - 2022.csv",
}
CBS_FILE = "selected-data-by-localities-and-statistical-areas-2022-census.xlsx"
FEATURES = ["hh_MidatDatiyut_Name", "ChldBorn_avg", "age_median",
            "AcadmCert_pcnt", "africa_pcnt", "europe_pcnt"]
FAMILIES_2022 = {
    "Centre-gauche laïque": ["אמת", "מרצ", "פה", "כן"],
    "Droite populaire": ["מחל"],
    "Sionisme religieux": ["ט", "ב"],
    "Haredi": ["ג", "שס"],
    "Arabes": ["עם", "ום", "ד"],
    "Droite nationale laïque": ["ל"],
}
OTHER = "Autres – listes marginales"
PROFILE_ORDER = ["Ultra-orthodoxe", "National-religieux",
                 "Urbain éduqué", "Populaire", "Métropolitain aisé"]
RELIGIONS = {"יהודים": "Juive", "מוסלמים": "Musulmane",
             "נוצרים": "Chrétienne", "דרוזים": "Druze",
             "דת אחרת": "Autre religion"}

def load_elections(raw):
    result = {}
    for election, filename in ELECTIONS.items():
        try:
            data = pd.read_csv(raw / filename, encoding="utf-8-sig")
        except UnicodeDecodeError:
            data = pd.read_csv(raw / filename, encoding="cp1255")
        data = data.rename(columns={"סמל ישוב": "LocalityCode",
                                    "סמל יישוב": "LocalityCode",
                                    "בזב": "RegisteredVoters",
                                    "מצביעים": "Voters",
                                    "כשרים": "ValidVotes",
                                    "שם ישוב": "LocalityName",
                                    "שם יישוב": "LocalityName"})
        for col in ("LocalityCode", "RegisteredVoters", "Voters", "ValidVotes"):
            data[col] = pd.to_numeric(data[col], errors="coerce")
        result[election] = data
    return result

def load_cbs(raw):
    data = pd.read_excel(raw / CBS_FILE)
    data = data[data.StatArea.isna()].dropna(subset=["LocalityCode"])
    data = data.drop_duplicates("LocalityCode").copy()
    data["LocalityCode"] = pd.to_numeric(data.LocalityCode, errors="coerce")
    return data

def round_rows_to_100(table):
    values = table.to_numpy(dtype=float)
    if not np.allclose(values.sum(axis=1), 100, atol=.05):
        raise AssertionError("Input percentages do not total 100")
    rounded = np.floor(values).astype(int)
    residual = values - rounded
    for i in range(len(rounded)):
        remaining = 100 - rounded[i].sum()
        order = np.argsort(-residual[i], kind="stable")
        rounded[i, order[:remaining]] += 1
    result = pd.DataFrame(rounded, index=table.index, columns=table.columns)
    assert (result.sum(axis=1) == 100).all()
    return result

def label_profiles(complete):
    traits = complete.groupby("cluster").agg(
        religion=("hh_MidatDatiyut_Name", "mean"),
        age=("age_median", "mean"),
        education=("AcadmCert_pcnt", "mean"),
    )
    left = set(traits.index)
    labels = {}
    h = max(left, key=lambda x: (traits.loc[x, "religion"], -traits.loc[x, "age"]))
    labels[h] = "Ultra-orthodoxe"; left.remove(h)
    n = max(left, key=lambda x: traits.loc[x, "religion"])
    labels[n] = "National-religieux"; left.remove(n)
    r = max(left, key=lambda x: traits.loc[x, "education"])
    labels[r] = "Métropolitain aisé"; left.remove(r)
    u = max(left, key=lambda x: traits.loc[x, "education"])
    labels[u] = "Urbain éduqué"; left.remove(u)
    labels[left.pop()] = "Populaire"
    return labels

def compute_2022(elections, cbs):
    votes = elections["K25"].copy()
    base = votes[["LocalityCode", "ValidVotes"]].merge(
        cbs[["LocalityCode", "pop_approx", *FEATURES]],
        on="LocalityCode", how="left", validate="one_to_one",
    )
    complete = base.dropna(subset=FEATURES).copy()
    standardized = StandardScaler().fit_transform(complete[FEATURES])
    weights = complete.pop_approx.fillna(1).clip(lower=1)
    model = KMeans(n_clusters=5, random_state=42, n_init=20)
    complete["cluster"] = model.fit_predict(standardized, sample_weight=weights)
    complete["SocialProfile"] = complete.cluster.map(label_profiles(complete))
    for family, codes in FAMILIES_2022.items():
        votes[family] = votes[codes].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    cols = list(FAMILIES_2022)
    votes[OTHER] = votes.ValidVotes - votes[cols].sum(axis=1)
    assert votes[OTHER].min() >= 0
    merged = votes[["LocalityCode", "ValidVotes", *cols, OTHER]].merge(
        complete[["LocalityCode", "SocialProfile"]], on="LocalityCode",
        validate="one_to_one",
    )
    grouped = merged.groupby("SocialProfile")[["ValidVotes", *cols, OTHER]].sum().reindex(PROFILE_ORDER)
    heatmap = grouped[[*cols, OTHER]].div(grouped.ValidVotes, axis=0).mul(100)
    assert np.allclose(heatmap.sum(axis=1), 100, atol=1e-6)
    population = complete.groupby("SocialProfile").agg(
        Localities=("LocalityCode", "size"),
        Population=("pop_approx", "sum"),
    ).reindex(PROFILE_ORDER)
    population["LocalitySharePct"] = population.Localities / population.Localities.sum() * 100
    population["PopulationSharePct"] = population.Population / population.Population.sum() * 100
    return complete, heatmap, population

def compute_turnout(elections, cbs):
    group_map = cbs[["LocalityCode", "ReligionHeb"]]
    rows = []
    for election, data in elections.items():
        joined = data[["LocalityCode", "RegisteredVoters", "Voters"]].merge(
            group_map, on="LocalityCode", validate="many_to_one"
        )
        grouped = joined.groupby("ReligionHeb")[["RegisteredVoters", "Voters"]].sum()
        for religion, row in grouped.iterrows():
            rows.append({"Election": election, "DominantReligion": RELIGIONS.get(religion, religion),
                         "RegisteredVoters": row.RegisteredVoters, "Voters": row.Voters,
                         "TurnoutPct": 100 * row.Voters / row.RegisteredVoters})
    return pd.DataFrame(rows)

def run(root):
    raw = root / "data/raw"
    required = [*ELECTIONS.values(), CBS_FILE]
    missing = [file for file in required if not (raw / file).is_file()]
    if missing:
        raise FileNotFoundError("Missing official source inputs: " + ", ".join(missing))
    out = root / "outputs/tables"
    out.mkdir(parents=True, exist_ok=True)
    elections = load_elections(raw)
    cbs = load_cbs(raw)
    turnout = compute_turnout(elections, cbs)
    complete, heatmap, population = compute_2022(elections, cbs)
    turnout.to_csv(out / "slide_07_turnout_by_dominant_religion.csv", index=False)
    heatmap.to_csv(out / "slide_23_heatmap_exact.csv")
    round_rows_to_100(heatmap).to_csv(out / "slide_23_heatmap_rounded.csv")
    population.to_csv(out / "slide_20_21_social_profiles.csv")
    complete[["LocalityCode", "cluster", "SocialProfile"]].to_csv(
        out / "slide_20_21_locality_assignments.csv", index=False
    )
    print(json.dumps({"status": "computed", "localities": len(complete),
                      "files": [p.name for p in out.glob("*.csv")]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
