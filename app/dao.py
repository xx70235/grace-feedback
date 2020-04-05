
import sqlite3
import logging

from app.modes import User
from app.config import Config as cfg

logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s', level=logging.WARNING)
mapped_class_dic = dict(user=User)


def get_conn():
    return sqlite3.connect(cfg.SQLLITE_DB_PATH)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE user
           (shop_id    CHAR(50) PRIMARY KEY     NOT NULL,
           shop_name    TEXT    NOT NULL,
           passwd       TEXT    NOT NULL,
           scope        TEXT    NOT NULL,
           access_token   TEXT     NOT NULL,
           shop_email    TEXT      NOT NULL,
           contact_url   TEXT      NOT NULL);''')
    print("Table user created successfully")
    conn.commit()
    cursor.close()
    conn.close()


def save_user(conn, user):
    if not user:
        logging.error("user is None!")
        return
    sql = "insert into user VALUES (?,?,?,?,?,?,?)"  # sql语句
    cursor = conn.cursor()  # 定义一个游标
    cursor.execute(sql, (user.shop_id, user.shop_name, user.passwd, user.scope,
                         user.access_token, user.shop_email, user.contact_url))  # 执行sql语句
    conn.commit()  # 提交数据库改动
    cursor.close()  # 关闭游标


def query_user_by_id(conn, shop_id):
    cursor = conn.cursor()
    rows = cursor.execute("SELECT shop_id, shop_name, passwd, scope, access_token, shop_email, contact_url  from user;")
    for row in rows:
        if row[0] == shop_id:
            return User(shop_id=row[0], shop_name=row[1], passwd=row[2], scope=row[3],
                        access_token=row[4], shop_email=row[5], contact_url=row[6])
    return None


def delete_user_by_id(conn, shop_id):
    cursor = conn.cursor()
    sql = "DELETE from user where shop_id={};".format(shop_id)
    cursor.execute(sql)
    conn.commit()
    logging.warning("delete shop_id: {} successful".format(shop_id))


def update_usr_by_id(conn, user):
    if not user:
        logging.error("user is None!")
        return False
    cursor = conn.cursor()
    sql = "UPDATE user set shop_name='{0}', passwd='{1}', scope='{2}', access_token='{3}', shop_email ='{4}', contact_url ='{5}' where shop_id='{6}';" \
        .format(user.shop_name, user.passwd, user.scope, user.access_token, user.shop_email, user.contact_url, user.shop_id)
    cursor.execute(sql)
    conn.commit()
    logging.warning("update user successful")
    return True


def update_user_email_contact_url(conn, shop_id, shop_email, contact_url):
    user = query_user_by_id(conn, shop_id)
    if not user:
        return False
    else:
        cursor = conn.cursor()
        sql = "UPDATE user set shop_email='{0}', contact_url='{1}' where shop_id='{2}'"\
            .format(shop_email, contact_url, shop_id)
        cursor.execute(sql)
        conn.commit()
        logging.warning("update email and contact_url successful")
        return True


def save_user_with_check(user):
    if not user or not isinstance(user, User) or not user.shop_id:
        return False
    else:
        conn_s = get_conn()
        shop_id = user.shop_id
        user_query = query_user_by_id(conn_s, shop_id)
        if user_query and isinstance(user_query, User):
            try:
                update_usr_by_id(conn_s, user)
                return True
            except Exception as e:
                logging.error("save user error, error message is {}".format(e), exc_info=True)
                return False
            finally:
                conn_s.close()
        else:
            try:
                save_user(conn_s, user)
                return True
            except Exception as e:
                logging.error("save user error, error message is {}".format(e), exc_info=True)
                return False
            finally:
                conn_s.close()


def query_user_with_close_by_id(shop_id):
    conn_q = get_conn()
    try:
        user_q = query_user_by_id(conn_q, shop_id)
        return user_q
    except Exception as e:
        logging.error("query_user_with_close_by_id method has error, the error message is {]".format(e), exc_info=True)
        return None
    finally:
        conn_q.close()


if __name__ == "__main__":
    init_db()
    # user = User(shop_id="1234510", shop_name="http-tankers.myshopify.com", passwd="12345678",
    #             scope="read_products,read_collection_listings,write_customers",
    #             access_token="sdfjlsfjklpxpj",
    #             shop_email="xudong_ftd@163.com",
    #             contact_url="https://http-tankers.myshopify.com/admin/pages/55621156997"
    #             )
    # result = save_user_with_check(user)
    # if result:
    #     print("save success")
    # else:
    #     print("save failed")
    # conn = get_conn()
    # delete_user_by_id(conn, shop_id="123457")
    # save_user(conn, user)
    # q_user = query_user_by_id(conn, shop_id="123457")
    # print(q_user.passwd)
    # print(q_user.access_token)
    # q_user.shop_email = "asqhaqs@163.com"
    # q_user.contact_url = "www.baidu.com"
    # #update_usr_by_id(conn, q_user)
    # update_user_email_contact_url(conn, shop_id="123457", shop_email="asqhaqs@163.com", contact_url="www.baidu.com")
    # q_user2 = query_user_by_id(conn, shop_id="123457")
    # print(q_user2.shop_email)
    # conn.close()


