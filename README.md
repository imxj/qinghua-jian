# 清华简 · 简影与识读

把清华简的公开照片、整理简号、通行字选读与白话解释放在一起的静态阅读网站。支持按篇目、简号或图片浏览，搜索文字与解释，放大原图，以及分享具体条目的链接。

- 网站：[imxj.github.io/qinghua-jian](https://imxj.github.io/qinghua-jian/)
- 阅读页：[reading.html](reading.html)
- 图片画廊：[gallery.html](gallery.html)
- 图片来源索引：[image-index.json](image-index.json)
- 识读数据：[annotations.json](annotations.json)
- 图片与文献出处说明：[ATTRIBUTION.md](ATTRIBUTION.md)

这是个人整理的阅读辅助项目，与清华大学及原出版、收藏机构没有官方隶属或认证关系。

## 收录范围与读法

本版整理日期为 **2026-10-01**：

| 项目 | 数量与含义 |
| --- | --- |
| 来源图片 | 135 张，全部附有说明；同一支简可能有全长照、局部或整组照片 |
| 图像文件 | 153 张，含另外渲染的 18 张 PDF 整页图版 |
| 篇目 | 21 种，《说命》上、中、下合计为一种 |
| 编号简记录 | 169 条，含尚未可靠释出的记录 |
| 来源辅助选读 | 155 条 |
| 暂定选读 | 9 条，保留异说与疑难字 |
| 尚未确释 | 5 条 |
| 仅图像或篇章层面的说明 | 8 张图片，暂未提供逐简释文 |

这些数字不是清华简全部馆藏数量，也不能把图片数当作互不重复的竹简数。当前资料来自公开展示图、发布报道、出版机构公开图录等，尚未覆盖全部整理报告与红外图版。

释读采用照片核对与已有出版释文、学者校读相结合的方法，白话说明由 AI 辅助整理，**未经古文字专家逐字审定**。阅读页分别标出采用的读法、图上观察、出处以及不确定之处；不是逐字 OCR 定本，也不是无缺口的全篇翻译。小图不够清晰、字形有争议或尚未获取可核验材料时，保留限制，不补造原文。

“……”表示选读中省去的文字，不自动表示原简残缺；跨简句子应按提示连读。历史叙述、占筮图式与古代宇宙观按文献解释，不直接等同于已确证的历史事实或现代科学结论。

## 本地阅读

下载或克隆仓库后，在仓库目录运行：

```bash
python3 -m http.server 8000
```

在浏览器打开 `http://localhost:8000/reading.html`。网站是纯静态 HTML、CSS 和 JavaScript，无需 Node.js、数据库、API 密钥或第三方前端依赖。生成后的页面内嵌索引数据，图片与 PDF 采用仓库相对路径；外部出处链接需要联网访问。

## 修改内容与重新构建

构建使用 Python 3 标准库：

```bash
python3 tools/build_reading.py
```

该命令同时生成画廊与阅读页，并校验图像 ID、简记录引用和本地图像文件。修改结构化内容后应运行此命令，不直接改生成页面内的数据。

| 路径 | 用途 |
| --- | --- |
| `annotations/*.json` | 分组维护的篇章、逐简识读和图片说明，是识读内容的编辑入口 |
| `sources/*.json` | 照片与图录来源元数据 |
| `photos/` | 来源图像和 PDF 图版渲染图 |
| `sources/qinghua-exhibition-2016-public.pdf` | 出版机构公开图录试读文件 |
| `tools/reading-template.html` | 阅读页模板 |
| `tools/gallery-template.html` | 画廊模板 |
| `tools/build_reading.py` | 合并、校验识读记录，调用画廊构建并生成阅读页 |
| `tools/build_gallery.py` | 整理图像索引并生成画廊 |
| `annotations.json`、`image-index.json` | 构建后的完整结构化数据 |

`tools/build_remaining_annotations.py` 是早期数据种子脚本，已有校对记录时会主动停止，以免覆盖人工修订；日常维护请直接编辑 `annotations/remaining.json`。

## GitHub Pages

站点可由 GitHub Pages 直接托管，无需后台服务。发布时需包含生成后的入口页面、`reading.html`、`gallery.html`、两份索引 JSON，以及 `photos/`、`sources/` 中页面引用的文件，并保持相对目录结构。

仓库使用 [`.github/workflows/pages.yml`](.github/workflows/pages.yml) 部署。在仓库的 **Settings → Pages → Build and deployment** 中选择 **GitHub Actions**；每次更新 `main` 分支，工作流运行：

```bash
python3 tools/build_site.py
```

该脚本重新构建画廊与阅读页，仅把选定的页面、数据 JSON、照片与公开图录 PDF 复制到 `_site/`，再由工作流上传并部署到 GitHub Pages。临时文件、本地压缩包与维护记录不作为网站内容发布。可在仓库 **Actions** 中检查构建与部署结果。

项目站点部署到 `/qinghua-jian/` 子路径，所有站内链接应使用相对路径。`_site/` 是生成目录，不作为内容的编辑入口。

## 纠错与来源

欢迎通过 GitHub Issue 提出具体的简号、字形、断句或来源问题。请尽量附上篇名、简号、图片 ID 和可回查的图版页码或学术文献；异读应保留出处与适用范围，避免把某一讨论意见改写为定论。

第三方照片、出版图版、PDF 和研究文献的权利归相应权利人；本仓库不为这些资产授予新的使用许可。详见 [ATTRIBUTION.md](ATTRIBUTION.md)。
