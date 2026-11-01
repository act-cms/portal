#!/usr/bin/env python3
"""Render an instructor-guide markdown file to PDF.

usage: build_guide.py BODY.md OUT.pdf "Notebook display title" "Notebook file name"
"""
import sys, markdown, weasyprint, re, html

body_md, out_pdf, title, nbfile = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
src = open(body_md).read()

CSS = """
@page {
  size: letter; margin: 20mm 19mm 18mm 19mm;
  @bottom-left  { content: "TITLEHERE"; font: 7.5pt "Nimbus Sans", sans-serif; color: #777; }
  @bottom-right { content: counter(page) " of " counter(pages);
                  font: 7.5pt "Nimbus Sans", sans-serif; color: #777; }
}
@page :first { @bottom-left { content: ""; } }
body { font-family: "P052", "Palatino", "DejaVu Serif", serif; font-size: 10.3pt;
       line-height: 1.42; color: #16181c; hyphens: none; }
p { margin: 0 0 7pt 0; text-align: left; }
h1 { font-family: "Nimbus Sans", sans-serif; font-size: 17pt; line-height:1.18;
     margin: 0 0 2pt 0; letter-spacing: -0.2pt; }
.sub { font-family: "Nimbus Sans", sans-serif; font-size: 10.5pt; color:#444;
       margin: 0 0 10pt 0; }
.byline { border-top: 1.6pt solid #16181c; border-bottom: 0.5pt solid #bbb;
          padding: 6pt 0 7pt 0; margin: 0 0 14pt 0; font-size: 9.3pt; color:#333; }
.byline b { font-size: 10pt; color:#16181c; }
.byline .fn { font-family: "DejaVu Sans Mono", monospace; font-size: 8.6pt; }
h2 { font-family: "Nimbus Sans", sans-serif; font-size: 11.6pt; margin: 17pt 0 6pt 0;
     padding-bottom: 2.5pt; border-bottom: 0.6pt solid #c8ccd2; break-after: avoid; }
h3 { font-family: "Nimbus Sans", sans-serif; font-size: 10.2pt; margin: 12pt 0 4pt 0;
     break-after: avoid; }
h4 { font-family: "Nimbus Sans", sans-serif; font-size: 9.6pt; margin: 9pt 0 3pt 0;
     color:#333; break-after: avoid; }
ul, ol { margin: 0 0 7pt 0; padding-left: 15pt; }
li { margin-bottom: 2.5pt; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.7pt;
       background: #f2f3f5; padding: 0 1.5pt; border-radius: 2px; }
pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.2pt; line-height: 1.33;
      background: #f6f7f9; border-left: 2pt solid #c0c5cc; padding: 6pt 8pt;
      margin: 0 0 8pt 0; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 8.2pt; }
table { border-collapse: collapse; width: 100%; margin: 2pt 0 9pt 0; font-size: 9.2pt;
        break-inside: avoid; }
th { font-family: "Nimbus Sans", sans-serif; font-size: 8.4pt; text-transform: uppercase;
     letter-spacing: 0.3pt; text-align: left; border-bottom: 0.9pt solid #16181c;
     padding: 3pt 5pt 3pt 0; vertical-align: bottom; }
td { padding: 3pt 5pt 3pt 0; border-bottom: 0.4pt solid #dcdfe3; vertical-align: top; }
blockquote { margin: 0 0 8pt 0; padding: 7pt 9pt; background: #f4f1ea;
             border-left: 2.5pt solid #9a8c6a; font-size: 9.6pt; break-inside: avoid; }
blockquote p { margin-bottom: 4pt; }
blockquote p:last-child { margin-bottom: 0; }
hr { border: none; border-top: 0.5pt solid #ccd0d6; margin: 12pt 0; }
em { font-style: italic; } strong { font-weight: 600; }
.tight li { margin-bottom: 1pt; }
"""

md = markdown.Markdown(extensions=['tables', 'fenced_code', 'attr_list', 'sane_lists',
                                   'md_in_html', 'footnotes'])
head = (f'<h1>{html.escape(title)}</h1>\n'
        f'<p class="sub">Instructor guide &mdash; preparation, delivery and known issues</p>\n'
        f'<div class="byline"><b>Keith Fraser, PhD</b> &nbsp;·&nbsp; Senior Lecturer, '
        f'Department of Biological Sciences &nbsp;·&nbsp; Rensselaer Polytechnic Institute'
        f'<br><span class="fn">online/{html.escape(nbfile)}</span></div>\n')
doc = (f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}'
       f' — instructor guide</title>'
       f'<meta name="author" content="Keith Fraser, PhD">'
       f'<meta name="description" content="Instructor guide for the Colab notebook '
       f'{html.escape(nbfile)}: preparation, delivery, expected output and known issues.">'
       f'<meta name="keywords" content="instructor guide, computational structural biology, '
       f'Google Colab, Rensselaer Polytechnic Institute">'
       f'<style>'
       + CSS.replace('TITLEHERE', title.replace('"', "'"))
       + '</style></head><body>' + head + md.convert(src) + '</body></html>')
open(out_pdf.replace('.pdf', '.html'), 'w').write(doc)
weasyprint.HTML(string=doc, base_url='.').write_pdf(out_pdf)
print('wrote', out_pdf)
