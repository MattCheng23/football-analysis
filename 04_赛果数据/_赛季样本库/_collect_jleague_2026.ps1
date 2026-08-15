# J.League 2026 (leagueId 223) played-match collector via FotMob teams API
$ErrorActionPreference = "Stop"
$dir = "D:\Cola\足球分析学习\04_赛果数据\_赛季样本库"
$tmp = Join-Path $dir "_tmp_teams"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

$queue = [System.Collections.Generic.List[int]]::new()
foreach ($s in @(4397, 8006)) { $queue.Add($s) }
$fetched = [System.Collections.Generic.HashSet[int]]::new()
$all = [System.Collections.Generic.List[object]]::new()
$teamNames = @{}

while ($queue.Count -gt 0) {
    $tid = $queue[0]; $queue.RemoveAt(0)
    if ($fetched.Contains($tid)) { continue }
    [void]$fetched.Add($tid)
    $file = Join-Path $tmp ("team_{0}.json" -f $tid)
    curl.exe -s -H "x-mas: 9a9a7e262fce7ff04f0de2242aaf5c34" ("https://www.fotmob.com/api/data/teams?id={0}" -f $tid) -o $file
    Start-Sleep -Milliseconds 250
    try { $j = Get-Content $file -Raw -Encoding UTF8 | ConvertFrom-Json } catch { Write-Host ("PARSE FAIL {0}" -f $tid); continue }
    if (-not $j.fixtures -or -not $j.fixtures.allFixtures -or -not $j.fixtures.allFixtures.fixtures) { Write-Host ("NO FIXTURES {0}" -f $tid); continue }
    $teamNames[$tid] = $j.details.name
    Write-Host ("OK {0} {1}" -f $tid, $j.details.name)
    foreach ($m in $j.fixtures.allFixtures.fixtures) {
        if ($m.tournament.leagueId -ne 223) { continue }
        if ($m.home.id) { $queue.Add([int]$m.home.id) }
        if ($m.away.id) { $queue.Add([int]$m.away.id) }
        if ($m.status.finished) { $all.Add($m) }
    }
}

# dedupe by date+home+away+score (JST date)
$seen = [System.Collections.Generic.HashSet[string]]::new()
$rows = [System.Collections.Generic.List[object]]::new()
foreach ($m in $all) {
    $dto = [DateTimeOffset]::Parse($m.status.utcTime).UtcDateTime.AddHours(9)
    $date = $dto.ToString("yyyy-MM-dd")
    $homeName = [string]$m.home.name
    $awayName = [string]$m.away.name
    $score = ("{0}-{1}" -f $m.home.score, $m.away.score)
    $key = ("{0}|{1}|{2}|{3}" -f $date, $homeName, $awayName, $score)
    if (-not $seen.Add($key)) { continue }
    $rows.Add([ordered]@{ date = $date; home = $homeName; away = $awayName; score = $score; ht = $null })
}

$rows | ConvertTo-Json -Depth 3 | Set-Content -Path (Join-Path $dir "日职_2026.json") -Encoding UTF8
Write-Host ("TOTAL finished raw (with dupes): {0}" -f $all.Count)
Write-Host ("UNIQUE matches: {0}" -f $rows.Count)
Write-Host ("TEAMS fetched: {0}" -f $fetched.Count)
$teamNames.GetEnumerator() | Sort-Object Value | ForEach-Object { Write-Host ("  {0} {1}" -f $_.Key, $_.Value) }
