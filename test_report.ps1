# UTF-8로 출력 + 입력 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 사용자 입력 받기


# FastAPI 서버 POST 요청

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/generate" `
    -Method POST `
    -Body (@{text="2025 Q4 sales"; companyName="Samsung Electronics"} | ConvertTo-Json) `
    -ContentType "application/json; charset=utf-8"

# 결과 출력
Write-Output "===== Report ====="
Write-Output $response.reportText
Write-Output "===== Charts ====="
Write-Output ($response.charts | ConvertTo-Json -Depth 5)


$reportHtml = "<html><body><pre>$($response.reportText)</pre></body></html>"
$reportHtml | Out-File -FilePath "report.html" -Encoding UTF8
Start-Process "report.html"