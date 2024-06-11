from conf import cur,conn






def add_user(Email, Phone, Username,User_id, cur, con):
    last_id = cur.execute('SELECT MAX (id) FROM Users').fetchone()

    if last_id[0] is None:
        id = 1
    else:
        id = int(last_id[0]) + 1

    cur.execute(
        'INSERT INTO Users (ID,Email, Phone, Username, User_id) VALUES (?,?, ?, ?, ?)',
        (id, Email, Phone, Username, User_id)
    )
    con.commit()

    cur.execute("SELECT * FROM Users;")
    one_result = cur.fetchall()
    for i in one_result:
        print(i)
