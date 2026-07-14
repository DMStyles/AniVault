; AniVault Custom NSIS Installer Script
; This runs during installation

!macro customInit
  nsExec::Exec 'taskkill /F /IM anivault-backend.exe'
!macroend

!macro customInstall
  nsExec::Exec 'taskkill /F /IM anivault-backend.exe'
  ; Add AniVault to Windows "Add/Remove Programs" with correct info
  WriteRegStr HKCU "Software\AniVault" "InstallPath" "$INSTDIR"
  WriteRegStr HKCU "Software\AniVault" "Version" "${VERSION}"
!macroend

!macro customUnInstall
  ; Clean up registry on uninstall
  DeleteRegKey HKCU "Software\AniVault"
!macroend
