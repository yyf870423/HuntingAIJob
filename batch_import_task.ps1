param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet('list', 'cancel', 'delete', 'help')]
    [string]$Action,
    [Parameter(Position=1, Mandatory=$false)]
    [string]$TaskId
)

function Show-Help {
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\\batch_import_task.ps1 list                 # List all tasks" -ForegroundColor Yellow
    Write-Host "  .\\batch_import_task.ps1 cancel <TaskID>      # Cancel the specified task" -ForegroundColor Yellow
    Write-Host "  .\\batch_import_task.ps1 delete <TaskID>      # Delete the specified task" -ForegroundColor Yellow
    Write-Host "  .\\batch_import_task.ps1 help                 # Show this help message" -ForegroundColor Yellow
}

$pythonScript = Join-Path $PSScriptRoot 'app/batch_import_task.py'

if ($Action -eq 'list') {
    python $pythonScript list
} elseif ($Action -eq 'cancel' -and $TaskId) {
    python $pythonScript cancel $TaskId
} elseif ($Action -eq 'delete' -and $TaskId) {
    python $pythonScript delete $TaskId
} elseif ($Action -eq 'help') {
    Show-Help
} else {
    Show-Help
    exit 1
} 