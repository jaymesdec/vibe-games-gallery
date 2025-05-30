import os, re, shutil
from urllib.parse import quote

OUTPUT = "index.html"
EXT_HTML = (".html", ".htm", ".HTML", ".HTM")
EXT_REWRITE = EXT_HTML + (".css", ".js")
SKIP_DIR = {'.git', '__pycache__', 'node_modules', '.DS_Store'}

# -------- path-fix helpers --------
LOCAL_ABS = re.compile(r'''(["'])/([^/][^"']*)\1''')  # "/foo/bar.png"
CSS_URL   = re.compile(r'url\(\s*["\']?/([^/][^)"\']*)["\']?\s*\)', re.I)

def fix_paths(file_path):
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        txt = f.read()

    # HTML src/href
    txt = LOCAL_ABS.sub(lambda m: f'{m.group(1)}{m.group(2)}{m.group(1)}', txt)
    # CSS url()
    txt = CSS_URL.sub(lambda m: f'url({m.group(1)})', txt)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(txt)

def patch_folder(folder):
    """rewrite any local-absolute paths in html/css/js"""
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR and not d.startswith('.')]
        for fname in files:
            if fname.endswith(EXT_REWRITE):
                fp = os.path.join(root, fname)
                backup = fp + ".orig"
                if not os.path.exists(backup):
                    shutil.copy2(fp, backup)
                fix_paths(fp)

# -------- gallery helpers --------
def first_html(folder):
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR and not d.startswith('.')]
        for f in files:
            if f.endswith(EXT_HTML):
                return os.path.relpath(os.path.join(root, f), os.getcwd())
    return None

def collect_projects(base):
    projects = []
    for entry in sorted(os.listdir(base)):
        full = os.path.join(base, entry)
        if os.path.isdir(full) and entry not in SKIP_DIR and not entry.startswith('.'):
            html_rel = first_html(full)
            if html_rel:
                patch_folder(full)             # <-- auto-fix assets
                projects.append((entry, html_rel))
                print(f"✅ {entry}: {html_rel}")
            else:
                print(f"⚠️  {entry}: no html found")
    return projects

def build_gallery(projects):
    rows = []
    for folder, rel in projects:
        label = folder.replace("_", " ").replace("-", " ")
        rows.append(f'    <li><a href="{quote(rel)}" target="_blank">{label}</a></li>')
    body = "\n".join(rows)

    return f"""<!DOCTYPE html>
<html lang='en'><head><meta charset='utf-8'>
<title>Vibe Coding Game Gallery</title>
<style>
 body{{font-family:sans-serif;padding:2rem}}
 h1{{text-align:center}}
 ul{{list-style:none;padding:0;max-width:700px;margin:auto}}
 li{{margin:1rem 0}}
 a{{text-decoration:none;color:#007acc;font-size:1.2rem}}
</style></head><body>
<h1>🎮 Vibe Coding Game Gallery 🎮</h1>
<ul>
{body}
</ul></body></html>"""

def main():
    root = os.getcwd()
    print(f"🔍 scanning {root}\n")
    projects = collect_projects(root)
    if not projects:
        print("❌ nothing found"); return
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(build_gallery(projects))
    print(f"\n🎉 wrote {OUTPUT} with {len(projects)} links")

if __name__ == "__main__":
    main()
