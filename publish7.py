import subprocess, os

env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_TOKEN', 'GH_TOKEN')}

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, env=env)
    print("CMD:", " ".join(args))
    print("OUT:", r.stdout.strip())
    print("ERR:", r.stderr.strip())
    return r.returncode

run(["git", "add", "-A"])
run(["git", "commit", "-m", "KamiWatch v2.0.6: Full rebuild - genre fix, manga home rows, no duplicate sections"])
run(["git", "push", "origin", "main"])
run(["git", "tag", "v2.0.6"])
run(["git", "push", "origin", "v2.0.6"])

r = subprocess.run([
    "gh", "release", "create", "v2.0.6",
    r"release\KamiWatch-Setup-2.0.6.exe",
    r"release\latest.yml",
    "--title", "KamiWatch v2.0.6 - Manga Genre Fix & Home Screen Manga Rows",
    "--notes", """KamiWatch v2.0.6 — Full Rebuild

✨ **New Features:**
- **📚 Trending Manga** row on Home screen — top followed manga from MangaDex
- **🔥 Recently Updated Manga** row on Home screen — manga with latest chapter uploads
- **✨ New Manga Releases** row on Home screen — newest manga added to MangaDex
- **📖 Continue Reading** row on Home screen — picks up where you left off

🐛 **Bug Fixes:**
- **Genre browsing now works** — fixed by doing a complete backend rebuild (all previous installers had the old backend)
- **Manga chapters now load** — fixed the MangaDex 500-chapter limit bug
- **Removed duplicate Upcoming rows** on Home screen
- This is the first release with a completely up-to-date backend bundled correctly"""
], capture_output=True, text=True, env=env)

print("Release STDOUT:", r.stdout)
print("Release STDERR:", r.stderr)
print("Release code:", r.returncode)
