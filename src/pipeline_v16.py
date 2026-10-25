"""V18 reproducible analysis core, separating verified claims and pending checks."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from .heatmap_v15 import compute, render, round_rows_to_100, FAMILIES, OTHER, PROFILE_ORDER

ELECTIONS = {
 'K21':'Knesset 21 - 2019 - 1.csv', 'K22':'Knesset 22 - 2019 - 2.csv',
 'K23':'Knesset 23 - 2020.csv','K24':'Knesset 24 - 2021.csv','K25':'Knesset 25 - 2022.csv'
}
RELIGIONS={'יהודים':'Jewish','מוסלמים':'Muslim','נוצרים':'Christian','דרוזים':'Druze','דת אחרת':'Other religion'}
PENDING={
 'slide_06_10_party_count':'41 distinct political parties needs a consistent definition of lists and alliances',
 'slide_11_evolution_families':'2019–2022 mapping of lists to stable families not present in validated V18 inputs',
 'slide_12_dominance_stability':'near 90 percent requires five-election harmonized party-family mapping',
 'slide_13_coalition_scenarios':'Netanyahu bloc 60,55,58,52,64 verified; all other coalition scenarios remain unverified',
 'slide_19_published_eta':'V14 group taxonomy differs from V15 and ordinal religiosity merits sensitivity checks'
}

def read_elections(raw):
    result={}
    for k,filename in ELECTIONS.items():
        try:x=pd.read_csv(raw/filename,encoding='utf-8-sig')
        except UnicodeDecodeError:x=pd.read_csv(raw/filename,encoding='cp1255')
        rename={'סמל ישוב':'LocalityCode','סמל יישוב':'LocalityCode','בזב':'RegisteredVoters','מצביעים':'Voters','כשרים':'ValidVotes','שם ישוב':'LocalityName','שם יישוב':'LocalityName'}
        x=x.rename(columns=rename)
        for c in ['LocalityCode','RegisteredVoters','Voters','ValidVotes']:
            x[c]=pd.to_numeric(x[c],errors='coerce')
        result[k]=x
    return result

def read_cbs(raw):
    cbs=pd.read_excel(raw/'selected-data-by-localities-and-statistical-areas-2022-census.xlsx')
    cbs=cbs[cbs.StatArea.isna()].dropna(subset=['LocalityCode']).drop_duplicates('LocalityCode').copy()
    cbs['LocalityCode']=pd.to_numeric(cbs.LocalityCode,errors='coerce').astype('Int64')
    return cbs

def calc_turnout(elections,cbs):
    attr=cbs[['LocalityCode','ReligionHeb']].drop_duplicates('LocalityCode')
    records=[]; national=[]
    for election,df in elections.items():
        national.append({'Election':election,'RegisteredVoters':df.RegisteredVoters.sum(),
                         'Voters':df.Voters.sum(),'TurnoutPct':100*df.Voters.sum()/df.RegisteredVoters.sum()})
        y=df[['LocalityCode','RegisteredVoters','Voters']].merge(attr,on='LocalityCode',how='inner')
        grouped=y.groupby('ReligionHeb',dropna=True)[['RegisteredVoters','Voters']].sum()
        for r,z in grouped.iterrows():
            records.append({'Election':election,'DominantReligion':RELIGIONS.get(r,str(r)),
                            'RegisteredVoters':int(z.RegisteredVoters),'Voters':int(z.Voters),
                            'TurnoutPct':100*z.Voters/z.RegisteredVoters})
    return pd.DataFrame(records),pd.DataFrame(national)

def calc_threshold(k25):
    administrative={'LocalityCode','RegisteredVoters','Voters','ValidVotes','LocalityName','סמל ועדה','פסולים','שם ועדה'}
    parties=[];total=k25.ValidVotes.sum()
    for col in k25:
        if col in administrative or str(col).startswith('Unnamed'):continue
        series=pd.to_numeric(k25[col],errors='coerce')
        if series.notna().any() and series.fillna(0).sum()>0 and col not in ('LocalityCode','RegisteredVoters','Voters','ValidVotes'):
            v=int(series.fillna(0).sum());parties.append({'PartyCode':col,'Votes':v,'SharePct':100*v/total,'AboveThreshold':100*v/total>=3.25})
    out=pd.DataFrame(parties).sort_values('Votes',ascending=False)
    return out,out.loc[~out.AboveThreshold,'Votes'].sum()/total*100

def calc_socioeconomic(raw,cbs):
    # Reuse historical source-file parsing, weighting by locality population.
    from .socio_source import load_socioeconomic
    socio=load_socioeconomic(raw)
    x=cbs[['LocalityCode','pop_approx']].merge(socio[['LocalityCode','SocioEcoCluster']],on='LocalityCode',how='inner')
    x=x.dropna(subset=['pop_approx','SocioEcoCluster']);x=x[x.pop_approx>0].copy()
    x['Indice']=x.SocioEcoCluster.astype(int);x=x[x.Indice.between(1,10)]
    tab=x.groupby('Indice').agg(Localities=('LocalityCode','count'),Population=('pop_approx','sum')).reindex(range(1,11),fill_value=0)
    tab['PopulationSharePct']=100*tab.Population/tab.Population.sum()
    grouped=[]
    for a in [1,3,5,7,9]:
        sub=tab.loc[[a,a+1]]
        grouped.append({'CBSGroup':f'{a}–{a+1}','Population':sub.Population.sum(), 'PopulationSharePct':100*sub.Population.sum()/tab.Population.sum()})
    return tab.reset_index(),pd.DataFrame(grouped),x

def profile_distribution(complete):
    t=complete.groupby('SocialProfile').agg(Localities=('LocalityCode','count'),Population=('pop_approx','sum')).reindex(PROFILE_ORDER)
    t['ShareLocalitiesPct']=100*t.Localities/t.Localities.sum()
    t['SharePopulationPct']=100*t.Population/t.Population.sum()
    return t.reset_index()

def calc_religiosity_table(cbs):
    """Slide 16: population-weighted locality indicators (not person-level traits)."""
    fields=['age_median','size_avg','AcadmCert_pcnt','employeesAnnual_medWage']
    base=cbs.loc[(pd.to_numeric(cbs['religion'],errors='coerce')==1)].copy()
    base['LifestyleCode']=pd.to_numeric(base['hh_MidatDatiyut_Name'],errors='coerce')
    base=base.loc[base.LifestyleCode.isin([1,2,3,4])]
    names={1:'Secular',2:'Traditional',3:'Religious',4:'Haredi'}
    records=[]
    for k,group in base.groupby('LifestyleCode'):
        result={'Profile':names[int(k)],'Localities':len(group),'Population':group.pop_approx.sum()}
        for name in fields:
            vals=pd.to_numeric(group[name],errors='coerce');w=pd.to_numeric(group.pop_approx,errors='coerce')
            ok=vals.notna() & w.notna() & w.gt(0)
            result[name]=float(np.average(vals[ok],weights=w[ok])) if ok.any() else None
        records.append(result)
    return pd.DataFrame(records)

def calc_nearest_neighbour(raw,complete):
    """Slide 21: Euclidean nearest neighbour, projected centroids (EPSG:2039)."""
    from scipy.spatial import cKDTree
    geo=pd.read_excel(raw/'bycode2023.xlsx').rename(columns={'סמל יישוב':'LocalityCode','קואורדינטות':'Coordinates'})
    geo['LocalityCode']=pd.to_numeric(geo.LocalityCode,errors='coerce')
    digits=geo.Coordinates.map(lambda v: str(int(v)) if pd.notna(v) else '').astype('string')
    a=digits.str.extract(r'^(\d{5})(\d{6})$')
    b=digits.str.extract(r'^(\d{6})(\d{6})$')
    xy=b.where(digits.str.len().fillna(0).ne(11),a).apply(pd.to_numeric,errors='coerce')
    geo['x']=xy[0];geo['y']=xy[1]
    match=complete[['LocalityCode','SocialProfile']].merge(geo[['LocalityCode','x','y']],on='LocalityCode',how='inner').dropna(subset=['x','y']).drop_duplicates('LocalityCode')
    if len(match)<2:raise AssertionError('Not enough locality coordinates')
    points=match[['x','y']].to_numpy()
    distances,ids=cKDTree(points).query(points,k=2)
    matches=(match.SocialProfile.to_numpy()==match.SocialProfile.to_numpy()[ids[:,1]])
    proportions=match.SocialProfile.value_counts(normalize=True)
    random_base=float((proportions**2).sum())
    return pd.DataFrame([{'LocalitiesWithCoordinates':len(match),'ObservedSameNearestPct':100*float(matches.mean()),'RandomIndependentBaselinePct':100*random_base,'BaselineDescription':'independent random assignment with observed profile proportions'}])

def calc_v15_eta_sensitivity(raw,cbs,complete):
    """V15 weighted eta-squared sensitivity, NOT a validation of slide 19 V14."""
    votes=pd.read_csv(raw/'Knesset 25 - 2022.csv',encoding='utf-8-sig').rename(columns={'סמל ישוב':'LocalityCode','כשרים':'ValidVotes'})
    from .heatmap_v15 import FAMILIES,OTHER
    votes['LocalityCode']=pd.to_numeric(votes.LocalityCode,errors='coerce')
    for fam,codes in FAMILIES.items():
        votes[fam]=votes[codes].apply(pd.to_numeric,errors='coerce').fillna(0).sum(axis=1)
    votes[OTHER]=pd.to_numeric(votes.ValidVotes,errors='coerce')-votes[list(FAMILIES)].sum(axis=1)
    all_families=[*FAMILIES,OTHER]
    votes['DominantFamily']=votes[all_families].idxmax(axis=1)
    selected=['AcadmCert_pcnt','hh_MidatDatiyut_Name','Computer_avg','age_median','employeesAnnual_medWage','ChldBorn_avg']
    data=cbs[['LocalityCode','pop_approx',*selected]].merge(votes[['LocalityCode','DominantFamily']],on='LocalityCode',how='inner')
    out=[]
    for field in selected:
        sub=data[['DominantFamily','pop_approx',field]].copy()
        sub[field]=pd.to_numeric(sub[field],errors='coerce')
        sub=sub.dropna();sub=sub.loc[sub.pop_approx>0]
        counts=sub.DominantFamily.value_counts();sub=sub[sub.DominantFamily.isin(counts[counts>=5].index)]
        weight=sub.pop_approx.to_numpy(float);x=sub[field].to_numpy(float)
        grand=np.average(x,weights=weight);sst=np.sum(weight*(x-grand)**2)
        ssb=sum(g.pop_approx.sum()*(np.average(g[field],weights=g.pop_approx)-grand)**2 for _,g in sub.groupby('DominantFamily'))
        out.append({'Variable':field,'WeightedEtaSquared':ssb/sst if sst>0 else np.nan,'Localities':len(sub),'Method':'V15 families, locality-level descriptive weighted eta squared'})
    return pd.DataFrame(out).sort_values('WeightedEtaSquared',ascending=False)

def output_csv(df,path):
    df.to_csv(path,index=False,encoding='utf-8-sig')

def run(root:Path):
    root=Path(root);raw=root/'data/raw';out=root/'outputs';tab=out/'tables';fig=out/'figures';tab.mkdir(parents=True,exist_ok=True);fig.mkdir(parents=True,exist_ok=True)
    elections=read_elections(raw);cbs=read_cbs(raw)
    turnout,national=calc_turnout(elections,cbs)
    output_csv(turnout,tab/'slide_07_turnout_dominant_religion.csv')
    output_csv(national,tab/'slide_07_national_reference.csv')
    threshold,below=calc_threshold(elections['K25'])
    # Three highlighted losing lists are not the same as all losing lists.
    featured_codes=['מרצ','ד','ב']
    featured=threshold.loc[threshold.PartyCode.isin(featured_codes)]
    if len(featured)!=3 or featured.AboveThreshold.any():
        raise AssertionError('Slide 8 featured below-threshold lists were not found')
    featured_pct=float(featured.SharePct.sum())
    if not (7.20<featured_pct<7.35 and 8.65<below<8.90):
        raise AssertionError('Slide 8 featured/all losing-list shares differ from reference')
    pd.DataFrame([{'Scope':'Three highlighted lists (Meretz, Balad, Jewish Home)','SharePct':featured_pct},
                  {'Scope':'All below-threshold lists','SharePct':float(below)},
                  {'Scope':'Other below-threshold lists','SharePct':float(below-featured_pct)}]).to_csv(
        tab/'slide_08_losing_vote_scope_comparison.csv',index=False)
    output_csv(threshold,tab/'slide_08_threshold_all_lists_2022.csv')
    from .deck_visuals import (plot_2022_parties, plot_turnout, plot_seven_families_reference,
        plot_coalition_reference, plot_anova_reference, plot_cbs_reference)
    plot_2022_parties(threshold, fig/'slide_08_results_2022_by_party.png')
    pct,grouped,complete,stats,meta=compute(raw)
    socio10,socio5,socio_base=calc_socioeconomic(raw,cbs)
    output_csv(socio10,tab/'slide_17_socioeconomic_1_to_10.csv')
    output_csv(socio5,tab/'slide_17_socioeconomic_5_groups.csv')
    profile=profile_distribution(complete)
    religiosity=calc_religiosity_table(cbs)
    output_csv(religiosity,tab/'slide_16_religiosity_weighted_descriptives.csv')
    plot_cbs_reference(religiosity, fig/'slide_16_cbs_by_religiosity.png')
    plot_seven_families_reference(fig/'slide_11_seven_families_reference.png')
    plot_coalition_reference(fig/'slide_13_all_blocs_reference.png')
    plot_anova_reference(fig/'slide_19_weighted_anova_V14_reference.png')
    neighbour=calc_nearest_neighbour(raw,complete)
    output_csv(neighbour,tab/'slide_21_nearest_neighbour_check.csv')
    # Recompute historical electoral Ward families and V14 weighted eta
    # independently of the figures embedded in the conference PowerPoint.
    from .historical_reproduction import export as export_historical
    historic_audit=export_historical(raw,tab)
    eta=calc_v15_eta_sensitivity(raw,cbs,complete)
    output_csv(eta,tab/'slide_19_V15_sensitivity_NOT_published_V14.csv')
    output_csv(profile,tab/'slide_20_21_social_profile_population.csv')
    output_csv(stats,tab/'slide_20_cluster_diagnostics.csv')
    output_csv(complete[['LocalityCode','SocialProfile']],tab/'slide_20_21_profile_assignments.csv')
    output_csv(pct.round(4).reset_index().rename(columns={'SocialProfile':'Social profile'}),tab/'slide_23_heatmap_2022_exact.csv')
    rounded=round_rows_to_100(pct)
    output_csv(rounded.reset_index().rename(columns={'SocialProfile':'Social profile'}),tab/'slide_23_heatmap_2022_rounded100.csv')
    render(rounded,fig/'slide_23_heatmap_2022.png')
    from .maps import generate as generate_maps
    map_checks=generate_maps(raw,out,complete,elections['K25'])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    g=socio5.set_index('CBSGroup').PopulationSharePct
    ax=g.plot.bar(figsize=(8,4),title='CBS socioeconomic distribution (2021) — population 2022')
    ax.set_ylabel('Population share (%)');ax.set_xlabel('CBS index')
    ax.figure.tight_layout();ax.figure.savefig(fig/'slide_17_cbs_socioeconomic.png',dpi=180);plt.close(ax.figure)
    plot_turnout(turnout,national,fig/'slide_07_turnout_religion.png')
    checks={'slide_07_complete':len(turnout)>=20,'slide_08_threshold_range':8<below<10,
           'slide_17_groups_sum_100':bool(abs(socio5.PopulationSharePct.sum()-100)<1e-8),
           'slide_20_21_profiles_1040':int(profile.Localities.sum())==1040,
           'slide_23_rows_100':bool((rounded.sum(axis=1)==100).all()),
           'slide_16_four_lifestyles':len(religiosity)==4,
           'slide_21_geographic_neighbors':bool(50 < neighbour.ObservedSameNearestPct.iat[0] < 65),
           'slide_19_sensitivity_generated':len(eta)==6,
           'slide_23_haredi_80_69':abs(pct.loc['Ultra-orthodoxe','Haredi']-80.69)<0.05,
           'slide_23_metro_58_76':abs(pct.loc['Métropolitain aisé','Centre-gauche laïque']-58.76)<0.05}
    checks['slide_12_map_generated']=map_checks['slide_12_map_localities']>500
    checks['slide_21_map_generated']=map_checks['slide_21_map_localities']>500
    checks={k:bool(v) for k,v in checks.items()}
    from .historical_audit import verify_bloc, list_inventory
    bloc=verify_bloc(root)
    inventory=list_inventory(root)
    output_csv(bloc,tab/'slide_13_verified_netanyahu_bloc.csv')
    # Full coalition composition chart is generated from the slide 13 reference.
    output_csv(inventory,tab/'slides_09_12_historical_list_inventory_UNMAPPED.csv')
    checks['slide_13_netanyahu_bloc_official_seats']=bool(bloc.MatchesPDF.all())
    checks['slide_11_independent_Ward_reproduction']=historic_audit['slide_11_matches']
    checks['slide_19_independent_V14_eta_reproduction']=historic_audit['slide_19_matches']
    report={'pipeline':'Publication release V18','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
            'statistics':{'socio_localities':len(socio_base),'socio_population':float(socio_base.pop_approx.sum()),
             'profile_localities':int(profile.Localities.sum()),'nearest_neighbour_pct':float(neighbour.ObservedSameNearestPct.iat[0]),'profile_votes':meta['valid_votes_in_scope'],
             'votes_below_threshold_pct':float(below)},'not_certified':PENDING}
    (tab/'validation_v16.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not all(checks.values()):raise AssertionError('At least one V18 check failed')
    return report
