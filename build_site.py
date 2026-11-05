# -*- coding: utf-8 -*-
"""把 manuscript/ 全部章节转成带侧边目录的在线阅读站（单页应用，输出 docs/index.html）。"""
import os
import re
import sys
import markdown as md

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "docs")
os.makedirs(OUT, exist_ok=True)

BOOK_TITLE = "AI时代大学生的生存指南"
BOOK_SUB = "从使用工具到成为AI时代的创造者"

# 阅读顺序（文件名 → 目录显示名）
ORDER = [
    ("manuscript/00-前言.md", "前言"),
    ("manuscript/01-范式转移.md", "第一章 · 范式转移"),
    ("manuscript/02-认知重构.md", "第二章 · 认知重构"),
    ("manuscript/03-提问的艺术.md", "第三章 · 提问的艺术"),
    ("manuscript/04-学习革命.md", "第四章 · 学习革命"),
    ("manuscript/05-专业深耕.md", "第五章 · 专业深耕"),
    ("manuscript/06-创作与产出.md", "第六章 · 创作与产出"),
    ("manuscript/07-学术规范.md", "第七章 · 学术规范"),
    ("manuscript/08-职业竞争力.md", "第八章 · 职业竞争力"),
    ("manuscript/09-生活心理边界.md", "第九章 · 生活、心理与边界感"),
    ("manuscript/10-伦理与未来.md", "第十章 · 伦理与未来"),
    ("manuscript/11-后记.md", "后记"),
    ("manuscript/appendix/A-工具速查表.md", "附录A · 工具速查表"),
    ("manuscript/appendix/B-提示词模板库.md", "附录B · 提示词模板库"),
    ("manuscript/appendix/C-高校AI政策查询指南.md", "附录C · 高校AI政策查询指南"),
    ("manuscript/appendix/D-延伸阅读.md", "附录D · 延伸阅读"),
    ("manuscript/appendix/E-术语词典.md", "附录E · 术语词典"),
]

def strip_trailing_note(text):
    """去掉文末的斜体扩写说明（*（初稿……）*），阅读站只展示正文。"""
    return re.sub(r"\n\*（[^*]{10,400}）\*\s*$", "\n", text)

def clean_md(text):
    text = re.sub(r"^#.*\n", "", text, count=1)  # 首行章标题由页面框架渲染
    return text

def main():
    chapters = []
    total_chars = 0
    for i, (rel, label) in enumerate(ORDER):
        path = os.path.join(BASE, rel)
        raw = open(path, encoding="utf-8").read()
        raw = strip_trailing_note(raw)
        total_chars += len(re.findall(r"[\u4e00-\u9fff]", raw))
        body = md.markdown(clean_md(raw), extensions=["tables", "toc", "sane_lists"])
        # 小标题加锚点 id（markdown toc 已处理 h1/h2，这里确保 h2 有 id）
        chapters.append({"label": label, "body": body})

    toc_items = "\n".join(
        f'<a class="toc-item" data-ch="{i}" href="javascript:void(0)">{c["label"]}</a>'
        for i, c in enumerate(chapters)
    )
    chapter_divs = "\n".join(
        f'<article class="chapter" id="ch{i}" hidden><div class="ch-label">{c["label"]}</div>{c["body"]}'
        f'<div class="ch-nav"><a class="prev" data-go="{i-1}" href="javascript:void(0)">← 上一章</a>'
        f'<a class="next" data-go="{i+1}" href="javascript:void(0)">下一章 →</a></div></article>'
        for i, c in enumerate(chapters)
    )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{BOOK_TITLE}：{BOOK_SUB}</title>
