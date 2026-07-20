import subprocess, os, sys

env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_TOKEN', 'GH_TOKEN')}

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, env=env)
    print("CMD:", " ".join(args))
    print("OUT:", r.stdout.strip())
    print("ERR:", r.stderr.strip())
    return r.returncode

run(["git", "add", "-A"])
run(["git", "commit", "-m", "KamiWatch v2.0.0: Rebrand + Manga Reader with MangaDex and MangaKakalot"])
run(["git", "push", "origin", "main"])
run(["git", "tag", "v2.0.0"])
run(["git", "push", "origin", "v2.0.0"])

# Create GitHub release
r = subprocess.run([
    "gh", "release", "create", "v2.0.0",
    r"release\KamiWatch-Setup-2.0.0.exe",
    r"release\latest.yml",
    "--title", "KamiWatch v2.0.0 - Major Release",
    "--notes", """KamiWatch v2.0.0 — Major Release

🎉 App renamed from AniVault to KamiWatch

📚 NEW: Manga Reader
- Search manga via MangaDex (primary) and MangaKakalot (backup)
- Long-strip (vertical scroll) and page-by-page reading modes
- Keyboard navigation (arrow keys)
- Auto-advance to next chapter
- Exclusive warm amber/ink theme for the Manga section

🔧 Bug Fixes (from v1.x)
- Fixed stale state bug preventing Japanese fallback title matching
- Added server pill buttons for manual stream server selection
- Fixed rate-limiting on Anikoto stream resolution"""
], capture_output=True, text=True, env=env)

print("Release STDOUT:", r.stdout)
print("Release STDERR:", r.stderr)
print("Release code:", r.returncode)
