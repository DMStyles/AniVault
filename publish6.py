import subprocess, os

env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_TOKEN', 'GH_TOKEN')}

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, env=env)
    print("CMD:", " ".join(args))
    print("OUT:", r.stdout.strip())
    print("ERR:", r.stderr.strip())
    return r.returncode

run(["git", "add", "-A"])
run(["git", "commit", "-m", "KamiWatch v2.0.5: Fix genre browsing backend, add Continue Reading manga history, add Upcoming Season section"])
run(["git", "push", "origin", "main"])
run(["git", "tag", "v2.0.5"])
run(["git", "push", "origin", "v2.0.5"])

r = subprocess.run([
    "gh", "release", "create", "v2.0.5",
    r"release\KamiWatch-Setup-2.0.5.exe",
    r"release\latest.yml",
    "--title", "KamiWatch v2.0.5 - Genre Browsing Fixed + Home Screen Improvements",
    "--notes", """KamiWatch v2.0.5 — Complete Fix & Feature Release

✨ **New Features:**
- **Continue Reading (Home)**: Home screen now shows a "Continue Reading" manga row that remembers where you left off — clicking any card takes you directly to your last chapter.
- **Upcoming This Season (Home)**: Replaced the fake static "Recently Updated" row with a live "Upcoming This Season" section pulling real data.

🐛 **Bug Fixes:**
- **Genre Browsing now works!** Fixed the root cause: previous installers bundled the old v2.0.0 backend which had no /genre endpoint. Now the correct backend is included.
- **Manga Chapters now load!** Fixed the MangaDex 500-chapter limit bug that caused all manga to show 0 chapters.
- The genre endpoint now correctly handles demographic-only filters (Shounen, Seinen, Shoujo, Josei)."""
], capture_output=True, text=True, env=env)

print("Release STDOUT:", r.stdout)
print("Release STDERR:", r.stderr)
print("Release code:", r.returncode)
