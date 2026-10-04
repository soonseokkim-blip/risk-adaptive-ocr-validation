import json, pathlib, collections, numpy as np
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'regenerated';OUT.mkdir(exist_ok=True)
rows=json.load(open(ROOT/'classifications.json'))
names={r['genre']:r['genre'] for r in rows}
def summ(rs):
 d=np.array([r['delta_anls'] for r in rs]); clusters=collections.defaultdict(list)
 for r in rs:clusters[r['source_id']].append(r['delta_anls'])
 cs=list(clusters.values());rng=np.random.default_rng(20261003);boot=[]
 for _ in range(10000):
  picked=rng.integers(0,len(cs),len(cs));boot.append(np.mean([v for k in picked for v in cs[k]]))
 return dict(n=len(rs),sources=len(cs),baseline_anls=np.mean([r['baseline_anls'] for r in rs]),masked_anls=np.mean([r['masked_anls'] for r in rs]),delta_anls=d.mean(),ci_low=np.quantile(boot,.025),ci_high=np.quantile(boot,.975),baseline_em=sum(r['baseline_em'] for r in rs)/len(rs),masked_em=sum(r['masked_em'] for r in rs)/len(rs))
out={'overall':summ(rows)}
for field in ['answer_category','genre']:
 out[field]={k:summ([r for r in rows if r[field]==k]) for k in dict.fromkeys(r[field] for r in rows)}
out['genre_high_confidence']={k:summ([r for r in rows if r['genre']==k and r['genre_confidence']=='high']) for k in names.values() if any(r['genre']==k and r['genre_confidence']=='high' for r in rows)}
json.dump(out,open(OUT/'category_genre_results.json','w'),indent=2)
for field in ['answer_category','genre']:
 print('\n'+field)
 for k,s in out[field].items():print(k,s['n'],*(round(s[x],4) for x in ['baseline_anls','masked_anls','delta_anls','ci_low','ci_high']))
print('overall',out['overall'])
# Recalculate Table 14 question-type point estimates and cluster intervals.
import csv
paired=list(csv.DictReader(open(ROOT/'paired_scores.csv')))
qr=[]
for r in paired:
 qr.append(dict(source_id=r['source_document_id'],question_types=r['question_types'],role=r['role'],baseline_anls=float(r['BASELINE_AUGMENTED']),masked_anls=float(r['ANSWER_MASKED']),delta_anls=float(r['ANSWER_MASKED'])-float(r['BASELINE_AUGMENTED']),baseline_em=float(r['BASELINE_AUGMENTED_EM']),masked_em=float(r['ANSWER_MASKED_EM'])))
qt={k for r in qr for k in r['question_types'].split('|') if k}
json.dump({'overall':summ(qr),'question_types':{k:summ([r for r in qr if k in r['question_types'].split('|')]) for k in sorted(qt)}},open(OUT/'answer_ablation_results.json','w'),indent=2)
