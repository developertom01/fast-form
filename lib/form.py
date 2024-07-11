import json
import os
import yaml

SupportedFileTypeJSON = ".json"
SupportedFileTypeYAML = ".yaml"
SupportedFileTypeYML = ".yml"


class InvalidFileFormatError(Exception):
    pass

class InvalidFilePathError(Exception):
    pass

class FormBuilder:

    def get_file_path(self):
        while True:
            file_path = input("Enter file path: ")
            if os.path.exists(file_path):
                return file_path
            

    def get_file_type(self, filename:str):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [SupportedFileTypeJSON,SupportedFileTypeYAML,SupportedFileTypeYML]:
            raise InvalidFileFormatError("Invalid file format. Only JSON or YAML files are supported.")
        
        return ext
    
    def read_yaml_file(self, path):
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return data


    def read_json(self,path:str):
        file_extension = os.path.splitext(path)[1].lower()

        if file_extension == ".json":
            with open(path, "r") as file:
                data = json.load(file)
                return data

    def validate(self, data):
        errors = {}
        for index, item in enumerate(data):
            error_list = []
            if "question" not in item or not isinstance(item["question"], str):
                error_list.append("Field 'question' is required and must be a string.")
            if "required" not in item or not isinstance(item["required"], bool):
                error_list.append("Field 'required' is required and must be a boolean.")
            if "type" not in item or item["type"] not in ["text", "number", "boolean", "choice"]:
                error_list.append("Field 'type' is required and must be one of: 'text', 'number', 'boolean', 'choice'.")
            if item["type"] == "choice":
                if "choices" not in item or not isinstance(item["choices"], list) or len(item["choices"]) < 1:
                    error_list.append("For 'type' == 'choice', 'choices' field is required and must be a non-empty list of strings.")
            if error_list:
                errors[index] = error_list
        return errors
    
    def validate_answer(self, item, answer):
        q_type = item["type"]
        required = item["required"]
        choices = item.get("choices", [])

        # Validate required field
        if required and not answer:
            return False, "This field is required."

        # Validate answer based on type
        if q_type == "text":
            if not isinstance(answer, str):
                return False, "Expected a string."
        elif q_type == "number":
            try:
                float(answer)
            except ValueError:
                return False, "Expected a number."
        elif q_type == "boolean":
            if answer.lower() not in ["true", "false"]:
                return False, "Expected 'true' or 'false'."
        elif q_type == "choice" and answer not in choices:
            return False, f"Expected one of the following choices: {', '.join(choices)}."

        return True, None
    
    def build_form(self, data):
        form = {}
        print("All questions with * is required")
        for index, item in enumerate(data):
            question = item["question"]
            q_type = item["type"]
            required = item["required"]
            choices = item.get("choices", [])

            # Display question and expected type
            if required:
                print(f"Question: *{question}")
            else:
                print(f"Question: {question}")
            print(f"Type: {q_type}")

            if q_type == "choice":
                print("Available choices:")
                for choice in choices:
                    print(f"- {choice}")

            # Prompt user for input
            while True:
                user_input = input("Your answer: ")
                (is_valid, error_message) = self.validate_answer(item=item,answer= user_input)

                if is_valid:
                    form[index] = user_input
                    break
                else:
                    print("Renter answer")
                    print(f"Error:{error_message}")

                print()
                 # Add a newline for clarity between questions
        return form
    
    
    def print_questions_and_answers(self, items, answers):
        for index, item in enumerate(items):
            question = item["question"]
            q_type = item["type"]
            choices = item.get("choices", [])
            answer = answers[index]

            print(f"Question {index + 1}: {question}")
            print(f"Type: {q_type}")
            if q_type == "choice":
                print("Available choices:")
                for choice in choices:
                    print(f"- {choice}")
            print(f"Your answer: {answer}")
            print()
    
    def write_questions_and_answers_to_file(self,path, items, answers):
        with open(path,"w") as f:
            for index, item in enumerate(items):
                question = item["question"]
                q_type = item["type"]
                choices = item.get("choices", [])
                answer = answers[index]

                f.write(f"Question {index + 1}: {question} ")
                f.write(f"Type: {q_type} ")

                if q_type == "choice":
                    f.write("Available choices: ")
                    for choice in choices:
                        f.write(f"- {choice} ")

                f.write(f"Your answer: {answer} ")
                f.write("\n")
# Example usage:
if __name__ == "__main__":
    form_builder = FormBuilder()
    form_builder.get_file_path()