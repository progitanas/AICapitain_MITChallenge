# AICaptain Full Stack Deployment Script (PowerShell)
# For Windows with Docker Desktop

param(
    [string]$Environment = "development",
    [string]$Action = "deploy"
)

# Colors
$Green = @{ ForegroundColor = "Green" }
$Yellow = @{ ForegroundColor = "Yellow" }
$Red = @{ ForegroundColor = "Red" }

Write-Host "═══════════════════════════════════════" @Yellow
Write-Host "   AICaptain Full Stack Deployment" @Yellow
Write-Host "═══════════════════════════════════════" @Yellow
Write-Host ""

# Function to check command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Check Docker
if (-not (Test-CommandExists docker)) {
    Write-Host "✗ Docker not installed or not in PATH" @Red
    Write-Host "Download Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
}
Write-Host "✓ Docker installed" @Green

# Check Docker Compose
if (-not (Test-CommandExists docker-compose)) {
    Write-Host "✗ Docker Compose not installed or not in PATH" @Red
    exit 1
}
Write-Host "✓ Docker Compose installed" @Green

Write-Host ""

# Handle actions
switch ($Action.ToLower()) {
    "deploy" {
        Write-Host "Building Docker images..." @Yellow
        docker-compose build
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Failed to build images" @Red
            exit 1
        }
        Write-Host "✓ Images built successfully" @Green
        Write-Host ""

        Write-Host "Starting services..." @Yellow
        docker-compose up -d
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Failed to start services" @Red
            exit 1
        }
        Write-Host "✓ Services started successfully" @Green
        Write-Host ""

        Start-Sleep -Seconds 5

        Write-Host "Checking service health..." @Yellow
        
        try {
            $backendHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($backendHealth.StatusCode -eq 200) {
                Write-Host "✓ Backend API healthy" @Green
            }
            else {
                Write-Host "✗ Backend API unhealthy (HTTP $($backendHealth.StatusCode))" @Red
            }
        }
        catch {
            Write-Host "✗ Backend API unreachable" @Red
        }

        try {
            $frontendHealth = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -ErrorAction SilentlyContinue
            if ($frontendHealth.StatusCode -eq 200 -or $frontendHealth.StatusCode -eq 301) {
                Write-Host "✓ Frontend app healthy" @Green
            }
            else {
                Write-Host "✗ Frontend app unhealthy (HTTP $($frontendHealth.StatusCode))" @Red
            }
        }
        catch {
            Write-Host "✗ Frontend app unreachable" @Red
        }

        Write-Host ""
        Write-Host "═══════════════════════════════════════" @Yellow
        Write-Host "Deployment Complete!" @Green
        Write-Host "═══════════════════════════════════════" @Yellow
        Write-Host ""
        Write-Host "Access your application:" @Yellow
        Write-Host "  Frontend:  http://localhost:3000" @Green
        Write-Host "  Backend:   http://localhost:8000" @Green
        Write-Host "  API Docs:  http://localhost:8000/api/v1/docs" @Green
        Write-Host ""
        Write-Host "Useful commands:" @Yellow
        Write-Host "  Logs:      docker-compose logs -f" @Yellow
        Write-Host "  Stop:      docker-compose down" @Yellow
        Write-Host "  Status:    docker-compose ps" @Yellow
        break
    }
    
    "stop" {
        Write-Host "Stopping services..." @Yellow
        docker-compose down
        Write-Host "✓ Services stopped" @Green
        break
    }
    
    "logs" {
        Write-Host "Displaying logs (Ctrl+C to exit)..." @Yellow
        docker-compose logs -f
        break
    }
    
    "status" {
        Write-Host "Service status:" @Yellow
        docker-compose ps
        break
    }
    
    "rebuild" {
        Write-Host "Rebuilding images without cache..." @Yellow
        docker-compose build --no-cache
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Images rebuilt successfully" @Green
            Write-Host "Starting services..." @Yellow
            docker-compose up -d
            Write-Host "✓ Services started" @Green
        }
        break
    }
    
    default {
        Write-Host "Usage: .\deploy.ps1 [-Action] [deploy|stop|logs|status|rebuild]" @Yellow
        Write-Host ""
        Write-Host "Examples:" @Yellow
        Write-Host "  .\deploy.ps1 -Action deploy     # Deploy full stack" @Yellow
        Write-Host "  .\deploy.ps1 -Action logs       # View logs" @Yellow
        Write-Host "  .\deploy.ps1 -Action stop       # Stop services" @Yellow
        Write-Host "  .\deploy.ps1 -Action status     # Check status" @Yellow
        Write-Host "  .\deploy.ps1 -Action rebuild    # Rebuild from scratch" @Yellow
    }
}
