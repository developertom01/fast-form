from app.cli.login import authenticate, login
from app.cli.logout import logout
from app.cli.build_form import (build,publish_form, delete_form, unpublish_form, perform_list_forms_itr)
import time
import argparse

def add_args(parser):
    parser.add_argument(
        "action", help="Action to execute", choices=["signin", "signout", "build","delete","publish","unpublish", "list"]
    )
    parser.add_argument("--file", "-f", required=False, help="Add file path")
    parser.add_argument("--id", "-i", required=False, help="Form id")


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
                print("You have successfully logged out 👋🏼")
                quit(0)
    elif args.action == "build":
        user = authenticate()
        print("Hello! 👋🏼", user)
        time.sleep(1.5)
        try:

            build(path=args.file, session=user.token)
        except Exception as e:
            if str(e) == "NOT_LOGGED_IN":
                print("Authentication failed 🚪. Redirecting you to login ...")
                logout()
                time.sleep(1)
                user = login()
                time.sleep(0.5)
                build(path=args.file,session=user.token)
            else:
                print("ERROR 😕 : ",str(e))
    elif args.action == "delete":
        user = authenticate()
        if not args.id:
            print("--id or -i is required for this action")
        try:
            delete_form(form_id=args.id,session=user.token)
        except Exception as e:
            if str(e) == "NOT_LOGGED_IN":
                print("Authentication failed 🚪. Redirecting you to login ...")
                logout()
                time.sleep(1)
                user = login()
                time.sleep(0.5)
                delete_form(form_id=args.id,session=user.token)
            else:
                print("ERROR 😕 : ",str(e))
    elif args.action == "publish":
        user = authenticate()
        if not args.id:
            print("--id or -i is required for this action")
        try:
            publish_form(form_id=args.id,session=user.token)
        except Exception as e:
            if str(e) == "NOT_LOGGED_IN":
                print("Authentication failed 🚪. Redirecting you to login ...")
                logout()
                time.sleep(1)
                user = login()
                time.sleep(0.5)
                publish_form(form_id=args.id,session=user.token)
            else:
                print("ERROR 😕 : ",str(e))

    elif args.action == "unpublish":
        user = authenticate()
        if not args.id:
            print("--id or -i is required for this action")
        try:
            unpublish_form(form_id=args.id,session=user.token)
        except Exception as e:
            if str(e) == "NOT_LOGGED_IN":
                print("Authentication failed 🚪. Redirecting you to login ...")
                logout()
                time.sleep(1)
                user = login()
                time.sleep(0.5)
                unpublish_form(form_id=args.id,session=user.token)
            else:
                print("ERROR 😕 : ",str(e))

    elif args.action == "list":
        user = authenticate()
        if not args.id:
            print("--id or -i is required for this action")
        try:
            perform_list_forms_itr(session=user.token)
        except Exception as e:
            if str(e) == "NOT_LOGGED_IN":
                print("Authentication failed 🚪. Redirecting you to login ...")
                logout()
                time.sleep(1)
                user = login()
                time.sleep(0.5)
                perform_list_forms_itr(session=user.token)
            else:
                print("ERROR 😕 : ",str(e))
    else:
        print("Unknown command 🤷🏽‍♂️")
        quit()


# Entry point
if __name__ == "__main__":
    main()
