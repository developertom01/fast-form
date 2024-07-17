# Fast-Form

Fast-Form is a web application for creating and managing forms. The project utilizes FastAPI for the HTTP server and Jina for some background tasks.

## Requirements

To run this project, you need the following installed:

- Python 3.8 or higher
- Docker (optional, for running with Docker)
- Git (for cloning the repository)

## Major Frameworks

### FastAPI
FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints. It is used here to handle HTTP requests and serve the web application.

### Jina
Jina is a cloud-native neural search framework for creating scalable deep learning search applications on the cloud. In this project, Jina is used for background tasks.

## Installation

### Clone the Repository

First, clone the repository to your local machine:

```sh
git clone https://github.com/developertom01/fast-form.git
cd fast-form
```

### Setting Up Virtual Environment (Optional but Recommended)

Create a virtual environment to manage dependencies:

```sh
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies

Install the necessary Python packages using pip:

```sh
pip install -r requirements.txt
```

### Environment Variables

Copy the `.env.example` file to `.env` and update it with your configuration:

```sh
cp .env.example .env
```

### Database Setup

Make sure you have a PostgreSQL database running and update your `.env` file with the correct database connection details.

### Running Migrations

Run the database migrations to set up the database schema:

```sh
python scripts/migrate_db_tables.py
```

## Running the HTTP Server

### Using Uvicorn

You can run the FastAPI server using Uvicorn, a lightning-fast ASGI server:

```sh
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Using Docker

Alternatively, you can use Docker to run the server. Ensure you have Docker installed and running on your machine.

#### Building the Docker Image

```sh
docker build -t fast-form .
```

#### Running the Docker Container

```sh
docker run -d --name fast-form -p 8000:8000 fast-form
```

### Accessing the Application

Once the server is running, you can access the application in your web browser at `http://localhost:8000`.

## Directory Structure

- `app/cli/`: CLI-related scripts and models.
- `app/http/`: HTTP-related scripts and routes.
- `app/models/`: Data models.
- `config.py`: Configuration settings.
- `server.py`: The main entry point for the FastAPI server.
- `requirements.txt`: Python dependencies.
- `scripts/`: Http server entry point.
- `/bin/cli.py`: Cli entry point
- `templates/`: HTML templates for the web application.

## Contributing

Contributions are welcome! Please fork the repository and open a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
