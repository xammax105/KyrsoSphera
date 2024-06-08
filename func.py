from conf import cur,conn


def get_users_instructions_count(cur):
    cur.execute("""
        SELECT  Users.user_id, COUNT(Instructions.ID) AS num_instructions
        FROM Users
        LEFT JOIN Instructions ON Users.user_id = Instructions.author_id
        GROUP BY Users.user_id
        ORDER BY num_instructions DESC;
    """)
    return cur.fetchall()


def add_user(Email, Phone, Username,User_id, cur, con):
    # last_id = cur.execute('SELECT MAX (id) FROM Users').fetchone()

    # if last_id[0] is None:
    #     id = 1
    # else:
    #     id = last_id[0] + 1

    cur.execute(
        'INSERT INTO Users (Email, Phone, Username, User_id) VALUES (?, ?, ?, ?)',
        (Email, Phone, Username, User_id)
    )
    con.commit()

    cur.execute("SELECT * FROM Users;")
    one_result = cur.fetchall()
    for i in one_result:
        print(i)
