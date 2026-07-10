# Restart the app cleanly — only stops Streamlit on this project, not all Python.
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

# Stop processes already using port 8501
$connections = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
foreach ($conn in $connections) {
    $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "Stopping process on port 8501 (PID $($proc.Id))..."
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 1

# Clear stale Python cache
Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Filter __pycache__ -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Remove-Item Env:AMINA_BOOTSTRAPPED -ErrorAction SilentlyContinue
# Local dev: allow app.py bytecode bootstrap for hot-reload. Never set on Streamlit Cloud.
$env:AMINA_DEV = "1"

Write-Host ""
Write-Host "Starting app at http://localhost:8501"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

streamlit run app.py