<style>
  :root {{
    --bg:#FFFDF8; --paper:#fff; --ink:#2c2620; --sub:#8a7f72;
    --red:#C0392B; --gold:#D4A574; --line:#ece4d8;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  html {{ scroll-behavior:smooth; }}
  body {{ background:var(--bg); color:var(--ink);
    font-family:"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",serif;
    line-height:2; }}
  a {{ color:var(--red); text-decoration:none; }}

  /* ---- 顶栏 ---- */
  header.top {{ position:sticky; top:0; z-index:20; background:rgba(255,253,248,.96);
    border-bottom:1px solid var(--line); backdrop-filter:blur(6px); }}
  .top-inner {{ max-width:1200px; margin:0 auto; padding:12px 20px;
    display:flex; align-items:baseline; gap:14px; }}
  .top-inner .book {{ font-weight:700; font-size:17px; letter-spacing:1px; }}
  .top-inner .sub {{ font-size:12.5px; color:var(--sub); }}
  .top-inner .menu-btn {{ margin-left:auto; display:none; border:1px solid var(--line);
    background:none; border-radius:6px; padding:4px 10px; cursor:pointer; color:var(--sub); font-size:13px; }}

  .layout {{ max-width:1200px; margin:0 auto; display:flex; gap:0; align-items:flex-start; }}

  /* ---- 侧边目录 ---- */
  nav#toc {{ width:264px; flex:none; position:sticky; top:57px; align-self:flex-start;
    max-height:calc(100vh - 70px); overflow-y:auto; padding:26px 18px 40px 20px; }}
  nav#toc .toc-title {{ font-size:12px; color:var(--sub); letter-spacing:3px; margin-bottom:14px; }}
  .toc-item {{ display:block; padding:7px 10px; margin:1px 0; font-size:14px; color:#5c5348;
    border-left:2px solid transparent; border-radius:0 6px 6px 0; line-height:1.5; }}
  .toc-item:hover {{ background:#f6efe3; }}
  .toc-item.active {{ color:var(--red); border-left-color:var(--red); background:#faf3e6; font-weight:600; }}
  nav#toc .stats {{ margin-top:22px; font-size:12px; color:var(--sub); line-height:1.8;
    border-top:1px dashed var(--line); padding-top:14px; }}

  /* ---- 正文 ---- */
  main {{ flex:1; min-width:0; padding:40px 44px 120px; }}
  article.chapter {{ max-width:760px; margin:0 auto; background:var(--paper);
    border:1px solid var(--line); border-radius:10px; padding:52px 58px 46px;
    box-shadow:0 2px 14px rgba(120,90,40,.05); }}
  .ch-label {{ font-size:12.5px; color:var(--gold); letter-spacing:2px; margin-bottom:6px; }}
  article.chapter h1 {{ font-size:26px; line-height:1.5; margin:4px 0 8px;
    padding-bottom:14px; border-bottom:2px solid var(--ink); }}
  article.chapter h2 {{ font-size:19px; margin:38px 0 12px; padding-left:12px;
    border-left:4px solid var(--red); line-height:1.6; }}
  article.chapter h3 {{ font-size:16.5px; margin:26px 0 8px; }}
  article.chapter p {{ margin:12px 0; font-size:16px; text-align:justify; }}
  article.chapter li {{ margin:8px 0; font-size:15.5px; }}
  article.chapter ul, article.chapter ol {{ padding-left:1.8em; margin:10px 0; }}
  article.chapter blockquote {{ margin:18px 0; padding:10px 18px; background:#faf6ee;
    border-left:3px solid var(--gold); color:#5c5348; }}
  article.chapter code {{ font-family:Consolas,monospace; font-size:.88em; background:#f4efe6;
    padding:1px 6px; border-radius:4px; }}
  article.chapter pre {{ background:#2c2620; color:#f2ead9; padding:16px 18px; border-radius:8px;
    overflow-x:auto; margin:16px 0; }}
  article.chapter pre code {{ background:none; color:inherit; padding:0; }}
  article.chapter table {{ border-collapse:collapse; width:100%; margin:18px 0; font-size:14px; }}
  article.chapter th, article.chapter td {{ border:1px solid var(--line); padding:8px 12px;
    text-align:left; line-height:1.7; }}
  article.chapter th {{ background:#f8f2e6; }}
  article.chapter hr {{ border:none; border-top:1px dashed var(--line); margin:30px 0; }}
  .ch-nav {{ margin-top:56px; padding-top:20px; border-top:1px solid var(--line);
    display:flex; justify-content:space-between; }}
  .ch-nav a {{ font-size:14px; }}
  .ch-nav a.prev[data-go="-1"], .ch-nav a.next[data-go="17"] {{ visibility:hidden; }}

  /* ---- 封面 ---- */
  #cover {{ max-width:760px; margin:0 auto; text-align:center; padding:90px 30px 70px; }}
  #cover h1 {{ font-size:34px; letter-spacing:4px; line-height:1.6; }}
  #cover .rule {{ width:64px; height:3px; background:var(--red); margin:26px auto; }}
  #cover .sub {{ font-size:17px; color:#5c5348; letter-spacing:2px; }}
  #cover .meta {{ margin-top:44px; font-size:13px; color:var(--sub); line-height:2.1; }}
  #cover .btn {{ display:inline-block; margin-top:40px; background:var(--red); color:#fff;
    padding:11px 38px; border-radius:999px; font-size:15px; letter-spacing:2px; }}
  #cover .btn:hover {{ background:#a93226; }}

  footer {{ text-align:center; padding:30px; font-size:12px; color:var(--sub); }}

  /* ---- 移动端 ---- */
  @media (max-width:860px) {{
    .top-inner .menu-btn {{ display:block; }}
    nav#toc {{ position:fixed; left:0; top:0; bottom:0; background:var(--paper); z-index:30;
      width:270px; transform:translateX(-105%); transition:transform .25s; box-shadow:4px 0 18px rgba(0,0,0,.12); }}
    nav#toc.open {{ transform:translateX(0); }}
    main {{ padding:22px 16px 90px; }}
    article.chapter {{ padding:30px 22px; }}
  }}
</style>
</head>
<body>
<header class="top"><div class="top-inner">
  <span class="book">{BOOK_TITLE}</span><span class="sub">{BOOK_SUB}</span>
  <button class="menu-btn" id="menuBtn">目录 ☰</button>
</div></header>

<div class="layout">
<nav id="toc">
  <div class="toc-title">目　录</div>
  {toc_items}
  <div class="stats">全书初稿<br>约 {total_chars:,} 汉字<br><span style="opacity:.75">人机协作写作 · 持续更新</span></div>
</nav>

<main>
  <section id="cover">
    <h1>{BOOK_TITLE}</h1>
    <div class="rule"></div>
    <div class="sub">{BOOK_SUB}</div>
    <div class="meta">在线阅读版 · 全书 {len(chapters)} 个部分 · 约 {total_chars:,} 汉字<br>内容仍在扩写中，本页随仓库更新</div>
    <a class="btn" id="startBtn" href="javascript:void(0)">开始阅读</a>
  </section>
  {chapter_divs}
</main>
</div>

<footer>{BOOK_TITLE} —— 在线阅读版 · 由书稿仓库自动生成</footer>

<script>
var N = {len(chapters)};
function show(i) {{
  if (i < 0 || i >= N) return;
  document.getElementById("cover").hidden = true;
  for (var k = 0; k < N; k++) document.getElementById("ch" + k).hidden = (k !== i);
  var items = document.querySelectorAll(".toc-item");
  for (var k = 0; k < items.length; k++) items[k].classList.toggle("active", k === i);
  document.getElementById("toc").classList.remove("open");
  window.scrollTo({{ top: 0 }});
}}
document.querySelectorAll(".toc-item").forEach(function(el) {{
  el.addEventListener("click", function() {{ show(+el.dataset.ch); }});
}});
document.querySelectorAll(".ch-nav a").forEach(function(el) {{
  el.addEventListener("click", function() {{ show(+el.dataset.go); }});
}});
document.getElementById("startBtn").addEventListener("click", function() {{ show(0); }});
document.getElementById("menuBtn").addEventListener("click", function() {{
  document.getElementById("toc").classList.toggle("open");
}});
document.addEventListener("keydown", function(e) {{
  var cur = -1, items = document.querySelectorAll(".toc-item");
  for (var k = 0; k < items.length; k++) if (items[k].classList.contains("active")) cur = k;
  if (e.key === "ArrowRight") show(cur + 1);
  if (e.key === "ArrowLeft") show(cur - 1);
}});
</script>
</body>
</html>"""

    out_path = os.path.join(OUT, "index.html")
    open(out_path, "w", encoding="utf-8").write(html)
    print(f"OK: {out_path}")
    print(f"chapters={len(chapters)}  total_han={total_chars}")
    print(f"size={os.path.getsize(out_path)/1024:.0f} KB")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
