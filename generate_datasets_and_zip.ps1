param(
    [int]$LargeFileCount = 10,
    [int]$LargeFileSizeMB = 3,
    [int]$DiverseFileCount = 10,
    [string]$OutputDir = ".\student_datasets"
)

$ErrorActionPreference = 'Stop'

$basePath = (Resolve-Path .).Path
$outPath = Join-Path $basePath $OutputDir
$largeDir = Join-Path $outPath 'dataset_large'
$diverseDir = Join-Path $outPath 'dataset_diverse'

$topics = @{
    distributed = @('distributed','system','worker','coordinator','parallel','processing','node','cluster','message','queue','socket','throughput','latency','scaling','task','result','reduce','map','pipeline','fault')
    security    = @('security','policy','access','token','identity','audit','threat','firewall','credential','encryption','incident','zero','trust','monitoring','alert','compliance','session','risk','control','vault')
    cloud       = @('cloud','service','region','storage','compute','instance','container','kubernetes','serverless','backup','replication','availability','tenant','billing','deployment','autoscaling','platform','orchestration')
    data        = @('data','dataset','schema','query','table','index','record','analytics','warehouse','stream','batch','quality','transform','cleaning','feature','model','training','prediction','metric','visualization')
    network     = @('network','packet','route','switch','router','latency','bandwidth','segment','protocol','tcp','udp','session','frame','dns','gateway','vlan','firewall','monitoring','flow','tunnel')
    software    = @('software','module','testing','integration','deployment','release','version','repository','branch','commit','review','bug','feature','refactor','quality','documentation','maintainability','pipeline')
}

$common = @('analysis','performance','system','student','project','implementation','architecture','result','measurement','process','communication','synchronization','algorithm','input','output','comparison','resource')

$templates = @(
    'The {0} module sends a {1} update to the coordinator and records the result for later analysis.',
    'Each student reviews the {0} workflow, measures performance, and documents every important result.',
    'A stable system needs careful synchronization, predictable input, and clear output during parallel processing.',
    'When the worker finishes a task, the coordinator aggregates the result and updates the global metric table.',
    'Distributed processing improves throughput when communication overhead stays lower than useful computation.',
    'The project compares sequential execution with parallel execution and explains the observed speedup.',
    'Every dataset contains repeated terms so the final ranking highlights meaningful patterns in the analysis.',
    'Reliable software depends on testing, logging, reproducible measurements, and readable implementation details.',
    'A queue based architecture may simplify communication while a socket based design exposes lower level behavior.',
    'Students should explain how the algorithm splits files, merges partial dictionaries, and validates correctness.'
)

$diverseParagraphs = @(
    'Astronomy describes stars, planets, orbits, telescopes and deep sky observation. Such text gives words related to space, light, motion and measurement.',
    'Biology focuses on cells, genes, proteins, organisms and ecosystems. This adds vocabulary about evolution, energy, environment and experiment.',
    'History tells stories about states, wars, reforms, society and sources. Historical texts create a different pattern of frequent words than technical material.',
    'Economics studies market behavior, cost, production, demand, supply and investment. This introduces words connected with price, decision, balance and growth.',
    'Medicine covers diagnosis, therapy, patient, symptom, examination and prevention. This type of content increases token diversity and tests normalization rules.',
    'Literature uses characters, narration, style and metaphor. Files from this area usually contain richer vocabulary, longer sentences and fewer repeated technical terms.',
    'Computer science still remains part of the corpus and brings terms such as process, memory, thread, algorithm and synchronization. This mixes technical and general vocabulary.',
    'Transport includes logistics, route, shipment, warehouse, schedule and delay. It is useful for observing frequent words in an operational domain.',
    'Law discusses regulations, responsibility, contract, interpretation and procedure. Such texts show how different domains influence the final Top 20 ranking.',
    'Education highlights teaching, competence, evaluation, project, cooperation and development. It is a natural addition to the corpus prepared for students.'
)

$topicKeys = @($topics.Keys)
$random = [System.Random]::new(42)

function Get-RandomItem {
    param([object[]]$Items)
    return $Items[$random.Next(0, $Items.Count)]
}

