import csv,numpy as np
from pathlib import Path
rows=list(csv.DictReader((Path(__file__).parent/'public_utility_scores.csv').open()))
assert len(rows)==700
pairs={}
for r in rows:
 k=(r['document_id'],r['condition']);assert k not in pairs
 v=sum(int(r['exact_'+f]) for f in ('company','date','address','total'))/4
 assert abs(v-float(r['field_exact']))<1e-12
 pairs[k]=v
ids=[r['document_id'] for r in rows if r['condition']=='ORIGINAL'];assert len(set(ids))==350
assert set(pairs)=={(i,c) for i in ids for c in ('ORIGINAL','MASKED_SHARED')}
a=np.array([pairs[i,'ORIGINAL'] for i in ids]);b=np.array([pairs[i,'MASKED_SHARED'] for i in ids]);d=b-a
rng=np.random.default_rng(20261003);boot=[d[rng.integers(0,len(d),len(d))].mean() for _ in range(10000)]
print('Original:',a.mean(),'Masked:',b.mean(),'Difference:',d.mean(),'CI95:',np.quantile(boot,[.025,.975]))
