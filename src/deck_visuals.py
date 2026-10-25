"""Presentation-faithful plots, based on the user-supplied final PowerPoint.

Data sources remain explicit:
* 2022 vote shares, CBS and turnout: computed by the pipeline.
* K21–K25 seven-family series and coalition blocks and published V14 ANOVA:
  figures embedded in the final PPTX, pending complete independent reconstruction.
Do not confuse reference-chart rendering with statistical validation.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY="#06172b"; BLUE="#287dc0"; ORANGE="#ed8754"; GREEN="#27a796"; RED="#d85552"
FAMILIES=['Secular center-left','Popular right','Religious Zionism','Haredim','Arab parties','Secular national right','Other lists']
FAMILY_COLORS=[BLUE,ORANGE,RED,"#6852a3",GREEN,"#dcad42","#9aa4b1"]
ELECTIONS=['Apr 2019','Sep 2019','Mar 2020','Mar 2021','Nov 2022']
REFERENCE_SHARE=np.array([
 [35.9,30.0,6.9,11.8,7.8,6.8,.8],
 [35.1,25.1,7.8,13.5,10.6,7.0,1.0],
 [32.4,29.5,5.2,13.7,12.7,5.7,.8],
 [31.2,24.2,11.3,12.8,8.6,10.4,1.5],
 [33.7,23.4,12.0,14.1,10.7,4.5,1.5],
])
# Data transcribed from the embedded editable chart of slide 11.
assert np.allclose(REFERENCE_SHARE.sum(axis=1),100,atol=.11)

PARTY_NAMES={
 'מחל':'Likud','פה':'Yesh Atid','ט':'Religious Zionism',
 'כן':'National Unity','שס':'Shas','ג':'United Torah Judaism',
 'ל':'Yisrael Beiteinu','עם':"Ra'am",'ום':'Hadash-Ta’al',
 'אמת':'Labor','מרצ':'Meretz','ד':'Balad','ב':'Jewish Home',
}
MAIN_2022=['Likud','Yesh Atid','Religious Zionism','National Unity','Shas',
 'United Torah Judaism','Yisrael Beiteinu',"Ra'am",'Hadash-Ta’al',
 'Labor','Meretz','Balad','Jewish Home']
K25_PPT_VALUES=[23.41,17.79,10.84,9.08,8.25,5.88,4.48,4.07,3.75,3.69,3.16,2.91,1.19]

def plot_2022_parties(threshold:pd.DataFrame,out:Path):
    """Show the thirteen lists selected on slide 8; votes come from K25 CSV."""
    x=threshold.copy()
    x['Name']=x.PartyCode.astype(str).map(PARTY_NAMES)
    x=x[x.Name.isin(MAIN_2022)].set_index('Name').reindex(MAIN_2022)
    if x.SharePct.isna().any():
        raise ValueError('Missing an explicitly mapped 2022 ballot list: '+str(x[x.SharePct.isna()].index.tolist()))
    actual=x.SharePct.to_numpy(float)
    # Match the presentation to within the rounding displayed on its slide.
    if not np.allclose(actual,K25_PPT_VALUES,atol=.06):
        raise AssertionError('2022 party results differ from the supplied PowerPoint reference')
    fig,ax=plt.subplots(figsize=(12,7))
    y=np.arange(len(x))
    ax.barh(y,actual,color=[BLUE if v>=3.25 else RED for v in actual],height=.65)
    ax.invert_yaxis();ax.set_yticks(y,MAIN_2022,fontsize=11)
    ax.set_xlim(0,25.8);ax.axvline(3.25,ls='--',color=ORANGE,lw=1.7)
    ax.text(3.35,-.85,'3.25% electoral threshold',color=ORANGE,fontsize=10)
    for j,value in enumerate(actual): ax.text(value+.2,j,f'{value:.2f}%',va='center',fontsize=10)
    ax.set_title('2022 KNESSET ELECTION — PARTY RESULTS',loc='left',fontsize=17,fontweight='bold',pad=20)
    ax.set_xlabel('Share of valid votes (%)');ax.spines[['top','right','left']].set_visible(False)
    ax.tick_params(axis='y',length=0);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
    fig.text(.12,.005,'Below threshold: Meretz, Balad and Jewish Home together received about 7.3% of valid votes.',fontsize=9,color='#555')
    fig.tight_layout(rect=(0,.03,1,1));fig.savefig(out,dpi=190,bbox_inches='tight');plt.close(fig)

def plot_turnout(turnout:pd.DataFrame,national:pd.DataFrame,out:Path):
    series=['Jewish','Muslim','Christian','Druze','Other religion']
    palette=[BLUE,RED,"#8b5fb6",ORANGE,GREEN]
    fig,ax=plt.subplots(figsize=(12.5,6.4))
    for name,col in zip(series,palette):
        x=turnout[turnout.DominantReligion.eq(name)].set_index('Election').reindex(['K21','K22','K23','K24','K25'])
        if x.TurnoutPct.isna().any():continue
        ax.plot(range(5),x.TurnoutPct,color=col,marker='o',lw=2.4,label=name)
        ax.annotate(f'{x.TurnoutPct.iloc[-1]:.0f}%',(4,x.TurnoutPct.iloc[-1]),xytext=(8,0),
                    textcoords='offset points',va='center',fontsize=10,color=col)
    benchmark=national.set_index('Election').reindex(['K21','K22','K23','K24','K25']).TurnoutPct.to_numpy()
    ax.plot(range(5),benchmark,color='#454545',lw=2,ls='--',label='National turnout')
    ax.set_xlim(-.1,4.45);ax.set_ylim(40,80)
    ax.set_xticks(range(5),['Apr 2019\nK21','Sep 2019\nK22','Mar 2020\nK23','Mar 2021\nK24','Nov 2022\nK25'])
    ax.set_ylabel('Turnout (%)');ax.set_title('TURNOUT BY LOCALITY’S DOMINANT RELIGION',loc='left',fontsize=16,pad=18)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.12),ncol=3,frameon=False,fontsize=9)
    fig.text(.12,.01,'CBS dominant religion of each locality, not the religion of individual voters.',fontsize=9,color='#666')
    fig.tight_layout(rect=(0,.045,1,1));fig.savefig(out,dpi=190,bbox_inches='tight');plt.close(fig)

def plot_seven_families_reference(out:Path, computed_share:pd.DataFrame):
    fig,ax=plt.subplots(figsize=(12,6.8))
    values=computed_share.reindex(index=['K21','K22','K23','K24','K25'],columns=FAMILIES)
    if values.isna().any().any():raise ValueError('Incomplete recomputed family shares')
    actual=values.to_numpy(dtype=float)
    bottom=np.zeros(5)
    for j,(family,c) in enumerate(zip(FAMILIES,FAMILY_COLORS)):
        v=actual[:,j]
        ax.bar(np.arange(5),v,bottom=bottom,label=family,width=.65,color=c)
        bottom+=v
    ax.set_xticks(range(5),ELECTIONS);ax.set_ylim(0,100);ax.set_ylabel('Share of valid votes (%)')
    ax.set_title('EVOLUTION OF SEVEN POLITICAL FAMILIES · 2019–2022',loc='left',fontsize=16,pad=18)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.13),ncol=4,frameon=False,fontsize=9)
    diffs=actual[-1]-actual[0]
    comment='Apr 2019 → Nov 2022: '+ '   '.join(f'{n}: {x:+.1f} pp' for n,x in zip(['Center-left','Popular right','Rel. Zionism','Haredim','Arab','Secular right','Other'],diffs))
    fig.text(.07,.022,comment,fontsize=8,color='#333')
    fig.tight_layout(rect=(0,.065,1,1));fig.savefig(out,dpi=180,bbox_inches='tight');plt.close(fig)

# Segments visible in the user-supplied final slide 13 (not inferred from ballots).
# Each election is shown as two separate displayed blocs. Other parties are
# intentionally omitted because the historical slide did not allocate all 120 seats.
COALITIONS={
 'K21':{'Netanyahu':[('Likud',35),('Haredim',16),('National religious',9)],
        'Opposition':[('Center',35),('Left',10)]},
 'K22':{'Netanyahu':[('Likud',32),('Haredim',16),('National religious',7)],
        'Opposition':[('Center',33),('Left',11)]},
 'K23':{'Netanyahu':[('Likud',36),('Haredim',16),('National religious',6)],
        'Opposition':[('Center',33),('Left',7)]},
 'K24':{'Netanyahu':[('Likud',30),('Haredim',16),('National religious',6)],
        'Opposition':[('Center',31),('Left',13),('Yamina',7),('Ra’am',4),('Lieberman',7)]},
 'K25':{'Netanyahu':[('Likud',32),('Haredim',18),('National religious',14)],
        'Opposition':[('Center',36),('Left',4),('Lieberman',6)]},
}
def coalition_coverage():
    """Quantify what the conference's stylized bloc figure leaves unallocated.

    The values do not certify opposition membership or government membership.
    """
    rows=[]
    for election,blocs in COALITIONS.items():
        net=sum(v for _,v in blocs["Netanyahu"])
        other=sum(v for _,v in blocs["Opposition"])
        rows.append({"Election":election,"NetanyahuBlocSeats":net,
                     "OtherDisplayedSeats":other,
                     "UnallocatedSeats":120-net-other,
                     "Complete120SeatPartition":net+other==120})
    return pd.DataFrame(rows)

COALITION_COLORS={'Likud':BLUE,'Haredim':'#6852a3','National religious':RED,
 'Center':'#83abc9','Left':'#e0ac66','Yamina':'#72a76c','Ra’am':GREEN,'Lieberman':ORANGE}
def plot_coalition_reference(out:Path):
    fig,ax=plt.subplots(figsize=(12,6.5))
    y=[];lab=[]
    for k,group in COALITIONS.items():
        for side,sections in group.items():
            yy=len(y);y.append(yy);lab.append(f'{k} · {side}')
            left=0
            for title,v in sections:
                ax.barh(yy,v,left=left,height=.65,color=COALITION_COLORS[title])
                if v>=6:ax.text(left+v/2,yy,str(v),color='white',ha='center',va='center',fontsize=10,fontweight='bold')
                left+=v
            ax.text(left+.8,yy,str(left),va='center',fontsize=10,fontweight='bold')
    ax.invert_yaxis();ax.set_yticks(y,lab);ax.set_xlim(0,73)
    ax.axvline(61,color=RED,ls='--',lw=1.7,label='61-seat benchmark')
    handles=[plt.Rectangle((0,0),1,1,color=c) for c in COALITION_COLORS.values()]
    ax.legend(handles,list(COALITION_COLORS),loc='upper center',bbox_to_anchor=(.5,-.1),ncol=4,frameon=False,fontsize=9)
    ax.set_title('THE BATTLE FOR 61 SEATS · K21 TO K25',loc='left',fontsize=16,pad=15)
    ax.set_xlabel('Knesset seats');ax.spines[['top','right']].set_visible(False)
    fig.text(.13,.005,'Slide 13 reference allocations; bars do not represent an exhaustive partition of all 120 seats.',fontsize=9,color='#555')
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(out,dpi=180,bbox_inches='tight');plt.close(fig)

ETA=[('Higher education',714),('Religiosity',694),('Computer equipment',671),
 ('Median age',661),('Median employee wages',658),('Average number of children',624)]
def plot_anova_reference(out:Path, computed_eta:pd.DataFrame):
    fig,ax=plt.subplots(figsize=(11,5.3))
    x=computed_eta.sort_values('EtaSquaredX1000',ascending=False)
    names=x.Label.tolist();vals=x.EtaSquaredX1000.to_numpy(float)
    if len(vals)!=6:raise ValueError('Expected six recomputed ANOVA measures')
    bars=ax.barh(names,vals,color=[BLUE]+['#6688aa']*5,height=.65)
    ax.invert_yaxis();ax.set_xlim(0,790);ax.set_xlabel('Population-weighted η² × 1,000')
    ax.set_title('WHICH LOCALITY CHARACTERISTICS MOST DISTINGUISH VOTE PATTERNS?',loc='left',fontsize=14,pad=18)
    for b,v in zip(bars,vals):ax.text(v+6,b.get_y()+b.get_height()/2,str(v),va='center')
    ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
    ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True)
    fig.text(.13,.012,'Recomputed V14 population-weighted descriptive eta² from CBS localities and unmerged Ward groups.',fontsize=9,color='#666')
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(out,dpi=180,bbox_inches='tight');plt.close(fig)

def plot_cbs_reference(religiosity:pd.DataFrame,out:Path):
    """Match slide 16: national share donut + a compact comparative table."""
    x=religiosity.set_index('Profile').reindex(['Secular','Traditional','Religious','Haredi'])
    fig=plt.figure(figsize=(15,6.1))
    ax1=fig.add_axes([.035,.22,.25,.62]);ax2=fig.add_axes([.31,.17,.67,.68]);ax2.axis('off')
    shares=[74,21,5];ax1.pie(shares,colors=[BLUE,ORANGE,'#9daab7'],startangle=90,
                          wedgeprops={'width':.32,'edgecolor':'white'})
    ax1.text(0,0,'9.5M\nResidents',ha='center',va='center',fontsize=13,fontweight='bold')
    ax1.set_title('2022 national population',fontsize=12,pad=10)
    ax1.legend(['Jewish: 74%','Arab: 21%','Other: 5%'],loc='lower center',bbox_to_anchor=(.5,-.25),frameon=False,ncol=1,fontsize=9)
    labels=[('Population (M)','Population',1e6,2),('Median local age','age_median',1,1),
      ('Avg. household size','size_avg',1,2),('Higher education (%)','AcadmCert_pcnt',1,0),
      ('Median annual local wages (k NIS)','employeesAnnual_medWage',1000,0)]
    cells=[]
    for label,key,div,prec in labels:
        values=[float(z)/div if pd.notna(z) else np.nan for z in x[key]]
        cells.append([label]+[f'{v:.{prec}f}' if np.isfinite(v) else '—' for v in values])
    tbl=ax2.table(cellText=cells,colLabels=['Measure','Secular','Traditional','Religious','Haredi'],
       loc='center',cellLoc='center',colLoc='center',colWidths=[.32,.17,.17,.17,.17])
    tbl.auto_set_font_size(False);tbl.set_fontsize(10);tbl.scale(1,2.2)
    for (r,c),cell in tbl.get_celld().items():
        cell.set_edgecolor('#e6e9ef')
        if r==0:cell.set_facecolor(NAVY);cell.get_text().set_color('white');cell.get_text().set_weight('bold')
        elif r%2==0:cell.set_facecolor('#f0f5f8')
    fig.suptitle('FOUR LOCALITY RELIGIOSITY PROFILES — CBS 2022',fontsize=16,fontweight='bold',y=.98)
    fig.text(.33,.045,'Locality-level measures, population-weighted; national population shares are individual CBS categories.',fontsize=9,color='#555')
    fig.savefig(out,dpi=190,bbox_inches='tight');plt.close(fig)
