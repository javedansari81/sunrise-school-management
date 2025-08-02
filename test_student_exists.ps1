# PowerShell script to check if specific student exists

# First, get authentication token
Write-Host "Getting authentication token..."
$loginPayload = @{
    email = "admin@sunriseschool.edu"
    password = "admin123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login-json" -Method POST -Body $loginPayload -ContentType "application/json"
    $loginData = $loginResponse.Content | ConvertFrom-Json
    $token = $loginData.access_token
    Write-Host "✅ Got authentication token successfully"
} catch {
    Write-Host "❌ Failed to get authentication token:"
    Write-Host "Error: $($_.Exception.Message)"
    exit 1
}

# Check specific student
Write-Host "Checking student with ID 5..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/students/5" -Method GET -Headers @{"Authorization" = "Bearer $token"}
    Write-Host "✅ Student found:"
    Write-Host $response.Content
} catch {
    Write-Host "❌ Error getting student:"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error Message: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody"
    }
}
