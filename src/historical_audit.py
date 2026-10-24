"""Audit Netanyahu bloc seat totals keyed from electoral source data.

Does not verify all coalition configurations or historical seven-family classifications.
"""
from pathlib import Path
import pandas as pd
from .pipeline_v16 import read_elections

EXPECTED={'K21':60,'K22':55,'K23':58,'K24':52,'K25':64}

def verify_bloc(root:Path):
    source=pd.read_csv(root/'data/manual/netanyahu_bloc_official_seats.csv')
    assert source.groupby('Election').Seats.sum().to_dict()==EXPECTED
    summary=source.groupby('Election',as_index=False).Seats.sum()
    summary['PDFBlocNetanyahu']=summary.Election.map(EXPECTED)
    summary['MatchesPDF']=summary.Seats.eq(summary.PDFBlocNetanyahu)
    return summary

def list_inventory(root:Path):
    elections=read_elections(root/'data/raw')
    reserved={'LocalityCode','RegisteredVoters','Voters','ValidVotes','LocalityName','סמל ועדה','פסולים','שם ועדה','סמל ועדה'}
    result=[]
    for key, df in elections.items():
        total=df.ValidVotes.sum()
        for column in df.columns:
            if column in reserved or str(column).startswith('Unnamed'):continue
            s=pd.to_numeric(df[column],errors='coerce')
            if s.notna().any() and s.fillna(0).sum()>0:
                v=int(s.fillna(0).sum())
                result.append({'Election':key,'ListCode':column,'Votes':v,'NationalSharePct':100*v/total,'AboveThreshold':100*v/total>=3.25,'MappedToHistoricalFamily':False})
    return pd.DataFrame(result).sort_values(['Election','Votes'],ascending=[True,False])
