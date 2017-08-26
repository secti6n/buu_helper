from sqlobject import StringCol, SQLObject, ForeignKey, sqlhub, connectionForURI, mysql, IntCol, TinyIntCol
import buu_config

class class_model(object):

    MySQLConnection = mysql.builder()
    sqlhub.processConnection =  MySQLConnection(user = buu_config.config.mysql_username, password = buu_config.config.mysql_password,
                                                host = buu_config.config.mysql_addr, db = buu_config.config.mysql_database)

    class User(SQLObject):
        userName = StringCol()

    class Card(SQLObject):
        user_name = StringCol()
        password = StringCol()
        user = ForeignKey('User')

    class Switch(SQLObject):
        function_name = StringCol()
        function_enable = TinyIntCol()
        function_option = StringCol()
        user = ForeignKey('User')

    def init():
        if not sqlhub.processConnection.tableExists('user'):
            class_model.User.createTable()

        if not sqlhub.processConnection.tableExists('card'):
            class_model.Card.createTable()

        if not sqlhub.processConnection.tableExists('switch'):
            class_model.Switch.createTable()
