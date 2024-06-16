from conf import password,user
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText






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


def send_email_notification(data,letter):
    # Настройки для почтового сервера
    smtp_server = "smtp.yandex.com"
    smtp_port = 587
    smtp_user = user
    smtp_password = password

    # Получатель
    recipient_email = data['email']

    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = recipient_email
    msg['Subject'] = "KyrsoSphera"

    body = letter
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Установка соединения с сервером
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        # Отправка письма
        text = msg.as_string()
        server.sendmail(smtp_user, recipient_email, text)

        # Закрытие соединения
        server.quit()

        print("Письмо успешно отправлено ------------------------------------------")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e} -----------------------------")



