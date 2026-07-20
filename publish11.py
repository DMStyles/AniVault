import subprocess, os

env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_TOKEN', 'GH_TOKEN')}

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, env=env)
    print("CMD:", " ".join(args))
    print("OUT:", r.stdout.strip())
    print("ERR:", r.stderr.strip())
    return r.returncode

run(["git", "add", "-A"])
run(["git", "commit", "-m", "KamiWatch v2.1.0: Added all missing manga genres"])
run(["git", "push", "origin", "main"])
run(["git", "tag", "v2.1.0"])
run(["git", "push", "origin", "v2.1.0"])

r = subprocess.run([
    "gh", "release", "create", "v2.1.0",
    r"release\KamiWatch-Setup-2.1.0.exe",
    r"release\latest.yml",
    "--title", "KamiWatch v2.1.0 - The Genre Expansion Update",
    "--notes", """KamiWatch v2.1.0 — The Genre Expansion Update

📚 **Massive Genre Update:**
Added almost every single missing genre and demographic filter to the Manga tab, exactly as requested (skipping the weird ones). 

New Genres include:
- Harem
- Tragedy
- Girls' Love (Yuri)
- Boys' Love (Yaoi)
- Webtoon
- Doujinshi
- One Shot
- Historical
- Gender Bender
- ...and all the original ones!"""
], capture_output=True, text=True, env=env)

print("Release STDOUT:", r.stdout)
print("Release STDERR:", r.stderr)
print("Release code:", r.returncode)
