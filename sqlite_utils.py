import sqlite3
import json

limit_show_collection = 5

path_to_db = "database.db"


def update(table: str, name: str, value, where: str = "", ser_json: bool = False):
    with sqlite3.connect(path_to_db) as db:
        if where:
            where = "WHERE " + where
        req = f"UPDATE {table} SET {name} = ? {where};"
        if ser_json:
            db.execute(req, (json.dumps(value),))
        else:
            db.execute(req, (value,))


def get_all(table: str, par: str = '*', where: str = ""):
    with sqlite3.connect(path_to_db) as db:
        if where:
            where = "WHERE " + where
        return db.execute(f"SELECT {par} FROM {table} {where};").fetchall()


def get_one(table: str, par: str = '*', where: str = "", deser: bool = False):
    with sqlite3.connect(path_to_db) as db:
        if where:
            where = "WHERE " + where
        return db.execute(f"SELECT {par} FROM {table} {where};").fetchone()


def user_in_database(id_user):
    with sqlite3.connect(path_to_db) as db:
        res = db.execute("SELECT * FROM user_state WHERE id = ?;", (id_user,))
        if res.fetchone() is None:
            return False
        else:
            return True


def get_state(id_user):
    with sqlite3.connect(path_to_db) as db:
        res = db.execute("SELECT * FROM user_state WHERE id = ?;", (id_user,))
        user = res.fetchone()
        if user is None:
            db.execute("INSERT INTO user_state VALUES (?, 'main_menu');", (id_user,))
            return 'main_menu'
        else:
            return user[1]


def set_state(id_user, new_state):
    with sqlite3.connect(path_to_db) as db:
        res = db.execute("SELECT * FROM user_state WHERE id = ?;", (id_user,))
        user = res.fetchone()
        if user is None:
            db.execute("INSERT INTO user_state VALUES (?,'main_menu');", (id_user,))
        db.execute("UPDATE user_state SET state = ? WHERE id = ?;", (new_state, id_user))
        db.commit()


def get_page_collection(page=1):
    with sqlite3.connect(path_to_db) as db:
        arr_collection = db.execute("SELECT * FROM collection ORDER BY name ASC;").fetchall()

        # (strExp) Если коллекций вообще нету
        if len(arr_collection) == 0:
            return "Коллекций нету"

        max_count_page = int(len(arr_collection) / limit_show_collection) + int(
            bool(len(arr_collection) % limit_show_collection))

        # (strExp) Если столько страниц вообще нету
        if (page < 0 or page > max_count_page):
            return "Столько страниц нету"

        if (page == 0):
            page = max_count_page

        page_collection = []
        num_page = 0

        for collection in arr_collection:

            page_collection.append(collection)

            if len(page_collection) == limit_show_collection:

                num_page += 1

                if (num_page == page):
                    break
                else:
                    page_collection.clear()

        return page_collection


def get_count_collection():
    with sqlite3.connect(path_to_db) as db:
        return len(db.execute("SELECT * FROM collection").fetchall())


def get_costume_collection(id_collection=0):
    with sqlite3.connect(path_to_db) as db:
        return db.execute("SELECT * FROM costume WHERE id_collection = ?;", (id_collection,)).fetchall()


def get_costume(id_costume):
    with sqlite3.connect(path_to_db) as db:
        return db.execute("SELECT * FROM costume WHERE id_costume = ?;", (id_costume,)).fetchone()


def its_moder(id_user) -> bool:
    with sqlite3.connect(path_to_db) as db:
        result_id = db.execute("SELECT value FROM config WHERE name = ?;", ("arr_moder_id",)).fetchone()[0]
        for id_arr in json.loads(result_id):
            if id_user == id_arr:
                return True
    return its_admin(id_user)


def add_moder(id_user: int):
    with sqlite3.connect(path_to_db) as db:
        arr_moder = json.loads(db.execute("SELECT value FROM config WHERE name = ?;", ("arr_moder_id",)).fetchone()[0])
        arr_moder.append(id_user)
        db.execute("UPDATE config SET value = ? WHERE name = ?;", (json.dumps(arr_moder), "arr_moder_id"))


