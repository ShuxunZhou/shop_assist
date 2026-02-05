from langchain_community.utilities import SQLDatabase

if __name__ == '__main__':
    db = SQLDatabase.from_uri(
        'mysql+pymysql://root:1234@localhost:3306/shop_assist'
    )

    # print(db.get_usable_table_names())
    # print(db.run('select * from products limit 2'))