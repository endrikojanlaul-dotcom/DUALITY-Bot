from bot.db import init_db


def main():
    print("Initializing database (creating tables)...")
    init_db()
    print("Done.")


if __name__ == '__main__':
    main()
