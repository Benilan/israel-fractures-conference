"""Geographic plots reproduced from the historical presentation plotting method.

Maps are locality-centroid dot maps (EPSG:2039 converted to WGS84). They
are not administrative boundary choropleths and should not be called one.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer

def coordinates(raw: Path):
    frame=pd.read_excel(raw/'bycode2023.xlsx')
    frame.columns=frame.columns.astype(str).str.strip()
    frame=frame.rename(columns={'סמל יישוב':'LocalityCode','קואורדינטות':'Coordinates'})
    frame['LocalityCode']=pd.to_numeric(frame.LocalityCode,errors='coerce')
    digits=frame.Coordinates.astype('string').str.replace(r'\D','',regex=True)
    d11=digits.str.extract(r'^(\d{5})(\d{6})$')
    d12=digits.str.extract(r'^(\d{6})(\d{6})')
    xy=d12.where(digits.str.len().fillna(0).ne(11),d11)
    x=pd.to_numeric(xy[0],errors='coerce');y=pd.to_numeric(xy[1],errors='coerce')
    frame['lon']=np.nan;frame['lat']=np.nan
    valid=x.notna() & y.notna()
    transformer=Transformer.from_crs('EPSG:2039','EPSG:4326',always_xy=True)
    lon,lat=transformer.transform(x.loc[valid].to_numpy(),y.loc[valid].to_numpy())
    frame.loc[valid,'lon']=lon;frame.loc[valid,'lat']=lat
    return frame[['LocalityCode','lon','lat']].drop_duplicates('LocalityCode')

POLITICAL_COLORS={
    'Centre-gauche laïque':'#2389DC','Droite populaire':'#DF7B3A',
    'Sionisme religieux':'#D54E42','Haredi':'#5A4C96',
    'Arabes':'#18A398','Droite nationale laïque':'#E3B33C',
    'Autres – listes marginales':'#9CA3AF',
}
SOCIAL_COLORS={
    'Ultra-orthodoxe':'#6A4C93','National-religieux':'#F07A42',
    'Urbain éduqué':'#348ED2','Populaire':'#DA4E58',
    'Métropolitain aisé':'#26B3A4',
}

def scatter_locality_map(data,category,size,colors,title,target):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    frame=data.dropna(subset=['lon','lat',category]).copy()
    if frame.empty:raise ValueError('Map has no valid localities or coordinates')
    values=pd.to_numeric(frame[size],errors='coerce').fillna(1).clip(lower=1)
    point_size=8+42*np.sqrt(values/values.max())
    fig,ax=plt.subplots(figsize=(5.5,8.5))
    for label,part in frame.groupby(category):
        ax.scatter(part.lon,part.lat,s=point_size.loc[part.index],color=colors.get(str(label),'#9CA3AF'),label=str(label),alpha=.82,linewidths=0)
    # Selected city anchors are approximate cartographic labels for orientation.
    # They do not enter any calculations or locality classification.
    anchors={'Haifa':(34.99,32.79),'Tel Aviv':(34.78,32.08),
             'Jerusalem':(35.22,31.77),'Beersheba':(34.80,31.25),'Ariel':(35.19,32.11)}
    for city,(lon,lat) in anchors.items():
        ax.scatter([lon],[lat],marker='+',c='#222222',s=28,zorder=5,linewidths=.8)
        ax.annotate(city,(lon,lat),xytext=(5,3),textcoords='offset points',
                    fontsize=8,color='#242424',zorder=6,
                    bbox={'facecolor':'white','edgecolor':'none','alpha':.55,'pad':1})
    ax.set_xlim(34.1,35.9);ax.set_ylim(29.3,33.5);ax.axis('off')
    ax.set_title(title,fontsize=12,fontweight='bold')
    ax.legend(loc='lower left',frameon=False,fontsize=8,markerscale=1.2)
    fig.tight_layout()
    target.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(target,dpi=220,transparent=True)
    plt.close(fig)
    return len(frame)

def generate(raw,results_dir,complete,votes):
    geo=coordinates(raw)
    social=complete[['LocalityCode','SocialProfile','pop_approx']].merge(geo,on='LocalityCode',validate='one_to_one',how='left')
    count_social=scatter_locality_map(social,'SocialProfile','pop_approx',SOCIAL_COLORS,
       'Five social profiles by locality — 2022',
       results_dir/'figures/slide_21_social_profiles_map.png')
    # The political-family definition is the same mapping used for the 2022 heatmap.
    from .heatmap_v15 import FAMILIES,OTHER
    political=votes[['LocalityCode','ValidVotes']].copy()
    for label,codes in FAMILIES.items():
        political[label]=votes[codes].apply(pd.to_numeric,errors='coerce').fillna(0).sum(axis=1)
    political[OTHER]=pd.to_numeric(votes.ValidVotes,errors='coerce')-political[list(FAMILIES)].sum(axis=1)
    political['DominantFamily']=political[[*FAMILIES,OTHER]].idxmax(axis=1)
    political=political.merge(geo,on='LocalityCode',how='left',validate='one_to_one')
    count_political=scatter_locality_map(political,'DominantFamily','ValidVotes',POLITICAL_COLORS,
       'Dominant political family by locality — 2022',
       results_dir/'figures/slide_12_political_family_map.png')
    political[['LocalityCode','DominantFamily']].to_csv(results_dir/'tables/slide_12_dominant_family_assignments.csv',index=False)
    return {'slide_12_map_localities':count_political,'slide_21_map_localities':count_social}
