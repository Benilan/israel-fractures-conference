"""Historical Ward electoral families and descriptive population-weighted eta squared.

Independent recalculation from election/CBS locality source files. Ward
profiles use parties exceeding 1% in at least one election, shared
localities, row-centred vote-share profiles and seven groups. Two explicit
interpretive corrections: Shas -> Haredi; Zehut in K21 -> secular right.

IMPORTANT: weighted eta squared is descriptive, not a causal regression or
a p-value. Geography is the observation unit.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from .pipeline_v16 import read_elections,read_cbs
from .heatmap_v15 import FAMILIES

ORDER=["K21","K22","K23","K24","K25"]
LABELS=["Secular center-left","Popular right","Religious Zionism",
        "Haredim","Arab parties","Secular national right","Other lists"]
VARS={"AcadmCert_pcnt":"Higher education","hh_MidatDatiyut_Name":"Religiosity",
      "Computer_avg":"Computer equipment","age_median":"Median age",
      "employeesAnnual_medWage":"Median employee wages","ChldBorn_avg":"Average number of children"}
EXPECTED_ETA={"AcadmCert_pcnt":714,"hh_MidatDatiyut_Name":694,
              "Computer_avg":671,"age_median":661,
              "employeesAnnual_medWage":658,"ChldBorn_avg":624}
ADMIN={"LocalityCode","RegisteredVoters","Voters","ValidVotes","LocalityName",
       "LocalityNameHeb","CommitteeCode","InvalidVotes","source_file","election",
       "סמל ועדה","שם ועדה","פסולים"}
# 2022 party codes anchor the stable cluster naming.
ANCHORS={"מחל":"Popular right","פה":"Secular center-left",
         "ט":"Religious Zionism","ג":"Haredim",
         "עם":"Arab parties","ל":"Secular national right"}
def party_vote_columns(df):
    return [c for c in df if c not in ADMIN and not str(c).startswith("Unnamed")
            and pd.to_numeric(df[c],errors="coerce").fillna(0).sum()>0]

def calculate(raw:Path):
    elections=read_elections(raw)
    rows=[]; elections_norm={}
    for key in ORDER:
        df=elections[key].copy()
        df["LocalityCode"]=pd.to_numeric(df.LocalityCode,errors="coerce")
        df["ValidVotes"]=pd.to_numeric(df.ValidVotes,errors="coerce")
        df=df[df.LocalityCode.notna() & df.ValidVotes.gt(0)].copy()
        # Ignore special envelope entries when calculating common localities.
        name="LocalityName" if "LocalityName" in df else "LocalityNameHeb"
        elections_norm[key]=df
        cols=party_vote_columns(df)
        tmp=df[["LocalityCode","ValidVotes",*cols]].melt(
            id_vars=["LocalityCode","ValidVotes"],value_vars=cols,
            var_name="PartyLetter",value_name="Votes")
        tmp["Votes"]=pd.to_numeric(tmp.Votes,errors="coerce").fillna(0)
        tmp["Election"]=key
        rows.append(tmp)
    votes=pd.concat(rows,ignore_index=True)
    totals=pd.DataFrame([{"Election":key,"ValidVotes":float(elections[key].ValidVotes.sum())}
                          for key in ORDER]).set_index("Election")
    national=votes.groupby(["Election","PartyLetter"],as_index=False).Votes.sum()
    national=national.merge(totals,on="Election")
    national["Pct"]=100*national.Votes/national.ValidVotes
    selected=national.loc[national.Pct>=1,["Election","PartyLetter"]]
    common=set.intersection(*(
        set(frame.loc[
            ~frame["LocalityName"].astype("string").str.contains("מעטפות",na=False),
            "LocalityCode"].dropna()) if "LocalityName" in frame
        else set(frame.LocalityCode.dropna())
        for frame in elections_norm.values()
    ))
    local=votes[votes.LocalityCode.isin(common)].merge(selected,on=["Election","PartyLetter"],validate="many_to_one")
    local["Share"]=local.Votes/local.ValidVotes
    matrix=local.pivot(index=["Election","PartyLetter"],columns="LocalityCode",values="Share").sort_index()
    if matrix.isna().any().any():raise AssertionError("Incomplete historical locality matrix")
    centered=matrix.sub(matrix.mean(axis=1),axis=0)
    z=centered.div(np.linalg.norm(centered.to_numpy(float),axis=1),axis=0)
    ward=linkage(z,method="ward",metric="euclidean",optimal_ordering=True)
    ass=matrix.index.to_frame(index=False)
    ass["Cluster"]=fcluster(ward,t=7,criterion="maxclust")
    def anchor(code):
        q=ass[(ass.Election=="K25") & ass.PartyLetter.eq(code)]
        if len(q)!=1:raise ValueError(f"Anchor list not found: {code}")
        return int(q.Cluster.iloc[0])
    # Two clusters in the 2022 secular center-left are combined.
    anchors={key:anchor(k) for k,key in ANCHORS.items()}
    cluster_names={v:k for k,v in anchors.items()}
    if len(cluster_names)!=6:raise AssertionError("Unexpected Ward anchor collision")
    remaining=set(ass.Cluster)-set(cluster_names)
    if len(remaining)!=1:raise AssertionError("Expected one additional center-left cluster")
    cluster_names[remaining.pop()]="Secular center-left"
    ass["Family"]=ass.Cluster.map(cluster_names)
    mapping=national.merge(ass,on=["Election","PartyLetter"],how="left",validate="one_to_one")
    mapping["WardFamily"]=mapping.Family
    # The V14 ANOVA was run on seven Ward groups plus Other, BEFORE the
    # presentation merged two center-left clusters into a single family.
    # Keep the statistical partition distinct from the slide 11 family labels.
    mapping["WardGroupV14"]=mapping.Cluster.map(
        lambda x: f"Ward {int(x)}" if pd.notna(x) else "Other"
    )
    mapping["Family"]=mapping.Family.fillna("Other lists")
    mapping["Correction"]=""
    shas=mapping.PartyLetter.eq("שס")
    mapping.loc[shas,["Family","Correction"]]=["Haredim","Shas -> Haredim"]
    mapping.loc[shas,"WardGroupV14"]=f"Ward {anchors['Haredim']}"
    zehut=mapping.Election.eq("K21") & mapping.PartyLetter.eq("ז")
    if zehut.sum()!=1:raise AssertionError("K21 Zehut missing")
    mapping.loc[zehut,["Family","Correction"]]=["Secular national right","K21 Zehut -> secular right"]
    mapped=votes.merge(mapping[["Election","PartyLetter","Family","WardGroupV14"]],on=["Election","PartyLetter"],validate="many_to_one")
    aggregated=mapped.groupby(["Election","Family"],as_index=False).Votes.sum()
    share=aggregated.pivot(index="Election",columns="Family",values="Votes").fillna(0).reindex(ORDER)
    share=share.div(totals.ValidVotes,axis=0).mul(100).reindex(columns=LABELS,fill_value=0)
    if not np.allclose(share.sum(axis=1),100,atol=.01):
        raise AssertionError("National historical shares do not total 100%")
    # 2022 groups, on each locality: by family vote count
    city=mapped[mapped.Election=="K25"].groupby(
        ["LocalityCode","WardGroupV14"],as_index=False).Votes.sum()
    win=city.loc[city.groupby("LocalityCode").Votes.idxmax()][
        ["LocalityCode","WardGroupV14"]]
    win=win.rename(columns={"WardGroupV14":"DominantBlock"})
    cbs=read_cbs(raw)
    data=cbs.merge(win,on="LocalityCode",how="inner",validate="one_to_one")
    effects=[]
    for col,name in VARS.items():
        sub=data[["DominantBlock","pop_approx",col]].copy()
        sub[col]=pd.to_numeric(sub[col],errors="coerce")
        sub.pop_approx=pd.to_numeric(sub.pop_approx,errors="coerce")
        # Historical V14 selects eligible groups before filtering population
        # weights: preserve the original order of operations exactly.
        sub=sub.dropna(subset=["DominantBlock",col])
        eligible=sub.DominantBlock.value_counts()
        sub=sub[sub.DominantBlock.isin(eligible[eligible>=5].index)]
        sub=sub.dropna(subset=["pop_approx"])
        sub=sub[sub.pop_approx>0]
        w=sub.pop_approx.to_numpy(float);v=sub[col].to_numpy(float)
        mean=np.average(v,weights=w)
        total=float(np.sum(w*(v-mean)**2))
        between=sum(g.pop_approx.sum()*(np.average(g[col],weights=g.pop_approx)-mean)**2
                    for _,g in sub.groupby("DominantBlock"))
        eta=between/total
        effects.append({"Variable":col,"Label":name,"EtaSquared":eta,"EtaSquaredX1000":eta*1000,
                        "Localities":len(sub),"PowerPointReference":EXPECTED_ETA[col]})
    effect_table=pd.DataFrame(effects).sort_values("EtaSquared",ascending=False)
    # 2022 politics: whether the K21 and K25 dominant family is stable.
    winner=mapped[mapped.Election.isin(["K21","K25"])].groupby(
        ["Election","LocalityCode","Family"],as_index=False).Votes.sum()
    winner=winner.loc[winner.groupby(["Election","LocalityCode"]).Votes.idxmax()]
    stable=winner.pivot(index="LocalityCode",columns="Election",values="Family").dropna()
    stability=float(stable.K21.eq(stable.K25).mean())
    return mapping,share,effect_table,{"common_localities":len(common),
         "compared_localities":len(stable),"dominance_stability_pct":100*stability,
         "zehut_2019_pct":float(mapping.loc[zehut,"Pct"].iloc[0])}

def export(raw:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    mapping,share,eta,detail=calculate(raw)
    mapping.to_csv(out/"historical_ward_family_assignments.csv",index=False,encoding="utf-8-sig")
    share.to_csv(out/"slide_11_historical_families_recomputed.csv",encoding="utf-8-sig")
    eta.to_csv(out/"slide_19_weighted_eta_v14_recomputed.csv",index=False,encoding="utf-8-sig")
    changes=(share.loc["K25"]-share.loc["K21"]).to_dict()
    eta_comparison=[
        {"variable":str(row.Variable),
         "computed_eta_x1000":round(float(row.EtaSquaredX1000),5),
         "powerpoint_reference":float(row.PowerPointReference),
         "difference":round(float(row.EtaSquaredX1000-row.PowerPointReference),5)}
        for row in eta.itertuples()
    ]
    ok11=abs(changes["Religious Zionism"]-5.114)<.04
    ok19=all(abs(row["difference"])<.65 for row in eta_comparison)
    diagnostics={
        "slide_11_matches":bool(ok11),
        "slide_19_matches":bool(ok19),
        "slide_11_all_family_changes_pp":{k:round(float(v),5) for k,v in changes.items()},
        "slide_19_variable_comparison":eta_comparison,
        **detail,
    }
    report=out/"historical_recalculation_report.json"
    report.write_text(json.dumps(diagnostics,indent=2,ensure_ascii=False),encoding="utf-8")
    print("HISTORICAL AUDIT DIAGNOSTICS:",json.dumps(diagnostics,indent=2,ensure_ascii=False),flush=True)
    if not ok11 or not ok19:
        failures=[]
        if not ok11:failures.append(
            f"slide 11 Religious Zionism delta={changes['Religious Zionism']:.5f} pp; expected 5.114 pp")
        if not ok19:failures.append("slide 19 eta deviations="+str(
            [(r["variable"],r["difference"]) for r in eta_comparison if abs(r["difference"])>=.65]))
        raise AssertionError("; ".join(failures)+
            "; see outputs/tables/historical_recalculation_report.json")
    return diagnostics
