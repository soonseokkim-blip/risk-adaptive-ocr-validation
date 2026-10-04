import json, pathlib, numpy as np, csv
ROOT=pathlib.Path(__file__).resolve().parent
source=json.load(open(ROOT/'coordinates_35.json'))
def area(rects):
 xs=sorted({x for b in rects for x in (b[0],b[2])});a=0
 for l,r in zip(xs,xs[1:]):
  ys=sorted((b[1],b[3]) for b in rects if b[0]<r and b[2]>l);end=None;h=0
  for lo,hi in ys:
   if end is None or lo>end:h+=hi-lo;end=hi
   elif hi>end:h+=hi-end;end=hi
  a+=(r-l)*h
 return a
rows=[];pages=[]
for d in source:
 masks=[[e['box'] for e in d[k] if e['action']!='RETAIN'] for k in ['strong','risk_adaptive_c2']]
 pages.append({'id':d['document_id'],'n':len(d['entities']),'strong_area':area(masks[0])/(d['width']*d['height']),'ra_area':area(masks[1])/(d['width']*d['height'])})
 for e in d['entities']:
  b=e['box'];scores=[]
  for boxes in masks:
   ints=[[max(b[0],c[0]),max(b[1],c[1]),min(b[2],c[2]),min(b[3],c[3])] for c in boxes];ints=[c for c in ints if c[2]>c[0] and c[3]>c[1]]
   scores.append(area(ints)/((b[2]-b[0])*(b[3]-b[1])))
  rows.append(dict(document_id=d['document_id'],pii_id=e['pii_id'],pii_type=e['pii_type'],priority=e['field_protection_priority'],strong=scores[0],risk_adaptive=scores[1],delta=scores[1]-scores[0],ra_action=next(x['action'] for x in d['risk_adaptive_c2'] if x['pii_id']==e['pii_id'])))
ids=[d['document_id'] for d in source]
rng=np.random.default_rng(20261004);draw=rng.integers(0,35,(20000,35));counts=np.stack([(draw==i).sum(axis=1) for i in range(35)],axis=1)
def summary(rs):
 ns=np.array([sum(r['document_id']==i for r in rs) for i in ids]);ds=np.array([sum(r['delta'] for r in rs if r['document_id']==i) for i in ids]);den=counts@ns;valid=den>0;boots=(counts@ds)[valid]/den[valid]
 return dict(entities=len(rs),documents=int((ns>0).sum()),strong=float(np.mean([r['strong'] for r in rs])),risk_adaptive=float(np.mean([r['risk_adaptive'] for r in rs])),difference=float(np.mean([r['delta'] for r in rs])),ci=list(map(float,np.quantile(boots,[.025,.975]))),incomplete_entities=sum(r['risk_adaptive']<1-1e-12 for r in rs),incomplete_documents=len({r['document_id'] for r in rs if r['risk_adaptive']<1-1e-12}))
res={'overall':summary(rows),'by_type':{k:summary([r for r in rows if r['pii_type']==k]) for k in sorted({r['pii_type'] for r in rows})},'by_priority':{k:summary([r for r in rows if r['priority']==k]) for k in sorted({r['priority'] for r in rows})}}
res['area']={'strong':float(np.mean([p['strong_area'] for p in pages])),'risk_adaptive':float(np.mean([p['ra_area'] for p in pages]))};res['area']['relative_reduction']=1-res['area']['risk_adaptive']/res['area']['strong']
json.dump(res,open(ROOT/'results.json','w'),indent=2)
print(json.dumps(res,indent=2))
