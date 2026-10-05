import sqlite3


DATABASE = "careermatch.db"


def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def create_database():

    connection = get_db_connection()

    # ==================================================
    # USERS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'job_seeker',

            education TEXT DEFAULT '',

            location TEXT DEFAULT '',

            experience TEXT DEFAULT '',

            resume_filename TEXT DEFAULT ''

        )
        """
    )

    # ==================================================
    # SKILLS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS skills (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            skill_name TEXT NOT NULL,

            FOREIGN KEY (user_id)
            REFERENCES users (id)

        )
        """
    )

    # ==================================================
    # JOBS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            recruiter_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            company TEXT NOT NULL,

            description TEXT NOT NULL,

            required_skills TEXT NOT NULL,

            location TEXT NOT NULL,

            salary TEXT DEFAULT '',

            job_type TEXT DEFAULT 'Full Time',

            created_at TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (recruiter_id)
            REFERENCES users (id)

        )
        """
    )

    # ==================================================
    # APPLICATIONS TABLE
    # ==================================================

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER NOT NULL,

            user_id INTEGER NOT NULL,

            status TEXT DEFAULT 'Applied',

            applied_at TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (job_id)
            REFERENCES jobs (id),

            FOREIGN KEY (user_id)
            REFERENCES users (id),

            UNIQUE(job_id, user_id)

        )
        """
    )

    connection.commit()

    connection.close()


if __name__ == "__main__":

    create_database()

    print(
        "Database created successfully!"
    )