$source = 'C:\Users\GercakD\OneDrive - pvs.cz\H\_NORMY\AI_priprava'
$target = 'C:\Users\GercakD\OneDrive - pvs.cz\H\_NORMY\AI_priprava-test'
#$target = 'C:\Users\GercakD\OneDrive - pvs.cz\BIM_Podpora\_NORMY'

function Copy-IfNewer {
    param($src, $dst)
    if (-not (Test-Path $dst) -or (Get-Item $src).LastWriteTime -gt (Get-Item $dst).LastWriteTime) {
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "Zkopírováno: $src" -ForegroundColor Cyan
    }
}

Get-ChildItem -Path $source -Directory | ForEach-Object {
    $normDir = $_
    $destDir = Join-Path $target $normDir.Name

    New-Item -ItemType Directory -Path $destDir -Force | Out-Null

    # Rozdílové kopírování .pdf a .md souborů
    Get-ChildItem -Path $normDir.FullName -File |
        #Where-Object { $_.Extension -in '.pdf', '.md' } |
        Where-Object { $_.Extension -in '.md' } |
        ForEach-Object { Copy-IfNewer $_.FullName (Join-Path $destDir $_.Name) }

    # Pouze podsložky odpovídající názvu normy
    $normNames = Get-ChildItem -Path $normDir.FullName -Filter '*.pdf' -File |
        ForEach-Object { $_.BaseName }

    Get-ChildItem -Path $normDir.FullName -Directory |
        Where-Object { $_.Name -in $normNames } |
        ForEach-Object {
            $subSrc = $_.FullName
            $subDst = Join-Path $destDir $_.Name

            New-Item -ItemType Directory -Path $subDst -Force | Out-Null

            # Rekurzivně projdi všechny soubory v podsložce
            Get-ChildItem -Path $subSrc -Recurse -File | ForEach-Object {
                $relativePath = $_.FullName.Substring($subSrc.Length)
                $dstFile = Join-Path $subDst $relativePath
                New-Item -ItemType Directory -Path (Split-Path $dstFile) -Force | Out-Null
                Copy-IfNewer $_.FullName $dstFile
            }
        }
}

Write-Host "Hotovo." -ForegroundColor Green