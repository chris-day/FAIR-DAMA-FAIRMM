$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$projectRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$results=Join-Path $projectRoot 'results/high-level-connections'
$colors=@{Direct='#2463a7';Indirect='#b75f08';Descriptor='#7752a0';Deliverable='#607080';Responsible='#258373';Approving='#9a7031';Contributing='#647cb3'}
foreach($file in Get-ChildItem -LiteralPath $results -Recurse -Filter '*-sankey.json') {
    $model=Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
    $bitmap=[System.Drawing.Bitmap]::new([int]$model.width,[int]$model.height)
    $graphics=[System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.Clear([System.Drawing.Color]::White)
    $normal=[System.Drawing.Font]::new('Segoe UI',18,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
    $small=[System.Drawing.Font]::new('Segoe UI',16,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
    $title=[System.Drawing.Font]::new('Segoe UI',32,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
    $ink=[System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#16283c'))
    $nodeBrush=[System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml('#405468'))
    try {
        $graphics.DrawString($model.title,$title,$ink,48,24)
        $graphics.DrawString(('Ontology-derived documentary connections · 19 November 2026 · '+$model.links.Count+' graphical links'),$normal,$ink,48,78)
        $legendX=48
        foreach($entry in $model.counts.PSObject.Properties){
            $color=$colors[$entry.Name];if(-not $color){$color='#258373'}
            $brush=[System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml($color))
            $graphics.FillRectangle($brush,$legendX,128,28,12)
            $legend=if($model.key -eq 'dimensions-levels' -and $entry.Name -eq 'Descriptor'){'42 descriptors · 84 links'}else{$entry.Name+' · '+$entry.Value}
            $graphics.DrawString($legend,$normal,$ink,($legendX+40),120)
            $brush.Dispose();$legendX+=245
        }
        foreach($link in $model.links){
            $g=$link.geometry;$x0=[single]$g.x0;$x1=[single]$g.x1;$y0=[single]$g.y0;$y1=[single]$g.y1;$t=[single]$g.thickness
            $c0=$x0+($x1-$x0)*0.45;$c1=$x1-($x1-$x0)*0.45
            $path=[System.Drawing.Drawing2D.GraphicsPath]::new()
            $path.AddBezier($x0,$y0,$c0,$y0,$c1,$y1,$x1,$y1)
            $path.AddLine($x1,$y1,$x1,($y1+$t))
            $path.AddBezier($x1,($y1+$t),$c1,($y1+$t),$c0,($y0+$t),$x0,($y0+$t));$path.CloseFigure()
            $color=$colors[$link.kind];if(-not $color){$color='#258373'}
            $brush=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(89,[System.Drawing.ColorTranslator]::FromHtml($color)))
            $graphics.FillPath($brush,$path)
            if($link.kind -eq 'Indirect'){$pen=[System.Drawing.Pen]::new([System.Drawing.ColorTranslator]::FromHtml('#783b00'),1);$pen.DashPattern=@(6,4);$graphics.DrawPath($pen,$path);$pen.Dispose()}
            $brush.Dispose();$path.Dispose()
        }
        foreach($node in $model.nodes){
            $graphics.FillRectangle($nodeBrush,[single]$node.x,[single]$node.y,16,[single]$node.height)
            for($i=0;$i -lt $node.lines.Count;$i++){
                $line=$node.lines[$i];$size=$graphics.MeasureString($line,$normal)
                $x=if($node.column -eq 0){$node.x-16-$size.Width}else{$node.x+28}
                $y=$node.y+$node.height/2+($i-($node.lines.Count-1)/2)*22-12
                $graphics.FillRectangle([System.Drawing.Brushes]::White,[single]$x,[single]$y,[single]$size.Width,[single]$size.Height)
                $graphics.DrawString($line,$normal,$ink,[single]$x,[single]$y)
            }
        }
        $graphics.DrawString($model.basis,$small,$ink,[System.Drawing.RectangleF]::new(48,($model.height-105),($model.width-96),100))
        $output=Join-Path $file.DirectoryName ($file.BaseName+'.png')
        $bitmap.Save($output,[System.Drawing.Imaging.ImageFormat]::Png)
        $doc=Join-Path $projectRoot ('docs/high-level-connections/'+$model.key+'/'+$file.BaseName+'.png')
        Copy-Item -LiteralPath $output -Destination $doc
    } finally {$graphics.Dispose();$bitmap.Dispose();$normal.Dispose();$small.Dispose();$title.Dispose();$ink.Dispose();$nodeBrush.Dispose()}
    Write-Output ('Rendered '+$model.key+' PNG')
}
