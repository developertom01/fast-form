from lib.form import (
    FormBuilder,
    InvalidFilePathError,
    InvalidFileFormatError,
    SupportedFileTypeYAML,
    SupportedFileTypeJSON,
    SupportedFileTypeYML,
)


def build(path:str  = ""):
    form_builder = FormBuilder()
    # Prompt user for file path and check if file path exists
    if path is None or path == "":
        try:
            path = form_builder.get_file_path()
        except InvalidFilePathError as e:
            print(e)
            return

    try:
        file_type = form_builder.get_file_type(path)
    except InvalidFileFormatError as e:
        print(e)
        return

    if file_type == SupportedFileTypeJSON:
        data = form_builder.read_json(path=path)
        # Read json
    elif file_type == SupportedFileTypeYAML or file_type == SupportedFileTypeYML:
        data = form_builder.read_yaml_file(path=path)

    # Validate input from questions uploaded

    questions_validation_error = form_builder.validate(data=data)

    if len(questions_validation_error) != 0:
        print(questions_validation_error)
        return

    return data