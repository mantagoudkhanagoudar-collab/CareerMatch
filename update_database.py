import sqlite3


DATABASE = "careermatch.db"


connection = sqlite3.connect(DATABASE)


try:

    connection.execute(
        """
        ALTER TABLE users
        ADD COLUMN api_token TEXT DEFAULT ''
        """
    )

    connection.commit()

    print("Database updated successfully!")
    print("API token column added to users table.")


except sqlite3.OperationalError as error:

    if "duplicate column name" in str(error).lower():

        print("API token column already exists.")

    else:

        print("Database update failed.")
        print(error)


finally:

    connection.close()