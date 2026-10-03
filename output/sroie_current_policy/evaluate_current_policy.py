"""C2 current-policy coordinate audit; does not execute image rendering or inference."""
import argparse, csv, hashlib, json, zipfile
from pathlib import Path
import numpy as np

TYPE_GROUP = {'PERSON_NAME':'G1','PHONE':'G1','EMAIL':'G1','ADDRESS_FULL':'G1','PAYMENT_CARD':'G1','MEMBER_ID':'SUPPLEMENTAL_IDENTIFIER','TRANSACTION_ID':'SUPPLEMENTAL_IDENTIFIER'}

def area(b):
    return max(0,b[2]-b[0])*max(0,b[3]-b[1])

def union_area(boxes):
    xs=sorted({x for b in boxes for x in (b[0],b[2])})
    total=0
    for left,right in zip(xs,xs[1:]):
        intervals=sorted((b[1],b[3]) for b in boxes if b[0]<right and b[2]>left)
        end=-float('inf');length=0
        for lo,hi in intervals:
            length+=max(0,hi-max(lo,end));end=max(end,hi)
        total+=(right-left)*length
    return total

def write_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('--annotations',required=True);p.add_argument('--selection',required=True);p.add_argument('--out',required=True);args=p.parse_args()
    src=Path(args.annotations)
    with zipfile.ZipFile(src) as z:
        names=[n for n in z.namelist() if n.endswith('sroie_pii_full971.json')]
        if len(names)!=1:raise ValueError('Expected exactly one annotation JSON')
        docs=json.loads(z.read(names[0]))['documents']
    with open(args.selection,newline='',encoding='utf-8') as f:selected={r['document_id'] for r in csv.DictReader(f)}
    assert len(selected)==35
    docs=[d for d in docs if d['split']=='test'];assert len(docs)==350
    assert len({d['document_id'] for d in docs})==350
    assert selected <= {d['document_id'] for d in docs}
    records=[];entities=[];manifest=[]
    for d in docs:
        width,height=d['width'],d['height'];assert width>0 and height>0
        masks=[];es=d['pii_augmentation']['pii_entities']
        for e in es:
            typ=e['pii_type']
            if typ not in TYPE_GROUP:raise ValueError('Unspecified type: '+typ)
            b=e['box'];assert len(b)==4 and area(b)>0
            assert 0<=b[0]<b[2]<=width and 0<=b[1]<b[3]<=height
            masks.append(b)
        page=union_area(masks)/(width*height)
        records.append(dict(document_id=d['document_id'],original35=int(d['document_id'] in selected),entities=len(es),strong_coverage_sum=len(es),ra_coverage_sum=len(es),strong_page_area=page,ra_page_area=page))
        for e in es:
            b=e['box']
            intersections=[[max(b[0],m[0]),max(b[1],m[1]),min(b[2],m[2]),min(b[3],m[3])] for m in masks]
            cov=union_area([i for i in intersections if area(i)>0])/area(b)
            assert abs(cov-1)<1e-12
            entities.append(dict(document_id=d['document_id'],pii_id=e['pii_id'],pii_type=e['pii_type'],group=TYPE_GROUP[e['pii_type']],strong_coverage=cov,ra_coverage=cov))
            manifest.append(dict(document_id=d['document_id'],pii_id=e['pii_id'],pii_type=e['pii_type'],group=TYPE_GROUP[e['pii_type']],context='C2',strong_action='FULL_MASK',ra_action='FULL_MASK',box=b,margin_pixels=0,reason='mandatory G1 protection' if TYPE_GROUP[e['pii_type']]=='G1' else 'conservative supplemental-identifier rule; not an original 18-type assignment'))
    summaries=[]
    rng=np.random.default_rng(20261003)
    for label,rows in [('All350',records),('Original35',[r for r in records if r['original35']]),('Additional315',[r for r in records if not r['original35']])]:
        a=np.array([[r['entities'],r['strong_coverage_sum'],r['ra_coverage_sum']] for r in rows],float)
        boot=[]
        for _ in range(10000):
            s=a[rng.integers(0,len(a),len(a))].sum(axis=0)
            if s[0]>0:boot.append((s[2]-s[1])/s[0])
        mean_area=float(np.mean([r['strong_page_area'] for r in rows]))
        summaries.append(dict(group=label,documents=len(rows),positive_documents=sum(r['entities']>0 for r in rows),entities=int(a[:,0].sum()),strong_coverage=1.0,ra_coverage=1.0,difference=0.0,paired_ci95=np.quantile(boot,[.025,.975]).tolist(),strong_mean_page_area=mean_area,ra_mean_page_area=mean_area,relative_area_reduction=0.0))
    categories=[dict(pii_type=t,group=TYPE_GROUP[t],entities=sum(e['pii_type']==t for e in entities),strong_coverage=1.,ra_coverage=1.) for t in sorted({e['pii_type'] for e in entities})]
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'document_results.csv',records);write_csv(out/'entity_results.csv',entities);write_csv(out/'category_results.csv',categories)
    (out/'decision_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    report=dict(policy_version='CURRENT-C2-SPATIAL-1',scope='new coordinate-policy audit, not reproduction of Table 6; no images rendered, no OCR/detector/Donut run',context='C2',margin_pixels=0,rendering_spec='opaque black rectangles; specified but not executed',input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),seed=20261003,bootstrap_resamples=10000,type_mapping=TYPE_GROUP,summary=summaries,categories=categories,limitations=['No G2 or G3 entities in this sample','MEMBER_ID and TRANSACTION_ID are supplemental protective rules, not assignments from the original 18 types','Perfect overlap follows from using ground-truth boxes; it is not evidence of detection accuracy or resistance to re-identification','Equal masks make the zero paired difference structural; degenerate CI is not broader privacy assurance','Existing downstream scores cannot be attributed to these new masks'])
    (out/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
