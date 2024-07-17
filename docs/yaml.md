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
