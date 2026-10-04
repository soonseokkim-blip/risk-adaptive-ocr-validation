import pathlib, os, pandas as pd, numpy as np, json
ROOT=pathlib.Path(__file__).resolve().parent
os.chdir(ROOT)
OUT=ROOT/'regenerated';OUT.mkdir(exist_ok=True)
fields=['company','date','address','total']
document_order=[r['document_id'] for r in json.load(open(ROOT/'source_validation.json'))['checks']]
df=pd.read_csv(ROOT/'source_control_scores.csv')
summary=df.groupby('condition')['field_exact'].agg(['mean','count']);summary.to_csv(OUT/'summary.csv')
piv=df.pivot(index='document_id',columns='condition',values='field_exact').reindex(document_order)
comparisons=[]
for a,b,label in [('SOURCE_UNAUGMENTED','AUGMENTED_UNMASKED','insertion_effect'),('AUGMENTED_UNMASKED','MASKED_SHARED','masking_effect'),('SOURCE_UNAUGMENTED','MASKED_SHARED','net_effect')]:
 delta=(piv[b]-piv[a]).to_numpy();rng=np.random.default_rng(20261003)
 boot=np.array([rng.choice(delta,len(delta),replace=True).mean() for _ in range(10000)])
 lo,hi=np.quantile(boot,[.025,.975])
 comparisons.append({'comparison':label,'reference':a,'evaluated':b,'difference':float(delta.mean()),'ci95_low':float(lo),'ci95_high':float(hi)})
pd.DataFrame(comparisons).to_csv(OUT/'comparisons.csv',index=False)

df=pd.read_csv(ROOT/'field_ablation_scores.csv')
base=df[df.condition=='SOURCE_UNAUGMENTED'].set_index('document_id')
results=[]
for f in fields:
 masked=df[df.condition=='MASK_'+f].set_index('document_id')
 n=len(masked)
 if not n:continue
 ref=base.loc[masked.index]
 for outcome in ['target_field','other_fields','overall']:
  cols=['exact_'+f] if outcome=='target_field' else (['exact_'+x for x in fields if x!=f] if outcome=='other_fields' else ['exact_'+x for x in fields])
  a=ref[cols].astype(float).mean(axis=1).to_numpy();b=masked[cols].astype(float).mean(axis=1).to_numpy();delta=b-a
  rng=np.random.default_rng(20261003);boot=[rng.choice(delta,n,replace=True).mean() for _ in range(10000)];lo,hi=np.quantile(boot,[.025,.975])
  results.append(dict(masked_field=f,outcome=outcome,documents=n,baseline=float(a.mean()),masked=float(b.mean()),difference=float(delta.mean()),ci95_low=float(lo),ci95_high=float(hi)))
pd.DataFrame(results).to_csv(OUT/'ablation_summary.csv',index=False)

print('Regenerated Tables 12–13 aggregates in regenerated/.')
