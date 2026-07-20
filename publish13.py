import subprocess, os

env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_TOKEN', 'GH_TOKEN')}

def run(args):
    r = subprocess.run(args, capture_output=True, text=True, env=env)
    print("CMD:", " ".join(args))
    print("OUT:", r.stdout.strip())
    print("ERR:", r.stderr.strip())
    return r.returncode

run(["git", "add", "-A"])
run(["git", "commit", "-m", "KamiWatch v2.1.2: Added manga genre pagination"])
run(["git", "push", "origin", "main"])
run(["git", "tag", "v2.1.2"])
run(["git", "push", "origin", "v2.1.2"])

r = subprocess.run([
    "gh", "release", "create", "v2.1.2",
    r"release\KamiWatch-Setup-2.1.2.exe",
    r"release\latest.yml",
    "--title", "KamiWatch v2.1.2 - The Pagination Update",
    "--notes", """KamiWatch v2.1.2 — The Pagination Update

📚 **Manga Genre Pagination:**
- Added full pagination to the manga genre search page! Now, when you click on a genre (like "Harem" or "Action"), you can browse through thousands of titles instead of being limited to just the top 100!
- You'll find the "Previous" and "Next Page" buttons at the bottom of the grid."""
], capture_output=True, text=True, env=env)

print("Release STDOUT:", r.stdout)
print("Release STDERR:", r.stderr)
print("Release code:", r.returncode)
