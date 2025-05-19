from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                PRAGMA foreign_keys=off;

                CREATE TABLE accounts_user_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password varchar(128) NOT NULL,
                    last_login datetime NULL,
                    is_superuser bool NOT NULL,
                    email varchar(254) NOT NULL UNIQUE,
                    is_staff bool NOT NULL,
                    is_active bool NOT NULL,
                    date_joined datetime NOT NULL,
                    age integer NULL,
                    region varchar(50) NULL,
                    subregion varchar(50) NULL
                );

                INSERT INTO accounts_user_new (
                    id, password, last_login, is_superuser, email, is_staff,
                    is_active, date_joined, age, region, subregion
                )
                SELECT
                    id, password, last_login, is_superuser, email, is_staff,
                    is_active, date_joined, age, region, subregion
                FROM accounts_user;

                DROP TABLE accounts_user;
                ALTER TABLE accounts_user_new RENAME TO accounts_user;

                PRAGMA foreign_keys=on;
            """,
            reverse_sql="-- Not reversible",
        ),
    ]
