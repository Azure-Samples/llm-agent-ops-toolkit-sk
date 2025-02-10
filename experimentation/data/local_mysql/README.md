# Setup MySQL Locally for Development

Follow these steps to setup MySQL locally for development or experimentation.

## Pre-requisites

- [Docker](https://www.docker.com/products/docker-desktop)

## Steps

1. Run the PowerShell commands to create a database and user, provide the password when prompted

    ```pwsh
    cd ./experimentation/data/local_mysql/
    ./mysql_server.ps1 init
    ./mysql_server.ps1 start
    ./mysql_server.ps1 import
    ```
