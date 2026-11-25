$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$resultRoot = Join-Path $projectRoot 'results/tools-personas'
$model = Get-Content -LiteralPath (Join-Path $resultRoot 'dama-fairmm-tools-personas-sankey.json') -Raw | ConvertFrom-Json
$bitmap = [System.Drawing.Bitmap]::new([int]$model.width, [int]$model.height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$graphics.Clear([System.Drawing.Color]::White)
$normal = [System.Drawing.Font]::new('Segoe UI',18,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
$small = [System.Drawing.Font]::new('Segoe UI',17,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
$subtitle = [System.Drawing.Font]::new('Segoe UI',19,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
$title = [System.Drawing.Font]::new('Segoe UI',31,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$ink = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#16283c'))
$muted = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#475569'))
$nodeBrush = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#405468'))

function Draw-Label([string]$text,[double]$x,[double]$baseline,$font,$brush,[bool]$right=$false) {
    $measure=$graphics.MeasureString($text,$font)
    if ($right) { $x -= $measure.Width }
    $graphics.DrawString($text,$font,$brush,[single]$x,[single]($baseline-$font.GetHeight($graphics)*0.82))
}

try {
    Draw-Label $model.title 48 57 $title $ink
    Draw-Label 'Activity-role projection · FAIRMM D7 · 17 November 2026' 48 94 $subtitle $ink
    foreach($entry in @(@(48,'#2463a7',('Direct · '+$model.counts.Direct)),@(260,'#b75f08',('Indirect · '+$model.counts.Indirect)))) {
        $brush=[System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml($entry[1]))
        $graphics.FillRectangle($brush,[single]$entry[0],122,38,15)
        Draw-Label $entry[2] ($entry[0]+50) 136 $normal $ink
        $brush.Dispose()
    }
    Draw-Label 'One equal-width ribbon per persona and practice alignment type' 480 136 $normal $muted
    Draw-Label 'DAMA personas (activity role occurrences)' 48 183 $small $ink
    Draw-Label 'FAIRMM dimension' 1298 183 $small $ink
    foreach($link in $model.links) {
        $g=$link.geometry
        [single]$x0=$g.x0; [single]$x1=$g.x1; [single]$y0=$g.y0; [single]$y1=$g.y1; [single]$t=$g.thickness
        [single]$c0=$x0+($x1-$x0)*0.45; [single]$c1=$x1-($x1-$x0)*0.45
        $path=[System.Drawing.Drawing2D.GraphicsPath]::new()
        $path.AddBezier($x0,$y0,$c0,$y0,$c1,$y1,$x1,$y1)
        $path.AddLine($x1,$y1,$x1,($y1+$t))
        $path.AddBezier($x1,($y1+$t),$c1,($y1+$t),$c0,($y0+$t),$x0,($y0+$t))
        $path.CloseFigure()
        $color=if($link.kind -eq 'Direct'){'#2463a7'}else{'#b75f08'}
        $brush=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(89,[System.Drawing.ColorTranslator]::FromHtml($color)))
        $graphics.FillPath($brush,$path)
        if($link.kind -eq 'Indirect') {
            $pen=[System.Drawing.Pen]::new([System.Drawing.ColorTranslator]::FromHtml('#783b00'),1.2)
            $pen.DashPattern=[single[]]@(6,4)
            $graphics.DrawPath($pen,$path)
            $pen.Dispose()
        }
        $brush.Dispose(); $path.Dispose()
    }
    foreach($node in $model.nodes) {
        $graphics.FillRectangle($nodeBrush,[single]$node.x,[single]$node.y,16,[single]$node.height)
        $center=$node.y+$node.height/2
        for($i=0;$i -lt $node.lines.Count;$i++) {
            $baseline=$center+($i-($node.lines.Count-1)/2)*23+6
            if($node.side -eq 'source') { Draw-Label $node.lines[$i] 419 $baseline $normal $ink $true }
            else { Draw-Label $node.lines[$i] 1299 $baseline $normal $ink }
        }
    }
    Draw-Label 'Ribbons retain practice alignment type; role categories and activities are available in the interactive details.' 48 ($model.height-65) $small $muted
    Draw-Label 'Persona participation does not establish personal accountability, FAIR implementation or maturity.' 48 ($model.height-35) $small $muted
    $bitmap.Save((Join-Path $resultRoot 'dama-fairmm-tools-personas-sankey.png'),[System.Drawing.Imaging.ImageFormat]::Png)
    Copy-Item -LiteralPath (Join-Path $resultRoot 'dama-fairmm-tools-personas-sankey.png') -Destination (Join-Path $projectRoot 'docs/tools-personas/dama-fairmm-tools-personas-sankey.png')
} finally {
    $graphics.Dispose();$bitmap.Dispose();$normal.Dispose();$small.Dispose();$subtitle.Dispose();$title.Dispose();$ink.Dispose();$muted.Dispose();$nodeBrush.Dispose()
}
Write-Output 'Rendered Sankey PNG'

