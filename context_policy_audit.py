"""Controlled policy scenarios, NOT empirical linkage or document evaluation."""
import csv,json
from pathlib import Path
TYPES={'G1':['NAME','PHONE','EMAIL','DETAILED_ADDRESS','NATIONAL_ID','PASSPORT_ID','ACCOUNT_NUMBER','CARD_NUMBER'],'G2':['HEALTH_SENSITIVE','FREE_TEXT_SENSITIVE','DATE_OF_BIRTH','POSTAL_CODE'],'G3':['AGE','GENDER','NATIONALITY','ORGANIZATION','MARITAL_STATUS','OCCUPATION']}
SCENARIOS={
'approved_low_risk':dict(necessary=True,complete=True,linkage=False,rarity=False,exposure=False,conflict=False),
'not_necessary':dict(necessary=False,complete=True,linkage=False,rarity=False,exposure=False,conflict=False),
'adverse_linkage':dict(necessary=True,complete=True,linkage=True,rarity=False,exposure=False,conflict=False),
'adverse_rarity':dict(necessary=True,complete=True,linkage=False,rarity=True,exposure=False,conflict=False),
'adverse_exposure':dict(necessary=True,complete=True,linkage=False,rarity=False,exposure=True,conflict=False),
'incomplete_assessment':dict(necessary=True,complete=False,linkage=False,rarity=False,exposure=False,conflict=False),
'conflicting_assessment':dict(necessary=True,complete=True,linkage=False,rarity=False,exposure=False,conflict=True)}
def decide(group,context,s):
 if group=='G1':return 'MASK'
 if group=='G2' and context in ('C2','C3'):return 'MASK'
 if not s['necessary'] or not s['complete'] or s['conflict'] or any(s[k] for k in ('linkage','rarity','exposure')):return 'MASK'
 return 'PRESERVE'
def main():
 rows=[]
 for group,types in TYPES.items():
  for typ in types:
   for context in ('C1','C2','C3'):
    for name,s in SCENARIOS.items():
     action=decide(group,context,s)
     rows.append(dict(pii_type=typ,group=group,context=context,scenario=name,action=action,**s))
 # Invariants reflect manuscript protective overrides; no calibrated thresholds implied.
 assert len(rows)==378
 assert all(r['action']=='MASK' for r in rows if r['group']=='G1')
 assert all(r['action']=='MASK' for r in rows if r['group']=='G2' and r['context']!='C1')
 assert all(r['action']=='MASK' for r in rows if r['scenario']!='approved_low_risk')
 out=Path(__file__).parent/'context_results';out.mkdir(exist_ok=True)
 with (out/'decisions.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary=[]
 for g in TYPES:
  for c in ('C1','C2','C3'):
   selected=[r for r in rows if r['group']==g and r['context']==c]
   summary.append(dict(group=g,context=c,scenarios=len(selected),mask=sum(r['action']=='MASK' for r in selected),preserve=sum(r['action']=='PRESERVE' for r in selected)))
 (out/'summary.json').write_text(json.dumps({'cases':len(rows),'scope':'supplied scenario judgments; no real-world linkage, rarity, or utility evaluation','results':summary},indent=2))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
