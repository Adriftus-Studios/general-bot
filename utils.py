import secrets
import json
import discord

db = secrets.MONGO_CLIENT


# Class to call that logs to the database
class Logger:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            message = args.content
            data = {
                'message': message
            }
            with open('data.json', 'w+', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Arguments of the func: {args}")
            print(f"Result to be logged: {self.func(*args)}")
            print(f"Send to discord to emulate console: \n{self.func(*args)} was successfully logged")

        except Exception as err:
            print(err)

