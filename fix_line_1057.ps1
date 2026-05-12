$f = 'frontend\src\views\Reseaux.vue'
$lines = Get-Content $f -Encoding UTF8
$new = $lines[0..1055] + $lines[1057..($lines.Length - 1)]
Set-Content $f $new -Encoding UTF8
Write-Host "Done. Total lines: $($new.Length)"
