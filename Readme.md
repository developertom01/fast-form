# Form Builder

- This application contains program that allows you to load form questions from a json or yaml file and load them for users.

## Installation

- Create python virtual environment and activate

- Install Dependencies

```sh
pip install -r requirements.txt
```

## Support

- The application supports valid json and yaml files

- Supported data types are text,number, boolean and choice

## Formats

- json

```json

[
    {
        "question": "string", // Required
        "type": "text|number|boolean|choice", // Required
        "required": "boolean", 
        "choices": ["choice"]
    }
]

```

- yaml

```yaml
    - question: string #Required
      type: text|number|boolean|choice #Required
      required: boolean
      choices:
        - choice

```

### Note

When type is set to `choice`, choices is required and must contain at least one item

## Run application

```sh
python main.py
```

- Application will prompt you to add file path, go ahead and input a valid json file path of your choice or you can use the sample.json provided.
