import json, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

# The printed number range includes two missing slips; preserve the actual photographed set.
for path in ['sources/exhibition-photo-manifest.json','sources/pdf-gallery-entries.json']:
 p=ROOT/path
 d=json.loads(p.read_text())
 def walk(x):
  if isinstance(x,dict):
   if x.get('manuscript')=='封许之命' and x.get('slip_range')==[1,9]:
    x.update(slip_numbers=[2,3,5,6,7,8,9],title='《封许之命》· 实存七简（2、3、5—9）')
    for k in ['photo_scope','scope']:
     if k in x:x[k]='实际展示简2、3、5、6、7、8、9；编号1、4为空缺。'
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(d)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
exec(compile((ROOT/'tools/build_gallery.py').read_text(),'build_gallery.py','exec'))
catalog=json.loads((ROOT/'image-index.json').read_text())
merged=dict(manuscripts=[],slips=[],images=[])
for name in ['early','poetry','numerical','remaining']:
 d=json.loads((ROOT/f'annotations/{name}.json').read_text())
 for field in merged:merged[field]+=d[field]
for field,key in [('manuscripts','name'),('slips','key'),('images','id')]:
 vals=[r[key] for r in merged[field]]
 assert len(set(vals))==len(vals),(field,'duplicate ids')
slips={s['key']:s for s in merged['slips']}
notes={s['id']:s for s in merged['images']}
originals={r['id']:r for r in catalog['original_images']}
assert set(originals)<=set(notes),set(originals)-set(notes)
allimages={**originals,**{r['id']:r for r in catalog['images']}}
for id,row in allimages.items():
 if id not in notes:
  related=[r for r in catalog['original_images'] if r.get('pdf_page')==row.get('pdf_page') and r['manuscript']==row['manuscript']]
  assert related,(id,'no supporting image annotations')
  keys=list(dict.fromkeys(k for r in related for k in notes[r['id']]['slip_keys']))
  note=dict(id=id,slip_keys=keys,observation='出版社整页图版，保留原有排列、编号和局部图。对应下列来源图像的识读记录：'+ '、'.join(r['id'] for r in related),status='同页原图识读的汇总',limitations=['整页中的放大段与整简可能重复；不重复计为独立竹简。'])
  notes[id]=note
for id,note in notes.items():
 assert id in allimages,(id,'unknown image')
 assert set(note['slip_keys'])<=set(slips),(id,'unknown slip')
merged['images']=[{**row,**notes[id],'is_original':id in originals} for id,row in allimages.items()]
for row in merged['images']:
 if row['manuscript']=='封许之命' and row.get('slip_range')==[1,9]:
  row['title']='《封许之命》· 实存七简（2、3、5—9）'
 for key in ['local_path']:assert (ROOT/row[key]).is_file(),row[key]
for s in merged['slips']:
 s['quality']='pending' if s['manuscript']=='胥马' or s['key']=='两中-002' else 'tentative' if s['manuscript']=='五纪' else 'assisted'
 for key in ['reading','reading_basis','visual_observation','explanation','terms','uncertainties','sources']:assert key in s,(s['key'],key)
 assert any(s['key'] in i['slip_keys'] for i in merged['images']),(s['key'],'no image')
for x in merged['manuscripts']+merged['slips']:
 for src in x['sources']:
  if '071131-01.pdf' in src['url'] and '公开试读' in src['label']:
   src['label']='清华大学出版社公开图录'+('，第'+str(src['page'])+'页' if src.get('page') else '')
merged['scope']='135张已收集的来源图像均已尝试识读或说明限制；不是清华简全部馆藏，也不是逐字定本。'
merged['method']='先核对图片和简号，再参照出版释文、学者校读解释。通行字、标点与白话释义是阅读辅助；不得误认为原简逐字OCR。'
merged['notation']='……表示选读中省去的文字；〔〕为解释或未确释提示；□的含义以本条说明为准，可能是缺损字，也可能是本次未定字。跨简的句子须连读。'
merged['date']='2026-10-01'
merged['stats']={'source_images':len(originals),'all_images':len(merged['images']),'slip_attempts':len(slips),'manuscripts':len(merged['manuscripts']),'quality':dict(collections.Counter(s['quality'] for s in merged['slips'])),'image_only':sum(not notes[id]['slip_keys'] for id in originals)}
(ROOT/'annotations.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2))
payload=json.dumps(merged,ensure_ascii=False).replace('</','<\\/')
(ROOT/'reading.html').write_text((ROOT/'tools/reading-template.html').read_text().replace('/*ANNOTATION_DATA*/',payload))
print(json.dumps(merged['stats'],ensure_ascii=False,indent=2))
