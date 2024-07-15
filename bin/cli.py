from app.cli.login import authenticate, login
from app.cli.logout import logout
from app.cli.build_form import build
from lib.form import FormBuilder
import time
import argparse


def add_args(parser):
    parser.add_argument(
        "action", help="Action to execute", choices=["signin", "signout", "build"]
    )
    parser.add_argument("--file", "-f", required=False, help="Add file path")


def main():
    parser = argparse.ArgumentParser()
    add_args(parser)
    args = parser.parse_args()

    if args.action == "signin":
        user = login()
        print("Welcome ", user)
        return
    if args.action == "signout":
        confirmation = input(
            "Are you sure you want to logout? Type Y or Yes to continue: "
        )
        if confirmation.lower() == "y" or confirmation.lower() == "yes":
            try:
                logout()
            finally:
                print("You have successfully logged out")
                quit(0)
    else:
        user = authenticate()
        print("Hello ", user)
        time.sleep(1.5)

        data = build(path=args.file)

        print(data)


# Entry point
if __name__ == "__main__":
    main()
