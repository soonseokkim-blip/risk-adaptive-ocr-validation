import csv,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

root=Path(__file__).parent
source=root.parent/'ocr_images/SROIE-PII-full971-images-test.zip'
policy=root/'sroie_current_policy'
with zipfile.ZipFile(policy/'annotations_test350.zip') as z:
    docs=json.loads(z.read('sroie_pii_full971.json'))['documents']
rows=[]
target=root/'SROIE_Current_C2_Rendered350.zip'
with zipfile.ZipFile(source) as zin,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as zout:
    members={Path(n).stem:n for n in zin.namelist() if n.lower().endswith(('.jpg','.png','.jpeg'))}
    for d in docs:
        member=members[d['document_id']]
        im=Image.open(io.BytesIO(zin.read(member))).convert('RGB')
        assert im.size==(d['width'],d['height'])
        original=np.asarray(im).copy(); mask=np.zeros((d['height'],d['width']),bool)
        for e in d['pii_augmentation']['pii_entities']:
            x0,y0,x1,y1=e['box'];mask[y0:y1,x0:x1]=True
        expected=original.copy();expected[mask]=0
        result=Image.fromarray(expected)
        data=io.BytesIO();result.save(data,format='PNG');png=data.getvalue()
        actual=np.asarray(Image.open(io.BytesIO(png)).convert('RGB'))
        assert np.array_equal(actual[~mask],original[~mask])
        assert np.all(actual[mask]==0)
        zout.writestr('shared_Strong_RA_C2/'+d['document_id']+'.png',png)
        rows.append(dict(document_id=d['document_id'],entities=len(d['pii_augmentation']['pii_entities']),masked_pixels=int(mask.sum()),page_pixels=mask.size,page_area=mask.mean(),all_selected_pixels_black=True,all_outside_pixels_unchanged=True,png_sha256=hashlib.sha256(png).hexdigest()))
    buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);zout.writestr('pixel_audit.csv',buf.getvalue())
    report=dict(documents=len(rows),entities=sum(r['entities'] for r in rows),positive_documents=sum(r['entities']>0 for r in rows),mean_page_area=float(np.mean([r['page_area'] for r in rows])),strong_ra_images_identical_by_design=True,opaque_black_mask=True,margin_pixels=0,coordinate_convention='half-open',source_archive_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),ocr_recovery_executed=False,donut_inference_executed=False)
    assert len(rows)==350 and report['entities']==846
    expected_report=json.loads((policy/'results/results.json').read_text())
    assert abs(report['mean_page_area']-expected_report['summary'][0]['strong_mean_page_area'])<1e-12
    zout.writestr('render_audit.json',json.dumps(report,indent=2))
    zout.writestr('render_sroie_current.py',Path(__file__).read_text())
    zout.writestr('README.md','# SROIE current C2 rendered images\n\n350 lossless PNGs. The same image is used for Strong and Risk-adaptive because decisions and zero margins are identical. All 846 annotation boxes are black; all pixels outside their union are unchanged relative to the decoded input. No OCR or Donut inference was performed. This is a new experiment, not reproduction of historical Table 6. See the separately provided current-policy coordinate audit for mapping decisions. Do not attribute historical utility scores to these new images.\n')
print(json.dumps(report,indent=2));print('Archive bytes',target.stat().st_size)