function New-WeightedWords {
    param(
        [string[]]$A,
        [string[]]$B,
        [string[]]$C,
        [int]$Count
    )

    $all = @($A + $B + $C)
    $list = New-Object System.Collections.Generic.List[string]
    for ($i = 0; $i -lt $Count; $i++) {
        $list.Add((Get-RandomItem -Items $all))
    }
    return ($list -join ' ')
}

function Build-LargeText {
    param(
        [int]$TargetBytes,
        [string]$DominantKey,
        [string]$SecondaryKey
    )

    $sb = New-Object System.Text.StringBuilder
    $a = $topics[$DominantKey]
    $b = $topics[$SecondaryKey]

    while ($sb.Length -lt $TargetBytes) {
        $template = Get-RandomItem -Items $templates
        $sentence = [string]::Format($template, (Get-RandomItem -Items $a), (Get-RandomItem -Items $b))
        $weighted = New-WeightedWords -A $a -B $b -C $common -Count 60
        [void]$sb.AppendLine("$sentence $weighted.")
        [void]$sb.AppendLine()
    }

    return $sb.ToString()
}

function Build-DiverseText {
    param(
        [int]$Index,
        [int]$TargetWords = 10000
    )

    $sb = New-Object System.Text.StringBuilder
    $baseText = $diverseParagraphs[$Index % $diverseParagraphs.Count]
    $dominant = $topics[$topicKeys[$Index % $topicKeys.Count]]
    $secondary = $topics[$topicKeys[($Index + 2) % $topicKeys.Count]]
    $wordCount = 0

    while ($wordCount -lt $TargetWords) {
        $template = Get-RandomItem -Items $templates
        $sentence = [string]::Format($template, (Get-RandomItem -Items $dominant), (Get-RandomItem -Items $secondary))
        $mixed = New-WeightedWords -A $dominant -B $secondary -C $common -Count 45
        $paragraph = ('{0} {1} {2}.{3}{3}' -f $baseText, $sentence, $mixed, [Environment]::NewLine)
        [void]$sb.Append($paragraph)
        $wordCount += ($paragraph -split '\s+').Count
    }

    return $sb.ToString()
}

function Write-TextFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
    $sizeMB = [math]::Round(((Get-Item $Path).Length / 1MB), 2)
    Write-Host ('Created: {0} ({1} MB)' -f $Path, $sizeMB)
}

function Reset-Dir {
    param([string]$Path)

    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Path | Out-Null
}

Reset-Dir -Path $outPath
Reset-Dir -Path $largeDir
Reset-Dir -Path $diverseDir

$targetBytes = $LargeFileSizeMB * 1MB
for ($i = 0; $i -lt $LargeFileCount; $i++) {
    $dominant = $topicKeys[$i % $topicKeys.Count]
    $secondary = $topicKeys[($i + 1) % $topicKeys.Count]
    $content = Build-LargeText -TargetBytes $targetBytes -DominantKey $dominant -SecondaryKey $secondary
    $filePath = Join-Path $largeDir ('large_text_{0}.txt' -f ($i + 1))
    Write-TextFile -Path $filePath -Content $content
}

for ($i = 0; $i -lt $DiverseFileCount; $i++) {
    $content = Build-DiverseText -Index $i -TargetWords 10000
    $filePath = Join-Path $diverseDir ('diverse_text_{0}.txt' -f ($i + 1))
    Write-TextFile -Path $filePath -Content $content
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipLarge = Join-Path $outPath 'dataset_large.zip'
$zipDiverse = Join-Path $outPath 'dataset_diverse.zip'
if (Test-Path $zipLarge) { Remove-Item $zipLarge -Force }
if (Test-Path $zipDiverse) { Remove-Item $zipDiverse -Force }
[System.IO.Compression.ZipFile]::CreateFromDirectory($largeDir, $zipLarge)
[System.IO.Compression.ZipFile]::CreateFromDirectory($diverseDir, $zipDiverse)

$summary = @"
Done.
Working folder: $outPath
ZIP archives:
 - $zipLarge
 - $zipDiverse
"@

$summaryPath = Join-Path $outPath 'README_GENERATED.txt'
$summary | Set-Content -Path $summaryPath -Encoding UTF8
Write-Host ''
Write-Host $summary