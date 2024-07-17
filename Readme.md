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
- `scripts/`: Various utility scripts.
- `templates/`: HTML templates for the web application.


# JSON Schema for Form Building

This document outlines the structure of the JSON file used to create a form in the Fast-Form application. Each form consists of various elements such as questions, options, and metadata. The JSON schema ensures that the data is validated and properly structured before being processed.

## Root Object

The root object of the JSON file contains the following properties:

- `title` (string): The title of the form.
- `description` (string, optional): A brief description of the form.
- `questions` (array): A list of questions included in the form.

```json
{
  "title": "Survey Form",
  "description": "A form to collect survey responses.",
  "questions": [
    {
      // Question objects
    }
  ]
}
```

## Question Object

Each question object within the `questions` array contains the following properties:

- `id` (string): A unique identifier for the question.
- `type` (string): The type of question. Supported types include `text`, `multiple_choice`, `checkbox`, and `dropdown`.
- `label` (string): The question text displayed to the user.
- `required` (boolean, optional): Indicates whether the question is required. Default is `false`.
- `options` (array, optional): A list of options for `multiple_choice`, `checkbox`, and `dropdown` question types.

### Example

```json
{
  "id": "q1",
  "type": "multiple_choice",
  "label": "What is your favorite color?",
  "required": true,
  "options": [
    {
      // Option objects
    }
  ]
}
```

## Option Object

Each option object within the `options` array contains the following properties:

- `value` (string): The value of the option.
- `label` (string): The text displayed for the option.

### Example

```json
{
  "value": "red",
  "label": "Red"
}
```

## Full Example

Here is a full example of a JSON file used to build a form:

```json
{
  "title": "Customer Feedback Form",
  "description": "Please provide your feedback.",
  "questions": [
    {
      "id": "q1",
      "type": "text",
      "label": "What is your name?",
      "required": true
    },
    {
      "id": "q2",
      "type": "multiple_choice",
      "label": "How satisfied are you with our service?",
      "required": true,
      "options": [
        {
          "value": "very_satisfied",
          "label": "Very Satisfied"
        },
        {
          "value": "satisfied",
          "label": "Satisfied"
        },
        {
          "value": "neutral",
          "label": "Neutral"
        },
        {
          "value": "dissatisfied",
          "label": "Dissatisfied"
        },
        {
          "value": "very_dissatisfied",
          "label": "Very Dissatisfied"
        }
      ]
    },
    {
      "id": "q3",
      "type": "checkbox",
      "label": "Which of our products do you use?",
      "options": [
        {
          "value": "product_a",
          "label": "Product A"
        },
        {
          "value": "product_b",
          "label": "Product B"
        },
        {
          "value": "product_c",
          "label": "Product C"
        }
      ]
    },
    {
      "id": "q4",
      "type": "dropdown",
      "label": "How did you hear about us?",
      "options": [
        {
          "value": "friend",
          "label": "Friend"
        },
        {
          "value": "advertisement",
          "label": "Advertisement"
        },
        {
          "value": "social_media",
          "label": "Social Media"
        },
        {
          "value": "other",
          "label": "Other"
        }
      ]
    }
  ]
}
```

## Validation

The JSON schema is validated using the `CreateFormRequest` model in the `app/http/form.py` file. This ensures that the provided JSON adheres to the required structure and data types before being processed to create a form.

# YAML Schema for Form Building

This document outlines the structure of the YAML file used to create a form in the Fast-Form application. Each form consists of various elements such as questions, options, and metadata. The YAML schema ensures that the data is validated and properly structured before being processed.

## Root Object

The root object of the YAML file contains the following properties:

- `title` (string): The title of the form.
- `description` (string, optional): A brief description of the form.
- `questions` (array): A list of questions included in the form.

```yaml
title: Survey Form
description: A form to collect survey responses.
questions:
  - # Question objects
```

## Question Object

Each question object within the `questions` array contains the following properties:

- `id` (string): A unique identifier for the question.
- `type` (string): The type of question. Supported types include `text`, `multiple_choice`, `checkbox`, and `dropdown`.
- `label` (string): The question text displayed to the user.
- `required` (boolean, optional): Indicates whether the question is required. Default is `false`.
- `options` (array, optional): A list of options for `multiple_choice`, `checkbox`, and `dropdown` question types.

### Example

```yaml
id: q1
type: multiple_choice
label: What is your favorite color?
required: true
options:
  - # Option objects
```

## Option Object

Each option object within the `options` array contains the following properties:

- `value` (string): The value of the option.
- `label` (string): The text displayed for the option.

### Example

```yaml
value: red
label: Red
```

## Full Example

Here is a full example of a YAML file used to build a form:

```yaml
title: Customer Feedback Form
description: Please provide your feedback.
questions:
  - id: q1
    type: text
    label: What is your name?
    required: true
  - id: q2
    type: multiple_choice
    label: How satisfied are you with our service?
    required: true
    options:
      - value: very_satisfied
        label: Very Satisfied
      - value: satisfied
        label: Satisfied
      - value: neutral
        label: Neutral
      - value: dissatisfied
        label: Dissatisfied
      - value: very_dissatisfied
        label: Very Dissatisfied
  - id: q3
    type: checkbox
    label: Which of our products do you use?
    options:
      - value: product_a
        label: Product A
      - value: product_b
        label: Product B
      - value: product_c
        label: Product C
  - id: q4
    type: dropdown
    label: How did you hear about us?
    options:
      - value: friend
        label: Friend
      - value: advertisement
        label: Advertisement
      - value: social_media
        label: Social Media
      - value: other
        label: Other
```

## Validation

The YAML schema is validated using the `CreateFormRequest` model in the `app/http/form.py` file. This ensures that the provided YAML adheres to the required structure and data types before being processed to create a form.
