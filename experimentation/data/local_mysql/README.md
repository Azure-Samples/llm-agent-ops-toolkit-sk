# Setup MySQL Locally for Development

Follow these steps to setup MySQL locally for development or experimentation.

## Pre-requisites

- [Docker](https://www.docker.com/products/docker-desktop)

## Steps

1. Start [MySQL server using Docker](https://hub.docker.com/_/mysql)

    ```bash
    docker run --name mysql-local -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag
    ```

1. Run the PowerShell script to create a database and user, provide the password when prompted

    ```bash
    mysql_server.ps1
    ```
