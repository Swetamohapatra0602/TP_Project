$ErrorActionPreference = 'Stop'
$presentationRoot = Split-Path -Parent $PSScriptRoot
$deckPath = Join-Path $presentationRoot 'Online_Shopping_Playwright_Project_Fixed_Headers.pptx'
$pdfPath = Join-Path $presentationRoot 'Online_Shopping_Playwright_Project_Fixed_Headers.pdf'
$previewPath = Join-Path $PSScriptRoot 'rendered-fixed-headers'
New-Item -ItemType Directory -Path $previewPath -Force | Out-Null
$powerPoint = $null
$deck = $null
$priorCount = 0
$issues = @()
$shapeCount = 0
function Get-OfficeColor([string]$HexColor) {
    return [Convert]::ToInt32($HexColor.Substring(0, 2), 16) +
        256 * [Convert]::ToInt32($HexColor.Substring(2, 2), 16) +
        65536 * [Convert]::ToInt32($HexColor.Substring(4, 2), 16)
}
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $priorCount = $powerPoint.Presentations.Count
    $priorSecurity = $powerPoint.AutomationSecurity
    $powerPoint.AutomationSecurity = 3
    # Open the reference read-only; save the adapted deck to a different file.
    $deck = $powerPoint.Presentations.Open('C:\Users\Admin\Downloads\CRM (1).pptx', -1, 0, 0)
    $manifest = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $PSScriptRoot 'slide_manifest.json') | ConvertFrom-Json
    for ($masterIndex = $deck.SlideMaster.Shapes.Count; $masterIndex -ge 1; $masterIndex--) {
        $deck.SlideMaster.Shapes.Item($masterIndex).Delete()
    }
    foreach ($layout in $deck.SlideMaster.CustomLayouts) {
        for ($layoutShapeIndex = $layout.Shapes.Count; $layoutShapeIndex -ge 1; $layoutShapeIndex--) {
            # Nested reference geometry was displaced by the user's viewer.
            # Every visible shape now comes from bounded slide-local primitives.
            $layout.Shapes.Item($layoutShapeIndex).Delete()
        }
    }
    foreach ($slideData in $manifest) {
        $slide = $deck.Slides.Item([int]$slideData.slide)
        $slide.CustomLayout = $deck.SlideMaster.CustomLayouts.Item([int]$slideData.layout)
        for ($existingShapeIndex = $slide.Shapes.Count; $existingShapeIndex -ge 1; $existingShapeIndex--) {
            $slide.Shapes.Item($existingShapeIndex).Delete()
        }
        foreach ($item in $slideData.shapes) {
            if ($item.kind -eq 'picture') {
                $pictureFile = Join-Path (Split-Path -Parent $presentationRoot) ('screenshots\' + $item.filename)
                $pictureHeight = [single]($item.h * 72 / (1 - $item.crop_bottom / 100000))
                $shape = $slide.Shapes.AddPicture($pictureFile, 0, -1, [single]($item.x*72), [single]($item.y*72), [single]($item.w*72), $pictureHeight)
                $shape.PictureFormat.CropBottom = [single]($pictureHeight * $item.crop_bottom / 100000)
                $shape.Left = [single]($item.x*72)
                $shape.Top = [single]($item.y*72)
                $shape.AlternativeText = 'Existing project screenshot showing an order awaiting processing.'
                continue
            }
            $geometry = switch ($item.geom) { 'rightArrow' {33}; 'downArrow' {36}; default {1} }
            $shape = $slide.Shapes.AddShape($geometry, [single]($item.x*72), [single]($item.y*72), [single]($item.w*72), [single]($item.h*72))
            $shape.Name = 'ProjectShape-' + $item.id
            if ($item.fill) {
                $shape.Fill.Visible = -1
                $shape.Fill.Solid()
                $shape.Fill.ForeColor.RGB = Get-OfficeColor $item.fill
            } else { $shape.Fill.Visible = 0 }
            if ($item.stroke) {
                $shape.Line.Visible = -1
                $shape.Line.ForeColor.RGB = Get-OfficeColor $item.stroke
                $shape.Line.Weight = 0.75
            } else { $shape.Line.Visible = 0 }
            if ($item.text) {
                $frame = $shape.TextFrame2
                $frame.AutoSize = 0
                $frame.WordWrap = -1
                $frame.MarginLeft = [single]($item.margin * 72)
                $frame.MarginRight = [single]($item.margin * 72)
                $frame.MarginTop = [single]($item.margin * 72)
                $frame.MarginBottom = [single]($item.margin * 72)
                $frame.VerticalAnchor = if ($item.valign -eq 'ctr') {3} else {1}
                $range = $frame.TextRange
                $range.Text = $item.text.Replace("`n", "`r")
                $range.Font.Name = $item.font
                $range.Font.Size = [single]$item.size
                $range.Font.Bold = if ($item.bold) {-1} else {0}
                $range.Font.Fill.ForeColor.RGB = Get-OfficeColor $item.color
                $range.ParagraphFormat.Alignment = switch ($item.align) { 'ctr' {2}; 'r' {3}; default {1} }
                $range.ParagraphFormat.SpaceBefore = 0
                $range.ParagraphFormat.SpaceAfter = 0
                $range.ParagraphFormat.Bullet.Visible = 0
            }
        }
        $notesBody = $null
        foreach ($noteShape in $slide.NotesPage.Shapes) {
            if ($noteShape.Type -eq 14 -and $noteShape.PlaceholderFormat.Type -eq 2 -and $noteShape.HasTextFrame -eq -1) {
                $notesBody = $noteShape
                break
            }
        }
        if ($null -eq $notesBody) { $notesBody = $slide.NotesPage.Shapes.AddPlaceholder(2, 36, 360, 468, 300) }
        $notesRange = $notesBody.TextFrame.TextRange
        $notesRange.Text = [string]$slideData.title + "`r`r" + [string]$slideData.notes
    }
    $deck.SaveAs($deckPath, 24)
    $deck.Close()
    $deck = $powerPoint.Presentations.Open($deckPath, -1, 0, 0)
    for ($slideIndex = 1; $slideIndex -le $deck.Slides.Count; $slideIndex++) {
        $slide = $deck.Slides.Item($slideIndex)
        $slide.Export((Join-Path $previewPath ('slide-{0:D2}.png' -f $slideIndex)), 'PNG', 1600, 900)
        for ($shapeIndex = 1; $shapeIndex -le $slide.Shapes.Count; $shapeIndex++) {
            $shape = $slide.Shapes.Item($shapeIndex)
            $shapeCount++
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $frame = $shape.TextFrame2
                $range = $frame.TextRange
                $availableHeight = $shape.Height - $frame.MarginTop - $frame.MarginBottom
                $availableWidth = $shape.Width - $frame.MarginLeft - $frame.MarginRight
                if ($range.BoundHeight -gt ($availableHeight + 2) -or $range.BoundWidth -gt ($availableWidth + 2)) {
                    $issues += [pscustomobject]@{
                        slide = $slideIndex
                        shape = $shape.Name
                        text = $range.Text
                        boundHeight = [math]::Round($range.BoundHeight, 2)
                        availableHeight = [math]::Round($availableHeight, 2)
                        boundWidth = [math]::Round($range.BoundWidth, 2)
                        availableWidth = [math]::Round($availableWidth, 2)
                    }
                }
            }
        }
    }
    $deck.SaveAs($pdfPath, 32)
    $report = [pscustomobject]@{
        slides = $deck.Slides.Count
        shapes = $shapeCount
        textOverflowIssues = @($issues)
        pdf = $pdfPath
        previews = $previewPath
    }
    $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'validation-fixed-headers.json') -Encoding UTF8
    $report | ConvertTo-Json -Depth 5
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $powerPoint) {
        $powerPoint.AutomationSecurity = $priorSecurity
        if ($priorCount -eq 0 -and $powerPoint.Presentations.Count -eq 0) { $powerPoint.Quit() }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)
    }
}
