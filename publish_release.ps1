$env:GITHUB_TOKEN = ""
$env:GH_TOKEN = ""
gh release create v1.0.62 `
  "release\AniVault-Setup-1.0.62.exe" `
  "release\latest.yml" `
  --title "AniVault v1.0.62 (Feature Update)" `
  --notes "v1.0.62 Feature Update: 
- Removed the old server dropdown and replaced it with clean pill-style buttons (HD-1, VidCloud-1, Vidstream-2, etc.) matching AniKoto's website style.
- The UI now shows *all* available server options on the backend, instead of just auto-selecting one. You can click on any server to switch manually when one encounters an error."
