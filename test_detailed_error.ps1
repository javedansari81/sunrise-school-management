# PowerShell script to get detailed error information

# First, get authentication token using OAuth2 form
Write-Host "Getting authentication token using OAuth2 form..."
$formData = @{
    username = "admin@sunriseschool.edu"
    password = "admin123"
}

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $formData -ContentType "application/x-www-form-urlencoded"
    $loginData = $loginResponse.Content | ConvertFrom-Json
    $token = $loginData.access_token
    Write-Host "✅ Got authentication token successfully"
} catch {
    Write-Host "❌ Failed to get authentication token:"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error Message: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody"
    }
    exit 1
}

# Now test the leave request creation with detailed error handling
$payload = @{
    applicant_id = 5
    applicant_type = "student"
    leave_type_id = 1
    start_date = "2025-08-01"
    end_date = "2025-08-02"
    reason = "Personal Time Off"
    parent_consent = $false
    emergency_contact_name = ""
    emergency_contact_phone = ""
    substitute_teacher_id = ""
    substitute_arranged = $false
    total_days = 2
} | ConvertTo-Json

Write-Host "Testing leave request creation API..."
Write-Host "Payload: $payload"

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/leaves/" -Method POST -Body $payload -ContentType "application/json" -Headers @{"Authorization" = "Bearer $token"}
    Write-Host "✅ Success! Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "❌ Error occurred:"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error Message: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody"
    }
}
