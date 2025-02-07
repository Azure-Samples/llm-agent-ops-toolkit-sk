# MYSQL Server Administration Script
# Description: This script is used to manage the MySQL server, like starting, stopping, and restarting the server.
#

# Download the MySql Sample Database
function Initialize-MySQLData {
    param (
        [string]$Url = "https://www.mysqltutorial.org/wp-content/uploads/2023/10/mysqlsampledatabase.zip",
        [string]$DestinationFolder = "./.local_data",
        [string]$ZipFilePath = "./mysqlsampledatabase.zip"
    )

    # Download the zip file
    Invoke-WebRequest -Uri $Url -OutFile $ZipFilePath

    # Extract the zip file
    Expand-Archive -Path $ZipFilePath -DestinationPath $DestinationFolder

    # Move the SQL file to the data folder
    Move-Item -Path (Join-Path -Path $DestinationFolder -ChildPath "mysqlsampledatabase.sql") -Destination $DestinationFolder

    # Remove the zip file
    Remove-Item -Path $ZipFilePath
}

# Start the MySQL server
function Start-MySQLServer {
    param (
        [string]$ContainerName = "mysql_server",
        [string]$RootPassword = "root_password"
    )

    docker run -d `
        --name $ContainerName `
        -e MYSQL_ROOT_PASSWORD=$RootPassword `
        -p 3306:3306 `
        mysql:latest
}

# Stop the MySQL server
function Stop-MySQLServer {
    param (
        [string]$ContainerName = "mysql_server"
    )

    docker stop $ContainerName
}

# Load the MySQL sample database
function Import-MySQLData {
    param (
        [string]$ContainerName = "mysql_server",
        [string]$Data = "./.local_data",
        [string]$RootPassword = "root_password"
    )

    $RootPassword = "-p${RootPassword}"

    Get-Content(Join-Path -Path $Data -ChildPath "mysqlsampledatabase.sql") | docker exec -i $ContainerName mysql -u root $RootPassword
}

# Restart the MySQL server
function Restart-MySQLServer {
    param (
        [string]$ContainerName = "mysql_server"
    )

    docker restart $ContainerName
}

# Main function with all the commands
function Main {
    param (
        [string]$Command = "start",
        [string]$ContainerName = "mysql_server",
        [string]$RootPassword = "root_password",
        [string]$Data = "./.local_data"
    )

    switch ($Command) {
        "start" {
            Start-MySQLServer -ContainerName $ContainerName -RootPassword $RootPassword
        }
        "stop" {
            Stop-MySQLServer -ContainerName $ContainerName
        }
        "restart" {
            Restart-MySQLServer -ContainerName $ContainerName
        }
        "init" {
            Initialize-MySQLData
        }
        "import" {
            Import-MySQLData -ContainerName $ContainerName -Data $Data -RootPassword $RootPassword
        }
        default {
            Write-Host "Invalid command: $Command"
        }
    }
}

# Call the main function
$RootPassword = Read-Host -Prompt "Enter the root password" -AsSecureString
$RootPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($RootPassword))
$RootPassword = $RootPassword -replace "`n", ""
Main -RootPassword $RootPassword @args
