# IEPS project

The following project is the implementation of the multi threaded web crawler developed in Python.

**DOCKER SETUP:**

1. Download docker
2. Create folder docker with subfolder init-scripts which contains the crawldb.sql file from moodle
3. Run command in cmd (Windows):
   docker run --name postgresql-wier \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_USER=user \
    -e POSTGRES_DB=crawler
   -v %cd%/pgdata:/var/lib/postgresql/data \
    -v %cd%/init-scripts:/docker-entrypoint-initdb.d \
    -p 5432:5432 \
    -d postgres:12.2
4. You can check container's logs with: docker logs -f postgresql-wier
5. To log into database and execute SQL statements: docker exec -it postgresql-wier psql -U postgres

**RUN PROJECT:**

1. **cd web_crawler**
1. **.\env\Scripts\activate** (pip install virtualenv)
1. **python main.py "number of workers"**
