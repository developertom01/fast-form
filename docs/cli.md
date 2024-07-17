# CLI Commands Documentation

The Fast-Form project includes several CLI commands for interacting with the form building and management features. These commands are located in the `app/cli/` directory and are executed via the main CLI entry point in `bin/cli.py`.

## CLI Command Overview

The CLI commands include functionalities such as user login, user logout, form building, and uploading forms. Below is a detailed description of each command.

### Command: `signin`

#### Description

Logs in a user by prompting for their email and password, and stores the session token for future authenticated requests.

#### Usage

```sh
python -m bin.cli signin
```

### Command: `signout`

#### Description

Logs out the current user by invalidating the session token.

#### Usage

```sh
python -m bin.cli logout
```

### Command: `build`

#### Description

Delete a form

#### Usage

```sh
python -m bin.cli build -f <path to file>
```

#### Options

- `--file` or `-f` (required): Path to YAML or JSON file

### Command: `publish`

#### Description

Publish a form

#### Usage

```sh
python -m bin.cli publish -i <from id>
```

#### Options

- `--id` or `-i` (required): Id of form

### Command: `unpublish`

#### Description

Unpublish a form

#### Usage

```sh
python -m bin.cli unpublish -i <from id>
```

#### Options

- `--id` or `-i` (required): Id of form

### Command: `delete`

#### Description

Delete a form

#### Usage

```sh
python -m bin.cli delete -i <from id>
```

#### Options

- `--id` or `-i` (required): Id of form

### Command: `list`

#### Description

List forms uploaded

#### Usage

```sh
python -m bin.cli list
```

### Command: `authenticate`

#### Description

Authenticates the user by either checking the existing login status or prompting for login credentials if not already logged in.

#### Usage

```sh
python -m bin.cli signin
```

## Example Workflow

Here is an example workflow demonstrating how to use the CLI commands:

1. **Login**:

   ```sh
   python -m bin.cli login
   ```

   This command prompts for your email and password, then logs you in and stores the session token.

2. **Build and Upload Form**:

   ```sh
   python -m bin.cli build -f form.yaml
   ```

   This command builds a form from the specified YAML file and uploads it to the server. If you are not logged in, it will prompt for your login credentials.

3. **Logout**:

   ```sh
   python -m bin.cli signout
   ```

   This command logs you out by invalidating the session token.

## Help

For detailed help on any command, you can use the `--help` option. For example:

```sh
python -m bin.cli build --help
```

This will display usage information and available options for the `build-form` command.
