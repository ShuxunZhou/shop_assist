from sqlalchemy import create_engine, inspect


class MySQLDatabaseManager:
    """
    MySQL 数据库管理器, 负责数据库连接和查询操作
    """

    def __init__(self, connection_string: str):
        """
        初始化MySQL数据库连接

        Args:
            connection_string (str): 数据库连接字符串
                mysql+pymysql://username:password@host:port/database
        """
        self.engine = create_engine(connection_string, pool_size=5, pool_recycle=3600)

    def get_table_names(self) -> list[str]:
        """
        获取数据库中的所有表名

        Returns:
            list: 表名列表
        """

        try:

            # 创建一个数据库映射对象,用于获取数据库的元数据
            inspctor = inspect(self.engine)
            return inspctor.get_table_names()

        except Exception as e:
            print(e)
            raise e

if __name__ == '__main__':
    username = "root"
    password = "1234"
    host = "127.0.0.1"
    port = 3306
    database = "world_data"

    connection_string = f"mysql+pymysql://username:password@host:port/database"
    manager = MySQLDatabaseManager(