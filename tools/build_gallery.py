import json, pathlib, shutil, hashlib, collections, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

def read(path):
    p=pathlib.Path(path)
    return json.loads(p.read_text()) if p.exists() else []

def localize(row):
    p=pathlib.Path(row['local_path'])
    if p.is_absolute():
        if ROOT not in p.parents:
            target=ROOT/'photos'/p.name
            shutil.copy2(p,target)
            p=target
        row['local_path']=str(p.relative_to(ROOT))
    row['bytes']=(ROOT/row['local_path']).stat().st_size
    row['sha256']=hashlib.sha256((ROOT/row['local_path']).read_bytes()).hexdigest()
    return row

rows=[]
for r in read(ROOT/'sources/museum-photos.json')+read(ROOT/'sources/fudan-photos.json'):
    r['manuscript']=r['title'].replace('局部','')
    r['kind']='overview'
    r['group']='馆方与高校'
    rows.append(localize(r))
for n,r in enumerate(read(ROOT/'sources/qinghua-publisher-photos.json'),1):
    r.update(id=f'publisher-{n:02}',image_url=r['url'],source_name=r['source'],kind='plate',group='出版社选页')
    r['volume']=1 if r['manuscript'] in ['保训','楚居'] else 3
    rows.append(localize(r))
for n,r in enumerate(read(ROOT/'sources/qinghua-official-samples.json'),1):
    r.update(id=f'release-{n:02}',manuscript=r['title'],source_name=r.get('source_name','清华大学／出土文献中心'),kind='overview',group='后续辑公开照片')
    if r['volume']==11:r.update(manuscript='五纪',source_name='北京日报',title='五纪 · 9支选简')
    if r['volume']==14:r.update(manuscript='两中',source_name='文汇报（清华大学供图）',title='两中 · 简1—2样张')
    if r['volume']==15:r.update(manuscript='胥马',source_name='上观新闻（贾连翔署名文章）',title='胥马 · 简28—31')
    if r['title']=='摄命':r['scope']='正面总览及放大局部；网页尺寸较小。'
    elif r['title']=='成人':r['scope']='正面展示图；未核定是否覆盖该篇全部简。'
    elif r['title']=='五音图':r['scope']='正面展示图；保留残断及缺失部位。'
    rows.append(localize(r))
for n,r in enumerate(read(ROOT/'sources/qinghua-extra-photos.json'),1):
    r.setdefault('id',f'extra-{n:02}')
    r.setdefault('image_url',r.get('url',''))
    r.setdefault('source_name',r.get('source','网络转载'))
    r.setdefault('manuscript',r['title'])
    r.setdefault('kind','overview')
    r.setdefault('group','补充转载图')
    r.setdefault('volume',4)
    rows.append(localize(r))

# PDF entries are normalized in a separate small preparation step after extraction.
for r in read(ROOT/'sources/pdf-gallery-entries.json'):
    rows.append(localize(r))

seen=set(); unique=[]
for row in rows:
    if row['sha256'] in seen:continue
    seen.add(row['sha256']);unique.append(row)
rows=sorted(unique,key=lambda r:(r.get('volume') or 99,r['manuscript'],r['group'],r['id']))
for row in rows:
    if row['manuscript'].startswith('说命'):row['manuscript']='说命'
    row.setdefault('image_url','')
    row.setdefault('scope','照片／图版选录，未认定全篇覆盖。')
    row.setdefault('source_name','清华大学出版社')
    row.setdefault('kind','plate')

resources=[
  {'title':'完整整理报告电子书平台','url':'https://qhj.cihai.com.cn/','scope':'按册授权访问原大图版、放大图版、释文注释；需按册授权激活。','access':'需授权'},
  {'title':'官方电子书使用帮助','url':'https://qhj.cihai.com.cn/help','scope':'纸书版权页二维码按册激活；手机验证码登录。可按篇名及简号定位图版。','access':'公开'},
  {'title':'《竹简上的经典——清华简文献展》公开试读','url':'https://www.tup.tsinghua.edu.cn/upload/books/yz/071131-01.pdf','local_path':'sources/qinghua-exhibition-2016-public.pdf','scope':'80页公开试读，2016年资料；不是清华简全部图版。','access':'公开'},
  {'title':'清华艺博8组简影','url':'https://www.artmuseum.tsinghua.edu.cn/cpsj/zlxx/zlhg/201710/t20171023_2758.shtml','scope':'部分作品展示，网页分辨率有限。','access':'公开'},
  {'title':'上海书画出版社《楚简名品》线上展览','url':'https://www.sohu.com/a/374325442_369578','scope':'其中清华简部分12张选页；已排除同文中的其他藏简。','access':'公开'},
  {'title':'第十五辑官方发布公告','url':'https://www.ctwx.tsinghua.edu.cn/info/1011/3465.htm','scope':'2026-01-19发布第十五辑；公告称最后一辑仍待公布。','access':'公开'},
  {'title':'《校释》红外图版说明','url':'https://www.tsinghua.edu.cn/info/1182/115674.htm','scope':'《校释》各卷附红外图版；本次未取得全套红外图版。','access':'说明公开，图版另见书籍'},
  {'title':'最初的检索线索（知乎）','url':'https://zhuanlan.zhihu.com/p/60496118','scope':'本次访问返回403，无法核对文章图片清单。','access':'本次未读取成功'}
]
original_rows=[r for r in rows if r['group']!='出版社PDF图版']
pdf=read(ROOT/'sources/exhibition-photo-manifest.json')
if pdf:
    for r in pdf['original_photos']:
        r=dict(r)
        r['volume']={'壹':1,'贰':2,'叁':3,'肆':4,'伍':5,'陆':6,'陸':6}.get(r['volume'],r['volume'])
        r['kind']=r['image_kind'];r['scope']=r['photo_scope'];r['group']='出版社PDF原始图像';r['source_name']='清华大学出版社（PDF嵌入原图）';r['image_url']=''
        if r['manuscript'].startswith('说命'):r['manuscript']='说命'
        original_rows.append(localize(r))
original_rows=sorted(original_rows,key=lambda r:(r.get('volume') or 99,r['manuscript'],r['id']))
manifest={'collected_on':'2026-10-01','scope':'本次核实可公开获取的清华简照片和图版选集。不是清华简馆藏全集，也不是互不重复的竹简计数。','image_count':len(rows),'original_image_count':len(original_rows),'images':rows,'original_images':original_rows,'resources':resources}
(ROOT/'image-index.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
template=ROOT.joinpath('tools/gallery-template.html').read_text()
data=json.dumps(manifest,ensure_ascii=False).replace('</','<\\/')
(ROOT/'gallery.html').write_text(template.replace('/*PHOTO_DATA*/',data))
print(json.dumps({'gallery_entries':len(rows),'manuscripts':sorted(set(r['manuscript'] for r in rows)),'groups':dict(collections.Counter(r['group'] for r in rows))},ensure_ascii=False,indent=2))
