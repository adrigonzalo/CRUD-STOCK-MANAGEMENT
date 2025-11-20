"""
In this script just include code related with:
- Database connection.
- Create tables
"""

# Categories Table
'''
            CREATE TABLE IF NOT EXISTS "products" (
                      "id" INTEGER NOT NULL UNIQUE,
                      "name" TEXT NOT NULL UNIQUE,
                      "price" REAL NOT NULL,
                      PRIMARY KEY("id" AUTOINCREMENT)
                      )
            '''