**TODO: Include all instructions for server side configurations**


## PostgreSQL Configuration

0. First, download PostgreSQL for your operating system from: [PostgreSQL Downloads](https://www.postgresql.org/download/) and follow instructions.

1. During the installation, set a *username* and *password* for your PostgreSQL.


## Orthanc Configuration

0. First, download Orthanc for your operating system from: [Orthanc Downloads](https://www.orthanc-server.com/download.php) and follow instructions.

1. After installation navigate to orthanc configuration folder `\Orthanc Server\Configuration`.

2. Open `postgresql.json`.

3. Change the `Username` and `Password` fields to match your PostgreSQL username and password. Ensure the PostgreSQL port is set to 5432.

    ```json
    {
        "PostgreSQL" : {
            "EnableIndex" : true,
            "EnableStorage" : true,
            "Host" : "localhost",
            "Port" : 5432,
            "Database" : "Orthanc",
            "Username" : "postgres",
            "Password" : "password",
            "Lock" : false
        }
    }
    ```

## Continue PostgreSQL Configuration

1. Start PostgreSQL from the command line:

    ```sh
    "navigate\to\PostgreSQL\15\bin\psql" -U <your PostgreSQL username>
    ```

2. Create a new database for the analysis results:

    ```sql
    CREATE DATABASE "QA-results";
    ```

3. List databases to ensure `QA-results` is created:

    ```sql
    \l
    ```

4. Connect to the Orthanc database:

    ```sql
    \c Orthanc
    ```

5. Create the `series` table and `orthancseriesids` view for analyses:

    ```sql
    CREATE TABLE series (
        internalid SERIAL PRIMARY KEY,
        resourcetype VARCHAR(255),
        publicid VARCHAR(255)
    );

    CREATE VIEW orthancseriesids AS
    SELECT internalid, resourcetype, publicid
    FROM resources
    WHERE resourcetype = 2;
    ```
