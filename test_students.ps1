# PowerShell script to check available students

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

# Check available students
Write-Host "Checking available students..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/students/" -Method GET -Headers @{"Authorization" = "Bearer $token"}
    Write-Host "✅ Students API response:"
    Write-Host $response.Content
} catch {
    Write-Host "❌ Error getting students:"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error Message: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody"
    }
}