def del_moder(id_user: int):
    with sqlite3.connect(path_to_db) as db:
        arr_moder = json.loads(db.execute("SELECT value FROM config WHERE name = ?;", ("arr_moder_id",)).fetchone()[0])
        arr_moder.remove(id_user)
        db.execute("UPDATE config SET value = ? WHERE name = ?;", (json.dumps(arr_moder), "arr_moder_id"))


def its_admin(id_user) -> bool:
    with sqlite3.connect(path_to_db) as db:
        return id_user == int(db.execute("SELECT value FROM config WHERE name = ?;", ("admin_id",)).fetchone()[0])


def unique_collection_name(name_collection) -> bool:
    with sqlite3.connect(path_to_db) as db:
        db.execute("SELECT * FROM collection WHERE name = ?;", (name_collection,)).fetchall()
        if len(db.execute("SELECT * FROM collection WHERE name = ?;", (name_collection,)).fetchall()):
            return False
        else:
            return True


def set_collection(name_collection):
    with sqlite3.connect(path_to_db) as db:
        db.execute("INSERT INTO collection (name) VALUES (?);", (name_collection,)).fetchone()


def get_name_collection(id_collection):
    with sqlite3.connect(path_to_db) as db:
        return db.execute("SELECT name FROM collection WHERE id = ?;", (id_collection,)).fetchone()


def unique_costume_name(name_costume):
    with sqlite3.connect(path_to_db) as db:
        db.execute("SELECT * FROM costume WHERE name = ?;", (name_costume,)).fetchall()
        if len(db.execute("SELECT * FROM costume WHERE name = ?;", (name_costume,)).fetchall()):
            return False
        else:
            return True


def set_costume(name, description, arr_photo, id_collection) -> int:
    with sqlite3.connect(path_to_db) as db:
        db.execute(
            "INSERT INTO costume (json_arr_img,description,name,id_collection) VALUES (?,?,?,?)",
            (arr_photo, description, name, id_collection)
        )

        res = db.execute(
            "SELECT id_costume FROM costume WHERE name = ? AND id_collection = ?",
            (name, id_collection)
        ).fetchone()

        return int(res[0])


def remove_collection(id_collection) -> int:
    with sqlite3.connect(path_to_db) as db:
        arr_costume = db.execute("SELECT * FROM costume WHERE id_collection = ?;", (id_collection,)).fetchall()
        db.execute("DELETE FROM costume WHERE id_collection = ?;", (id_collection,))
        db.execute("DELETE FROM collection WHERE id = ?;", (id_collection,))

        count = 0

        for costume in arr_costume:
            db.execute(
                "INSERT INTO costume (json_arr_img,description,name,id_collection,id_costume) VALUES (?,?,?,?,?)",
                (costume[4], costume[3], costume[2], 0, costume[0])
            )
            count += 1

        return count


def remove_full_collection(id_collection):
    with sqlite3.connect(path_to_db) as db:
        db.execute("DELETE FROM costume WHERE id_collection = ?;", (id_collection,))
        db.execute("DELETE FROM collection WHERE id = ?;", (id_collection,))


def remove_costume(id_costume):
    with sqlite3.connect(path_to_db) as db:
        db.execute("DELETE FROM costume WHERE id_costume = ?;", (id_costume,))


def update_username(id_user: int, username: str):
    with sqlite3.connect(path_to_db) as db:
        res = db.execute("SELECT name FROM username WHERE id = ?;", (id_user,)).fetchone()
        if res is None:
            db.execute("INSERT INTO username VALUES (?,?);", (id_user, username))
        else:
            if res[0] != username:
                db.execute("UPDATE username SET name = ? WHERE id = ?;", (username, id_user))


def get_username(id_user: int) -> str:
    with sqlite3.connect(path_to_db) as db:
        res = db.execute("SELECT name FROM username WHERE id = ?;", (id_user,)).fetchone()
        if res is None:
            return f"Без имени (id{id_user})"
        else:
            return res[0]


def get_contact_manager() -> str:
    with sqlite3.connect(path_to_db) as db:
        return db.execute("SELECT value FROM config WHERE name = 'contact_url';").fetchone()[0]




