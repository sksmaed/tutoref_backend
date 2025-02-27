# tutoref_backend

tutoref.tw backend in Express and FastAPI

## How to Start to Develop

1. Create a virtual environment and activate it:

    ```sh
    source venv/bin/activate
    ```

2. Stop the PostgreSQL service if it's running:

    ```sh
    systemctl stop postgresql
    ```

3. Change permissions for the PostgreSQL data directory if permission denied error appears:

    ```sh
    sudo chmod -R 777 /home/sks/tutoref/fastapi/postgres_data
    ```

4. Start the Docker containers:

    ```sh
    docker-compose up -d
    ```

5. Verify Elasticsearch is running by performing a search query:

    ```sh
    curl -X GET "http://localhost:9200/_cat/health"
    ```