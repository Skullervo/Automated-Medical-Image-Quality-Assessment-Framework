# Medical Image Quality Assessment System

This project is an automated system for assessing the quality of medical ultra sound images using Python. It integrates with Orthanc as a DICOM server, connected to the hospital's PACS (Picture Archiving and Communication System), and uses PostgreSQL as the database. Additionally, it includes a web-based user interface for ease of use.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Future Work](#future-work)
- [Contributing](#contributing)
- [License](#license)

## Features

- Automaattinen ultraäänen kuvanlaadun arviointi
- Integration with Orthanc DICOM server
- Connectivity with hospital PACS [TODO]
- PostgreSQL database support
- Web-based user interface

## Architecture

The system consists of the following components:

1. **US Image Quality Assessment Module:** Python scripts and models to analyze and assess the quality of medical US images.
2. **Orthanc Server:** A DICOM server for storing and managing medical images.
3. **PostgreSQL Database:** A relational database for storing image quality assessment results and metadata.
4. **Web Interface:** A user-friendly web application for accessing and managing the analysis results.

## Technologies Used

- **Python** for backend processing and image quality assessment.
- **Django** as the web framework.
- **Orthanc** for DICOM server functionalities.
- **PostgreSQL** as the database.
- **HTML, CSS, JavaScript** for the web interface.
- **Bootstrap** for responsive web design.
- **pgAdmin** for managing PostgreSQL database.

## Prerequisites

Before you begin, ensure you have met the following requirements [TODO: confirm these]:

- Python 3.8 or higher
- Orthanc DICOM server
- PostgreSQL 12 or higher
- pgAdmin (optional, for database management)
- Docker (optional, for future containerized deployment)

## Installation [TODO: clone and test these]

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Skullervo/LV-automaatti.git
    cd LV-automaatti
    ```

2. **Set up the virtual environment and activate it:**
    ```bash
    python3 -m venv venvUS
    venvUS\Scripts\activate
    ```

3. **Install Python dependencies:**
    ```bash
    pip install -r Requirements.txt
    ```

4. **Set up Orthanc server:**
    - Follow the Orthanc [installation guide](https://book.orthanc-server.com/users/getting-started.html) to set up the server.

5. **Set up PostgreSQL:**
    - Install PostgreSQL and create a database (TODO: include all instructions how to configurate database):
        ```sql
        CREATE DATABASE <databaseName>;
        ```

6. **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

## Usage

# Server side

1. **Activate virtual environment if you haven't yet:**
   ```
   venvUS\Scripts\activate
   ```

2. **Run analyseServerData:**
   ```
   python analyseServerData.py
   ```

3. **Check results from pgAdmin or with python**

   

# Client side

1. **Start the Python application:**
    ```bash
    python  manage.py runserver
    ```
    
2. **Access the web interface:**
    Open your web browser and go to `http://127.0.0.1:8000/`.

## Configuration [TODO: confirm that every step is included and properly instructed]

### Orthanc Configuration

**TODO include instructions on how to install Orthanc and connect Orthanc to PACS**

1. **Install Orthanc:**

   - Visit the [Orthanc website](https://www.orthanc-server.com/) and download the installation package for your OS (e.g., Windows, macOS, Linux).
   - Follow the installation instructions provided to install the Orthanc server. This typically involves downloading and running the installer or using a package manager to install the package.

2. **Configure Orthanc:**

   - Open the Orthanc configuration file. This file is usually located at `/etc/orthanc/orthanc.json` or a similar directory depending on your installation environment.
   - Edit the configuration file to set up server settings, such as server name, port, and file paths.
   - Save and close the configuration file after making the necessary changes.

3. **Connect Orthanc to PACS:**

   - Ensure you have the PACS IP address, port, and AE title (Application Entity Title).
   - Add the PACS configuration to the Orthanc configuration file. This includes PACS server details and any required usernames and passwords.
   - Restart the Orthanc server to apply the changes.

4. **Test the Connection to PACS:**

   - Use the Orthanc web interface or command-line tools to verify the connection to PACS.
   - Send a test file to PACS and ensure it appears correctly.

### Connecting Orthanc Server to Analysis Code

1. **Configure Analysis Code to Use Orthanc:**

   - Ensure the analysis code can connect to the Orthanc server. This may require the server's IP address, port, and any authentication details.
   - Edit the configuration files or environment variables in the analysis code to point to the correct Orthanc server.

2. **Use Orthanc's REST API:**

   - Orthanc provides a RESTful API that your analysis code can use to retrieve, send, and manipulate image data.
   - Refer to the [Orthanc API documentation](https://book.orthanc-server.com/users/rest.html) and use appropriate API requests in your analysis code.

3. **Test the Compatibility of Analysis Code and Orthanc:**

   - Run tests with your analysis code to ensure it can communicate with the Orthanc server correctly.
   - Verify that analysis results are displayed correctly in both the Orthanc interface and PACS.

### Database Configuration

**TODO include instructions on how to install PostgreSQL and update the database connection settings**

1. **Install PostgreSQL:**

   - Visit the [PostgreSQL website](https://www.postgresql.org/download/) and download the installer for your operating system.
   - Follow the installation instructions provided to install PostgreSQL. This typically involves running the installer and configuring basic settings like the database superuser password.

2. **Configure PostgreSQL:**

   - After installation, open the PostgreSQL configuration file (usually `postgresql.conf` and `pg_hba.conf` located in the data directory).
   - Set the necessary configurations such as `listen_addresses` to allow remote connections and add appropriate authentication methods.
   - Restart the PostgreSQL server to apply the changes.

3. **Create a Database and User:**

   - Access the PostgreSQL shell using the command `psql`.
   - Create a new database and user with the necessary privileges:
     ```sql
     CREATE DATABASE mydatabase;
     CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
     GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;
     ```

4. **Update the Database Connection Settings in the Application:**

   - Open the `settings.py` file of your Python application.
   - Update the database connection settings to use PostgreSQL:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'mydatabase',
             'USER': 'myuser',
             'PASSWORD': 'mypassword',
             'HOST': 'localhost',
             'PORT': '5432',
         }
     }
     ```

5. **Test the Database Connection:**

   - Run your application and ensure it can connect to the PostgreSQL database.
   - Perform any necessary migrations or setup steps required by your application to initialize the database schema.

---

These instructions will guide you through the process of installing, configuring, and connecting PostgreSQL to your application.


## Future Work [TODO]

- **Docker Integration:** Future versions of this project will include Docker for containerized deployment, making it easier to manage and deploy the application in various environments.

## Contributing [TODO]

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
