# Crea un acceso directo de TortuScript en el Escritorio (solo para tu usuario).
# Uso (PowerShell):  powershell -ExecutionPolicy Bypass -File lanzadores\crear_acceso_windows.ps1
$aqui = Split-Path -Parent $PSScriptRoot
$bat = Join-Path $aqui "lanzadores\Iniciar TortuScript.bat"
$escritorio = [Environment]::GetFolderPath("Desktop")
$shell = New-Object -ComObject WScript.Shell
$acceso = $shell.CreateShortcut((Join-Path $escritorio "TortuScript.lnk"))
$acceso.TargetPath = $bat
$acceso.WorkingDirectory = $aqui
$acceso.Description = "Aprendé a programar en español"
$acceso.Save()
Write-Host "Listo: hay un acceso directo «TortuScript» en el Escritorio."
