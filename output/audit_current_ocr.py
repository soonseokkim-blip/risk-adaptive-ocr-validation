import csv,io,json,os,re,subprocess,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

root=Path(__file__).parent;out=root/'current_ocr_audit';out.mkdir(exist_ok=True)
with zipfile.ZipFile(root.parent/'ocr_metadata/SROIE-PII-full971-metadata.zip') as z:
    docs=[d for d in json.loads(z.read('sroie_pii_full971.json'))['documents'] if d['split']=='test']
with zipfile.ZipFile(root/'sroie_current_policy/annotations_test350.zip') as z:
    coord={d['document_id']:d for d in json.loads(z.read('sroie_pii_full971.json'))['documents']}
jobs=[]
with zipfile.ZipFile(root.parent/'ocr_images/SROIE-PII-full971-images-test.zip') as orig,zipfile.ZipFile(root/'SROIE_Current_C2_Rendered350.zip') as masked:
    for d in docs:
        es=d['pii_augmentation']['pii_entities'];assert [e['box'] for e in es]==[e['box'] for e in coord[d['document_id']]['pii_augmentation']['pii_entities']]
        ims={'ORIGINAL':Image.open(io.BytesIO(orig.read(d['image_file']))).convert('RGB'),'MASKED_SHARED':Image.open(io.BytesIO(masked.read('shared_Strong_RA_C2/'+d['document_id']+'.png'))).convert('RGB')}
        for e in es:
            target=e['synthetic_text'].split(':',1)[-1]
            for condition,im in ims.items():
                x0,y0,x1,y1=e['box'];crop=im.crop((max(0,x0-5),max(0,y0-5),min(im.width,x1+5),min(im.height,y1+5)))
                scale=max(1,round(60/crop.height));crop=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.BICUBIC)
                buf=io.BytesIO();crop.save(buf,format='PNG')
                jobs.append((d['document_id'],e['pii_id'],e['pii_type'],condition,target,buf.getvalue()))
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
def run(job):
    did,pid,typ,condition,target,data=job
    env=dict(os.environ,OMP_THREAD_LIMIT='1')
    r=subprocess.run(['tesseract','stdin','stdout','-l','eng','--psm','7'],input=data,capture_output=True,env=env,timeout=60)
    if r.returncode:raise RuntimeError(r.stderr.decode())
    text=r.stdout.decode();nt=norm(target);assert nt
    return dict(document_id=did,pii_id=pid,pii_type=typ,condition=condition,target=target,ocr_text=text.strip(),complete_value_recovered=int(nt in norm(text)))
rows=[]
with ThreadPoolExecutor(max_workers=6) as pool:
    for i,r in enumerate(pool.map(run,jobs),1):
        rows.append(r)
        if i%200==0:print('OCR regions completed',i,'/',len(jobs),flush=True)
with (out/'entity_ocr_results.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
lookup={(r['pii_id'],r['condition']):r for r in rows};summary=[]
for typ in sorted({r['pii_type'] for r in rows})+['TOTAL']:
    es=[r for r in rows if r['condition']=='ORIGINAL' and (typ=='TOTAL' or r['pii_type']==typ)]
    summary.append(dict(pii_type=typ,entities=len(es),original_recovered=sum(r['complete_value_recovered'] for r in es),masked_recovered=sum(lookup[(r['pii_id'],'MASKED_SHARED')]['complete_value_recovered'] for r in es),masked_recovered_among_original_recoverable=sum(lookup[(r['pii_id'],'MASKED_SHARED')]['complete_value_recovered'] for r in es if r['complete_value_recovered'])))
report=dict(documents=350,entities=846,negative_controls=sum(not d['pii_augmentation']['pii_entities'] for d in docs),tesseract_version='5.3.4',language='eng',psm=7,crop_border=5,scale='max(1, round(60/crop_height))',normalization='lowercase ASCII alphanumeric',recovery='complete normalized target is substring of OCR output',shared_masked_condition='Strong and RA identical; one OCR pass per entity represents both',summary=summary,limitations=['No partial-value, human-reader, alternative-OCR or re-identification attack evaluated','Known annotation coordinates; not end-to-end detection','No independence-based entity significance claim','Results apply only to newly rendered zero-margin policy'])
(out/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
