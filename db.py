import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=config.DB_PORT
    )


def verify_user(username, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    result = cur.fetchone()
    conn.close()
    return result     # dict이면 로그인 성공, None이면 실패


def verify_admin(userid, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM admin WHERE userid=%s AND password=%s",
        (userid, password)
    )
    result = cur.fetchone()
    conn.close()
    return result

