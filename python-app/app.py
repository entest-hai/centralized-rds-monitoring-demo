"""
haimtran 02/09/2024
simple app connecting to mysql
"""

import os
import time
from dotenv import load_dotenv
import mysql
import mysql.connector
from concurrent.futures import ThreadPoolExecutor
from random import choice
from string import ascii_uppercase

# load environment variables from .env file
load_dotenv()

# load db credentials from .env file
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
PASSWORD = os.getenv("PASSWORD")
USER_NAME = os.getenv("USER_NAME")


def create_db_connection():
    """
    create database connection, later on fetch credentials from AWS Secret.
    """
    # db connector
    connection = mysql.connector.connect(
        host=DB_HOST, user=USER_NAME, port=DB_PORT, password=PASSWORD, database=DB_NAME
    )
    # return
    return connection


def get_books(max_num_rows=100, max_length_content_display=16, DEBUG="OFF"):
    """
    get max number of books from books table
    """
    # get db connection
    connection = create_db_connection()
    # create cursor
    cursor = connection.cursor()
    # get books
    cursor.execute(
        "SELECT id, LEFT(content,%s) FROM books LIMIT %s",
        (
            max_length_content_display,
            max_num_rows,
        ),
    )
    # print books
    if DEBUG == "ON":
        for row in cursor.fetchall():
            print(row)
    # close connection
    connection.close()


def insert_books_long_text(id=10001, item_size=10, DEBUG="OFF"):
    """
    insert books with long text
    :param id: id of a book
    :item_size: size of a item in byte
    :DEBUG: ON show more information while running
    """
    # generate a random string with item_size bytes
    content = "".join(choice(ascii_uppercase) for i in range(item_size))
    # insert query
    # query = f'INSERT INTO books(id, content) VALUES({id}, "{content}")'
    # print thread id
    if DEBUG == "OFF":
        print(f"thread number {id}")
        pass
    # db connector
    connection = create_db_connection()
    # execute query
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO books(id, content) VALUES(%s, %s)",
        (
            id,
            content,
        ),
    )
    # must commit
    connection.commit()
    # close connection
    connection.close()


def load_test_write_only(num_loop=10, num_thread=10, item_size=1024, DEBUG="OFF"):
    """
    load test read only mysql
    :param num_loop: number of loop
    :param num_thread: number of thread
    :param item_size: size of item
    :param DEBUG: debug mode
    """
    for k in range(num_loop):
        print(f"look number {k}")
        # start id at kth loop - inserted k*num_thread items
        num_row_at_k_loop = num_thread * k
        with ThreadPoolExecutor(max_workers=num_thread) as executor:
            for thread_id in range(num_thread):
                id = num_row_at_k_loop + thread_id + 1
                executor.submit(insert_books_long_text, id, item_size, DEBUG)


def load_test_read_only_books(
    num_loop, num_thread, max_num_row, max_length_content_display=16, DEBUG="OFF"
):
    """
    load test for read only
    """
    for k in range(num_loop):
        print(f"loop number {k}")
        with ThreadPoolExecutor(max_workers=num_thread) as executor:
            for id in range(num_thread):
                executor.submit(
                    get_books, max_num_row, max_length_content_display, DEBUG
                )


if __name__ == "__main__":
    num_thread = 1
    max_num_row = 10
    max_length_content_display = 16
    DEBUG = "ON"
    k = 0
    while True:
        print(f"loop number {k}")
        k += 1
        get_books(
            max_num_rows=max_num_row,
            max_length_content_display=max_length_content_display,
            DEBUG=DEBUG,
        )
        # with ThreadPoolExecutor(max_workers=num_thread) as executor:
        #     for id in range(num_thread):
        #         executor.submit(
        #             get_books, max_num_row, max_length_content_display, DEBUG
        #         )
