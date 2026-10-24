"""Additional presentation charts produced from actual V18 tabular results.

No synthetic numbers or inferred historical family mapping.
"""
from pathlib import Path
import pandas as pd

def plot_2022_party_results(threshold: pd.DataFrame, destination: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ordered=threshold.sort_values("SharePct",ascending=True)
    fig,ax=plt.subplots(figsize=(11,max(7,len(ordered)*.23)))
    colors=["#2374ab" if b else "#cc5b51" for b in ordered["AboveThreshold"]]
    ax.barh(ordered.PartyCode.astype(str), ordered.SharePct, color=colors)
    ax.axvline(3.25,color="#202020",linestyle="--",linewidth=1.6,label="3.25% electoral threshold")
    ax.set_xlabel("Share of valid ballots (%)")
    ax.set_ylabel("Ballot-list code (original Hebrew)")
    ax.set_title("2022 Knesset election — national results by ballot list")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(destination,dpi=180,bbox_inches="tight")
    plt.close(fig)

def plot_cbs_religiosity(table: pd.DataFrame, destination: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    measurements=[
        ("age_median","Median age (years)"),
        ("size_avg","Average household size"),
        ("AcadmCert_pcnt","Higher education (%)"),
        ("employeesAnnual_medWage","Median employee annual earnings (NIS)"),
    ]
    available=[(column,title) for column,title in measurements if column in table.columns]
    if not available:
        raise ValueError("No CBS religiosity measures available")
    fig,axes=plt.subplots(len(available),1,figsize=(10,3*len(available)),layout="constrained")
    if len(available)==1:axes=[axes]
    for ax,(column,title) in zip(axes,available):
        ax.bar(table.Profile, pd.to_numeric(table[column],errors="coerce"),color="#3478aa")
        ax.set_title(title,fontsize=11)
        ax.tick_params(axis="x",rotation=10)
    fig.suptitle("CBS demographic characteristics by locality religiosity profile",fontsize=14)
    fig.savefig(destination,dpi=180,bbox_inches="tight")
    plt.close(fig)

def plot_verified_netanyahu_bloc(table: pd.DataFrame, destination: Path):
    """The original verified Netanyahu seat series, not a complete coalition decomposition."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ordered=table.set_index("Election").reindex(["K21","K22","K23","K24","K25"])
    fig,ax=plt.subplots(figsize=(9,4.5))
    ax.plot(ordered.index,ordered.Seats,marker="o",linewidth=2.5,color="#3478aa",label="Netanyahu bloc")
    ax.axhline(61,color="#ca5757",linestyle="--",label="61-seat majority")
    ax.set_ylim(0,72)
    ax.set_ylabel("Knesset seats")
    ax.set_title("Verified Netanyahu-bloc seat totals — K21 to K25")
    ax.grid(axis="y",alpha=.2)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(destination,dpi=180)
    plt.close(fig)
