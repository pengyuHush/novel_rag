# Test creating a novel via API
$body = @{
    title = "测试小说"
    author = "测试作者"
    description = "这是一个测试小说"
    tags = @("测试", "样例")
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/novels" -Method Post -Body $body -ContentType "application/json"

Write-Host "Created novel:"
$response | ConvertTo-Json -Depth 5

