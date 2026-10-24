"""Deterministic reproduction of the conference's 2022 vote-by-social-profile heatmap.

Observation unit: locality. Percentages aggregate ballots cast within each
social profile. Cluster names are interpreted from computed characteristics,
not arbitrary K-means label numbers.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

FEATURES = ['hh_MidatDatiyut_Name','ChldBorn_avg','age_median','AcadmCert_pcnt','africa_pcnt','europe_pcnt']
FAMILIES = {
    'Centre-gauche laïque': ['אמת','מרצ','פה','כן'],
    'Droite populaire': ['מחל'],
    'Sionisme religieux': ['ט','ב'],
    'Haredi': ['ג','שס'],
    'Arabes': ['עם','ום','ד'],
    'Droite nationale laïque': ['ל'],
}
OTHER = 'Autres – listes marginales'
PROFILE_ORDER = ['Ultra-orthodoxe','National-religieux','Urbain éduqué','Populaire','Métropolitain aisé']


def load_inputs(raw_dir:Path):
    votes = pd.read_csv(raw_dir/'Knesset 25 - 2022.csv', encoding='utf-8-sig').rename(columns={'סמל ישוב':'LocalityCode','כשרים':'ValidVotes'})
    cbs = pd.read_excel(raw_dir/'selected-data-by-localities-and-statistical-areas-2022-census.xlsx')
    cbs = cbs[cbs.StatArea.isna()].dropna(subset=['LocalityCode']).drop_duplicates('LocalityCode')
    cbs['LocalityCode']=cbs['LocalityCode'].astype('int64')
    votes['LocalityCode']=pd.to_numeric(votes['LocalityCode'],errors='raise').astype('int64')
    for c in ['ValidVotes',*{x for values in FAMILIES.values() for x in values}]:
        votes[c]=pd.to_numeric(votes[c],errors='coerce').fillna(0)
    return votes,cbs


def name_clusters(df):
    """Name clusters by observed social characteristics, not numeric labels.

    Highest coded religiosity with youngest population = ultra-orthodox;
    next highest religiosity = national-religious; among the rest, the highest
    education rates identify metropolitan-wealthy and urban-educated profiles.
    The residual is labeled popular. This assignment is calibrated to the
    V15 CBS 2022 dataset and should be reviewed if inputs change.
    """
    stats = df.groupby('cluster').agg(religiosity=('hh_MidatDatiyut_Name','mean'),
       median_age=('age_median','mean'), education=('AcadmCert_pcnt','mean'),
       n_localities=('LocalityCode','size'), population=('pop_approx','sum'))
    remain=set(stats.index)
    ranks={}
    h=max(remain,key=lambda i:(stats.loc[i,'religiosity'],-stats.loc[i,'median_age']))
    ranks[h]='Ultra-orthodoxe';remain.remove(h)
    nr=max(remain,key=lambda i:stats.loc[i,'religiosity'])
    ranks[nr]='National-religieux';remain.remove(nr)
    rich=max(remain,key=lambda i:stats.loc[i,'education'])
    ranks[rich]='Métropolitain aisé';remain.remove(rich)
    urban=max(remain,key=lambda i:stats.loc[i,'education'])
    ranks[urban]='Urbain éduqué';remain.remove(urban)
    ranks[remain.pop()]='Populaire'
    stats['profile']=[ranks[i] for i in stats.index]
    return ranks,stats.reset_index()


def compute(raw_dir:Path):
    votes,cbs=load_inputs(raw_dir)
    # Locality-level complete cases, 2022 only.
    base=votes[['LocalityCode','ValidVotes']].merge(
        cbs[['LocalityCode','pop_approx',*FEATURES]],on='LocalityCode',how='left',validate='one_to_one')
    complete=base.dropna(subset=FEATURES).copy()
    x=StandardScaler().fit_transform(complete[FEATURES])
    weights=complete.pop_approx.fillna(1).clip(lower=1)
    model=KMeans(n_clusters=5, random_state=42, n_init=20)
    complete['cluster']=model.fit_predict(x,sample_weight=weights)
    assignments,stats=name_clusters(complete)
    complete['SocialProfile']=complete['cluster'].map(assignments)

    family_cols=list(FAMILIES)
    for family,party_codes in FAMILIES.items():
        votes[family]=votes[party_codes].sum(axis=1)
    votes[OTHER]=votes.ValidVotes-votes[family_cols].sum(axis=1)
    if (votes[OTHER]<0).any():raise AssertionError('Family mapping exceeds valid vote totals')
    cols=[*family_cols,OTHER]
    merged=votes[['LocalityCode','ValidVotes',*cols]].merge(
        complete[['LocalityCode','SocialProfile']],on='LocalityCode',how='inner',validate='one_to_one')
    grouped=merged.groupby('SocialProfile')[['ValidVotes',*cols]].sum().reindex(PROFILE_ORDER)
    pct=grouped[cols].div(grouped.ValidVotes,axis=0).mul(100)
    if not np.allclose(pct.sum(axis=1),100,atol=1e-6):raise AssertionError('Shares do not total 100%')
    diagnostics={'input_vote_localities':int(len(votes)),
      'cbs_complete_localities':int(len(complete)), 'matched_localities':int(len(merged)),
      'valid_votes_in_scope':int(grouped.ValidVotes.sum()),
      'note':'Locality-based associations, not individual votes or causal effects.'}
    return pct,grouped,complete,stats,diagnostics


def round_rows_to_100(pct: pd.DataFrame) -> pd.DataFrame:
    """Round using largest remainders and stable column-order tie breaking.

    Each rounded row totals exactly 100 points while raw shares remain intact.
    """
    values = pct.to_numpy(dtype=float)
    if not np.allclose(values.sum(axis=1), 100.0, atol=0.05):
        raise ValueError('Input rows must sum to 100 before rounding')
    floors = np.floor(values).astype(int)
    remainders = values - floors
    for row in range(len(floors)):
        n = int(100 - floors[row].sum())
        if n < 0 or n > len(pct.columns):
            raise ValueError('Unexpected rounding residual')
        order = np.argsort(-remainders[row], kind='stable')
        floors[row, order[:n]] += 1
    result = pd.DataFrame(floors, index=pct.index, columns=pct.columns)
    if not (result.sum(axis=1) == 100).all():
        raise AssertionError('Rounded heatmap row total != 100')
    return result


def render(pct:pd.DataFrame,output:Path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    fig,ax=plt.subplots(figsize=(15,5.8))
    fig.patch.set_facecolor('#031226');ax.set_facecolor('#031226')
    vals=pct.to_numpy()
    cmap=LinearSegmentedColormap.from_list('navy_to_cyan',['#092c51','#086fa6','#0eb0ef'])
    im=ax.imshow(vals,cmap=cmap,vmin=0,vmax=81,aspect='auto')
    ax.set_xticks(range(len(pct.columns)),pct.columns)
    ax.set_yticks(range(len(pct.index)),pct.index)
    ax.tick_params(axis='both',length=0,colors='white',labelsize=10)
    for tick in ax.get_xticklabels():tick.set_rotation(20);tick.set_ha('right')
    for i in range(len(pct)):
        for j in range(len(pct.columns)):
            ax.text(j,i,f'{vals[i,j]:.0f} %',ha='center',va='center',color='white',fontsize=11,fontweight='bold')
    for spine in ax.spines.values():spine.set_visible(False)
    ax.set_title('Voting by social profile – Israel 2022 | Seven political families',color='white',fontsize=16,pad=18,loc='left')
    fig.text(.13,.015,'Sources: Central Elections Committee and CBS 2022; locality-aggregated votes',color='#9db0c9',fontsize=9)
    fig.subplots_adjust(left=.17,right=.98,top=.86,bottom=.32)
    fig.savefig(output,dpi=200,facecolor=fig.get_facecolor(),bbox_inches='tight')
    plt.close(fig)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=p.parse_args()
    out=args.root/'outputs'; (out/'tables').mkdir(parents=True,exist_ok=True);(out/'figures').mkdir(parents=True,exist_ok=True)
    pct,grouped,complete,stats,diagnostics=compute(args.root/'data/raw')
    pct.round(2).to_csv(out/'tables/heatmap_2022_corrected.csv',encoding='utf-8-sig',index_label='Social profile')
    round_rows_to_100(pct).to_csv(out/'tables/heatmap_2022_rounded.csv',encoding='utf-8-sig',index_label='Social profile')
    grouped.to_csv(out/'tables/heatmap_votes_by_profile.csv',encoding='utf-8-sig',index_label='Social profile')
    complete[['LocalityCode','cluster','SocialProfile']].to_csv(out/'tables/social_profiles_assignments_2022.csv',index=False,encoding='utf-8-sig')
    stats.to_csv(out/'tables/cluster_profiles_diagnostics.csv',index=False)
    (out/'tables/validation_report.json').write_text(json.dumps(diagnostics,indent=2,ensure_ascii=False),encoding='utf-8')
    render(round_rows_to_100(pct),out/'figures/heatmap_2022_corrected.png')
    print(pct.round(2).to_string());print(json.dumps(diagnostics,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
