"""CBS 2021 socioeconomic locality/authority XLSX loader from historical analysis."""
from pathlib import Path
import numpy as np
import pandas as pd

def number(v):
    if pd.isna(v): return np.nan
    t = str(v).strip().replace('\u00a0','').replace(' ','').replace(',','.')
    try: return float(t)
    except ValueError: return np.nan

def load_socioeconomic(raw_dir):
    raw_dir = Path(raw_dir)
    a = pd.read_excel(raw_dir/'24_24_230t1.xlsx',skiprows=6,header=None)
    b = pd.read_excel(raw_dir/'Copie de 24_24_230t3.xlsx',skiprows=10,header=None)
    x = pd.DataFrame({'LocalityCode':a.iloc[:,1].map(number),
        'SocioEcoIndex':a.iloc[:,5].map(number),
        'SocioEcoRank':a.iloc[:,6].map(number),
        'SocioEcoCluster':a.iloc[:,7].map(number)})
    y = pd.DataFrame({'LocalityCode':b.iloc[:,5].map(number),
        'SocioEcoIndex':b.iloc[:,10].map(number),
        'SocioEcoRank':b.iloc[:,11].map(number),
        'SocioEcoCluster':b.iloc[:,12].map(number)})
    return pd.concat([x,y],ignore_index=True).dropna(subset=['LocalityCode']).assign(LocalityCode=lambda d:d.LocalityCode.astype('Int64')).drop_duplicates('LocalityCode')
