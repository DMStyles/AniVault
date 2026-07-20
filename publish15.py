import subprocess, os

env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_TOKEN', 'GH_TOKEN')}

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, env=env)
    print("CMD:", " ".join(args))
    print("OUT:", r.stdout.strip())
    print("ERR:", r.stderr.strip())
    return r.returncode

run(["git", "add", "-A"])
run(["git", "commit", "-m", "KamiWatch v2.1.4: Fix manga crash and add glass header to search"])
run(["git", "push", "origin", "main"])
run(["git", "tag", "v2.1.4"])
run(["git", "push", "origin", "v2.1.4"])

r = subprocess.run([
    "gh", "release", "create", "v2.1.4",
    r"release\KamiWatch-Setup-2.1.4.exe",
    r"release\latest.yml",
    "--title", "KamiWatch v2.1.4 - Bug Fixes & Anime Search Polish",
    "--notes", """KamiWatch v2.1.4 — Polish Update

✨ **What's New:**
- **Manga Tab Fix:** Fixed a critical bug in v2.1.3 that caused the Manga tab to show a black screen when rendering the new hero slider. 
- **Anime Search UI:** Brought the beautiful frosted glass sticky header over to the Anime Search page as well! You'll now get the same premium feel when scrolling through the anime index."""
], capture_output=True, text=True, env=env)

print("Release STDOUT:", r.stdout)
print("Release STDERR:", r.stderr)
print("Release code:", r.returncode)
