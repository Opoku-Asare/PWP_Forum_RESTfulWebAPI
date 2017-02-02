'''
Created on 13.02.2013

Modified on 05.02.2016

Provides the database API to access the forum persistent data.

@author: ivan
'''

from datetime import datetime
import time, sqlite3, re, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/forum.db'
DEFAULT_SCHEMA = "db/forum_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/forum_data_dump.sql"


class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/forum.db*

    '''
    def __init__(self, db_path=None):
        '''
        '''

        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return Connection(self.db_path)

    def remove_database(self):
        '''
        Removes the database file from the filesystem.

        '''
        if os.path.exists(self.db_path):
            #THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        #THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM messages")
            cur.execute("DELETE FROM users")
            #NOTE since we have ON DELETE CASCADE BOTH IN users_profile AND
            #friends, WE DO NOT HAVE TO WORRY TO CLEAR THOSE TABLES.

    #METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
    def create_tables(self, schema=None):
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/forum_schema_dump.sql* is utilized.

        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with open(schema) as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then *db/forum_data_dump.sql* is utilized.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open (dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    #METHODS TO CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT
    def create_messages_table(self):
        '''
        Create the table ``messages`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE messages(message_id INTEGER PRIMARY KEY AUTOINCREMENT, \
                    title TEXT, body TEXT, timestamp INTEGER, \
                    ip TEXT, timesviewed INTEGER, \
                    reply_to INTEGER, \
                    user_nickname TEXT, user_id INTEGER, \
                    editor_nickname TEXT, \
                    FOREIGN KEY(reply_to) REFERENCES messages(message_id) \
                    ON DELETE CASCADE, \
                    FOREIGN KEY(user_id,user_nickname) \
                    REFERENCES users(user_id, nickname) ON DELETE SET NULL)'
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_users_table(self):
        '''
        Create the table ``users`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                    nickname TEXT UNIQUE, regDate INTEGER,\
                                    lastLogin INTEGER, timesviewed INTEGER,\
                                    UNIQUE(user_id, nickname))'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_users_profile_table(self):
        '''
        Create the table ``users_profile`` programmatically, without using
        .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        '''
        #TASK3 TODO#
        Write the SQL Statement to create users_profile table
        '''

        stmnt = 'CREATE TABLE users_profile(user_id INTEGER PRIMARY KEY, \
                    firstname TEXT, lastname TEXT, \
                    email TEXT, website TEXT, \
                    picture TEXT, mobile TEXT, \
                    skype TEXT, birthday TEXT, \
                    residence TEXT, gender TEXT, \
                    signature TEXT, avatar TEXT, \
                    FOREIGN KEY(user_id) REFERENCES users(user_id) \
                    ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_friends_table(self):
        '''
        Create the table ``friends`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE friends (user_id INTEGER, friend_id INTEGER, \
                     PRIMARY KEY(user_id, friend_id), \
                     FOREIGN KEY(user_id) REFERENCES users(user_id) \
                     ON DELETE CASCADE, \
                     FOREIGN KEY(friend_id) REFERENCES users(user_id) \
                     ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None


class Connection(object):
    '''
    API to access the Forum database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    '''
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()

    #FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        try:
            #Create a cursor to receive the database values
            cur = self.con.cursor()
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print "Foreign Keys status: %s" % 'ON' if is_activated else 'OFF'
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    def unset_foreign_keys_support(self):
        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    #HELPERS
    #Here the helpers that transform database rows into dictionary. They work
    #similarly to ORM

    #Helpers for messages
    def _create_message_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``messageid``: id of the message (int)
            * ``title``: message's title
            * ``body``: message's text
            * ``timestamp``: UNIX timestamp (long integer) that specifies when
              the message was created.
            * ``replyto``: The id of the parent message. String with the format
              msg-{id}. Its value can be None.
            * ``sender``: The nickname of the message's creator.
            * ``editor``: The nickname of the message's editor.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        message_id = 'msg-' + str(row['message_id'])
        message_replyto = 'msg-' + str(row['reply_to']) \
            if row['reply_to'] is not None else None
        message_sender = row['user_nickname']
        message_editor = row['editor_nickname']
        message_title = row['title']
        message_body = row['body']
        message_timestamp = row['timestamp']
        message = {'messageid': message_id, 'title': message_title,
                   'timestamp': message_timestamp, 'replyto': message_replyto,
                   'body': message_body, 'sender': message_sender,
                   'editor': message_editor}
        return message

    def _create_message_list_object(self, row):
        '''
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``messageid``, ``title``,
            ``timestamp`` and ``sender``.

        '''
        message_id = 'msg-' + str(row['message_id'])
        message_sender = row['user_nickname']
        message_title = row['title']
        message_timestamp = row['timestamp']
        message = {'messageid': message_id, 'title': message_title,
                   'timestamp': message_timestamp, 'sender': message_sender}
        return message

    #Helpers for users
    def _create_user_object(self, row):
        '''
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'registrationdate':,'nickname':'',
                                   'signature':'','avatar':''},
                'restricted_profile':{'firstname':'','lastname':'','email':'',
                                      'website':'','mobile':'','skype':'',
                                      'birthday':'','residence':'','gender':'',
                                      'picture':''}
                }

            where:

            * ``registrationdate``: UNIX timestamp when the user registered in
                                 the system (long integer)
            * ``nickname``: nickname of the user
            * ``signature``: text chosen by the user for signature
            * ``avatar``: name of the image file used as avatar
            * ``firstanme``: given name of the user
            * ``lastname``: family name of the user
            * ``email``: current email of the user.
            * ``website``: url with the user's personal page. Can be None
            * ``mobile``: string showing the user's phone number. Can be None.
            * ``skype``: user's nickname in skype. Can be None.
            * ``residence``: complete user's home address.
            * ``picture``: file which contains an image of the user.
            * ``gender``: User's gender ('male' or 'female').
            * ``birthday``: string containing the birthday of the user.

            Note that all values are string if they are not otherwise indicated.

        '''
        reg_date = row['regDate']
        return {'public_profile': {'registrationdate': reg_date,
                                   'nickname': row['nickname'],
                                   'signature': row['signature'],
                                   'avatar': row['avatar']},
                'restricted_profile': {'firstname': row['firstname'],
                                       'lastname': row['lastname'],
                                       'email': row['email'],
                                       'website': row['website'],
                                       'mobile': row['mobile'],
                                       'skype': row['skype'],
                                       'birthday': row['birthday'],
                                       'residence': row['residence'],
                                       'gender': row['gender'],
                                       'picture': row['picture']}
                }

    def _create_user_list_object(self, row):
        '''
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``registrationdate`` and
            ``nickname``

        '''
        return {'registrationdate': row['regDate'], 'nickname': row['nickname']}

    #API ITSELF
    #Message Table API.
    def get_message(self, messageid):
        '''
        Extracts a message from the database.

        :param messageid: The id of the message. Note that messageid is a
            string with format ``msg-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_message_object` or None if the message with target
            id does not exist.
        :raises ValueError: when ``messageid`` is not well formed

        '''
        #Extracts the int which is the id for a message in the database
        match = re.match(r'msg-(\d{1,3})', messageid)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM messages WHERE message_id = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (messageid,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return self._create_message_object(row)

    def get_messages(self, nickname=None, number_of_messages=-1,
                     before=-1, after=-1):
        '''
        Return a list of all the messages in the database filtered by the
        conditions provided in the parameters.

        :param nickname: default None. Search messages of a user with the given
            nickname. If this parameter is None, it returns the messages of
            any user in the system.
        :type nickname: str
        :param number_of_messages: default -1. Sets the maximum number of
            messages returning in the list. If set to -1, there is no limit.
        :type number_of_messages: int
        :param before: All timestamps > ``before`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type before: long
        :param after: All timestamps < ``after`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type after: long

        :return: A list of messages. Each message is a dictionary containing
            the following keys:

            * ``messageid``: string with the format msg-\d{1,3}.Id of the
                message.
            * ``sender``: nickname of the message's author.
            * ``title``: string containing the title of the message.
            * ``timestamp``: UNIX timestamp (long int) that specifies when the
                message was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        :raises ValueError: if ``before`` or ``after`` are not valid UNIX
            timestamps

        '''
        #Create the SQL Statement build the string depending on the existence
        #of nickname, numbero_of_messages, before and after arguments.
        query = 'SELECT * FROM messages'
          #Nickname restriction
        if nickname is not None or before != -1 or after != -1:
            query += ' WHERE'
        if nickname is not None:
            query += " user_nickname = '%s'" % nickname
          #Before restriction
        if before != -1:
            if nickname is not None:
                query += ' AND'
            query += " timestamp < %s" % str(before)
          #After restriction
        if after != -1:
            if nickname is not None or before != -1:
                query += ' AND'
            query += " timestamp > %s" % str(after)
          #Order of results
        query += ' ORDER BY timestamp DESC'
          #Limit the number of resulst return
        if number_of_messages > -1:
            query += ' LIMIT ' + str(number_of_messages)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Build the return object
        messages = []
        for row in rows:
            message = self._create_message_list_object(row)
            messages.append(message)
        return messages

    def delete_message(self, messageid):
        '''
        Delete the message with id given as parameter.

        :param str messageid: id of the message to remove.Note that messageid
            is a string with format ``msg-\d{1,3}``
        :return: True if the message has been deleted, False otherwise
        :raises ValueError: if the messageId has a wrong format.

        '''
        #Extracts the int which is the id for a message in the database
        match = re.match(r'msg-(\d{1,3})', messageid)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))
        '''
        #TASK5 TODO:#
        * Implement this method.
        * HINTS:
           * To remove a message use the DELETE sql command
           * To check if the message has been previously deleted you can check
             the size of the rows returned in the cursor. You can check it from
             the attribute cursor.rowcount. If the rowcount is < 1 means that
             no row has been  deleted and hence you should return False.
             Otherwise return True.
           * Be sure that you commit the current transaction
        * HOW TO TEST: Use the database_api_tests_message. The following tests
          must pass without failure or error:
            * test_delete_message
            * test_delete_message_malformed_id
            * test_delete_message_noexisting_id
        '''
        #Create the SQL statment
        stmnt = 'DELETE FROM messages WHERE message_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (messageid,)
        cur.execute(stmnt, pvalue)
        #Commit the message
        self.con.commit()
        #Check that the message has been deleted
        if cur.rowcount < 1:
            return False
        #Return true if message is deleted.
        return True

    def modify_message(self, messageid, title, body, editor="Anonymous"):
        '''
        Modify the title, the body and the editor of the message with id
        ``messageid``

        :param str messageid: The id of the message to remove. Note that
            messageid is a string with format msg-\d{1,3}
        :param str title: the message's title
        :param str body: the message's content
        :param str editor: default 'Anonymous'. The nickname of the person
            who is editing this message. If it is not provided "Anonymous"
            will be stored in db.
        :return: the id of the edited message or None if the message was
              not found. The id of the message has the format ``msg-\d{1,3}``,
              where \d{1,3} is the id of the message in the database.
        :raises ValueError: if the messageid has a wrong format.

        '''
        #Extracts the int which is the id for a message in the database
        match = re.match(r'msg-(\d{1,3})', messageid)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))
        '''
        TASK5 TODO:
        * Finish this method
        HINTS:
        * Remember that to modify the value of a row you have to use the UPDATE
         sql command
        * You have to modify just the title, the body and the
          editor_nickname of the message
        * You can check if a database has been modifed after an UPDATE using
          the attribute cur.rowcount. If rowcount < 1, there has not been an
          update.
        * Remember to activate the foreign key support
        HOW TO TEST: Use the database_api_tests_message. The following tests
                     must pass without failure or error:
                        * test_modify_message
                        * test_modify_message_malformed_id
                        * test_modify_message_noexisting_id
        '''
        #Create the SQL statment
        stmnt = 'UPDATE messages SET title=? , body=?, editor_nickname=?\
                 WHERE message_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (title, body, editor, messageid)
        cur.execute(stmnt, pvalue)
        self.con.commit()
        if cur.rowcount < 1:
            return None
        return 'msg-'+str(messageid)

    def create_message(self, title, body, sender="Anonymous",
                       ipaddress="0.0.0.0", replyto=None):
        '''
        Create a new message with the data provided as arguments.

        :param str title: the message's title
        :param str body: the message's content
        :param str sender: the nickname of the person who is editing this
            message. If it is not provided "Anonymous" will be stored in db.
        :param str ipaddress: The ip address from which the message was created.
            It is a string with format "xxx.xxx.xxx.xxx". If no ipaddress is
            provided then database will store "0.0.0.0"
        :param str replyto: Only provided if this message is an answer to a
            previous message (parent). Otherwise, Null will be stored in the
            database. The id of the message has the format msg-\d{1,3}

        :return: the id of the created message or None if the message could not
            be created, or the ``replyto`` parameter does not exist. Note that 
            the returned value is a string with the format msg-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        :raises ValueError: if the replyto has a wrong format.

        '''
        #Extracts the int which is the id for a message in the database
        if replyto is not None:
            match = re.match('msg-(\d{1,3})', replyto)
            if match is None:
                raise ValueError("The replyto is malformed")
            replyto = int(match.group(1))
        '''
        TASK5 TODO:
        * Finish this method
        HINTS
        * Remember that add a new row you must use the INSERT command.
         sql command
        * You have to add the following fields in the INSERT command:
            - title -> passed as argument
            - body -> passed as argument
            - timestamp -> Use the expression:
                           time.mktime(datetime.now().timetuple()) to get
                           current timestamp.
            - ip -> passed as argument ipaddres
            - timesviewed -> Use the int 0.
            - reply_to -> passed as argument replyto. It is recommended
                          that you check that the message exists.
                          Otherwise, return None.
                          To check if the message exists check the messages
                          table using the following SQL Query:
                          'SELECT * from messages WHERE message_id = ?'
            - user_nickname -> passed as sender argument
            - user_id -> You must find the user_id accessing the users table.
                         Use the following statement:
                         'SELECT user_id from users WHERE nickname = ?'
        * You can extract the id of the new row using lastrowid property
          in cursor
        * Be sure that you commit the current transaction
        * Remember to activate the foreign key support
        RECOMMENDED PROCEDURE:
          - Activate foreign key support
          - Calculate current timestamp
          - Check that the replyto message exists, otherwise return None
            'SELECT * from messages WHERE message_id = ?'
          - Get the user_id from a given nickname
            'SELECT user_id from users WHERE nickname = ?'
          - Append the new message to the database using a INSERT statement

        * HOW TO TEST: Use the database_api_tests_message. The following tests
                       must pass without failure or error:
                * test_create_message
                * test_append_answer
                * test_append_answer_malformed_id
                * test_append_answer_noexistingid
        '''
        #Create the SQL statment
          #SQL to test that the message which I am answering does exist
        query1 = 'SELECT * from messages WHERE message_id = ?'
          #SQL Statement for getting the user id given a nickname
        query2 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement for inserting the data
        stmnt = 'INSERT INTO messages (title,body,timestamp,ip, \
                 timesviewed,reply_to,user_nickname,user_id) \
                 VALUES(?,?,?,?,?,?,?,?)'
          #Variables for the statement.
          #user_id is obtained from first statement.
        user_id = None
        timestamp = time.mktime(datetime.now().timetuple())
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #If exists the replyto argument, check that the message exists in
        #the database table
        if replyto is not None:
            pvalue = (replyto,)
            cur.execute(query1, pvalue)
            messages = cur.fetchall()
            if len(messages) < 1:
                return None
        #Execute SQL Statement to get userid given nickname
        pvalue = (sender,)
        cur.execute(query2, pvalue)
        #Extract user id
        row = cur.fetchone()
        if row is not None:
            user_id = row["user_id"]
        #Generate the values for SQL statement
        pvalue = (title, body, timestamp, ipaddress, 0, replyto, sender,
                  user_id)
        #Execute the statement
        cur.execute(stmnt, pvalue)
        self.con.commit()
        #Extract the id of the added message
        lid = cur.lastrowid
        #Return the id in
        return 'msg-' + str(lid) if lid is not None else None

    def append_answer(self, replyto, title, body, sender="Anonymous",
                      ipaddress="0.0.0.0"):
        '''
        Same as :py:meth:`create_message`. The ``replyto`` parameter is not
        a keyword argument, though.

        :param str replyto: Only provided if this message is an answer to a
            previous message (parent). Otherwise, Null will be stored in the
            database. The id of the message has the format msg-\d{1,3}
        :param str title: the message's title
        :param str body: the message's content
        :param str sender: the nickname of the person who is editing this
            message. If it is not provided "Anonymous" will be stored in db.
        :param str ipaddress: The ip address from which the message was created.
            It is a string with format "xxx.xxx.xxx.xxx". If no ipaddress is
            provided then database will store "0.0.0.0"

        :return: the id of the created message or None if the message could not
            be created, or the ``replyto`` parameter does not exist. Note that 
            the returned value is a string with the format msg-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        :raises ValueError: if the replyto has a wrong format.

        '''
        return self.create_message(title, body, sender, ipaddress, replyto)

    #MESSAGE UTILS
    def get_sender(self, messageid):
        '''
        Get the information of the user who sent a message which id is
        ``messageid``

        :param str messageid: Id of the message to search. Note that messageid
            is a string with the format msg-\d{1,3}.

        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'registrationdate':,'nickname':'',
                                   'signature':'','avatar':''},
                'restricted_profile':{'firstname':'','lastname':'','email':'',
                                      'website':'','mobile':'','skype':'',
                                      'age':'','residence':'','gender':'',
                                      'picture':''}
                }

            where:

            * ``registrationdate``: UNIX timestamp when the user registered in
                                 the system (long integer)
            * ``nickname``: nickname of the user
            * ``signature``: text chosen by the user for signature
            * ``avatar``: name of the image file used as avatar
            * ``firstanme``: given name of the user
            * ``lastname``: family name of the user
            * ``email``: current email of the user.
            * ``website``: url with the user's personal page. Can be None
            * ``mobile``: string showing the user's phone number. Can be None.
            * ``skype``: user's nickname in skype. Can be None.
            * ``residence``: complete user's home address.
            * ``picture``: file which contains an image of the user.
            * ``gender``: User's gender ('male' or 'female').
            * ``birthday``: string containing the birthday of the user.

            Note that all values are string if they are not otherwise indicated.
            In the case that it is an unregistered user the dictionary just
            contains the key ``nickname``;

        '''
        raise NotImplementedError("")

    def contains_message(self, messageid):
        '''
        Checks if a message is in the database.

        :param str messageid: Id of the message to search. Note that messageid
            is a string with the format msg-\d{1,3}.
        :return: True if the message is in the database. False otherwise.

        '''
        return self.get_message(messageid) is not None

    def get_message_time(self, messageid):
        '''
        Get the time when the message was sent.

        :param str messageid: Id of the message to search. Note that messageid
            is a string with the format msg-\d{1,3}.
        :return: message time as a string or None if that message does not
            exist.
        :raises ValueError: if messageId is not well formed
        '''
        raise NotImplementedError("")

    #ACCESSING THE USER and USER_PROFILE tables
    def get_users(self):
        '''
        Extracts all users in the database.

        :return: list of Users of the database. Each user is a dictionary
            that contains two keys: ``nickname``(str) and ``registrationdate``
            (long representing UNIX timestamp). None is returned if the database
            has no users.

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the users
        query = 'SELECT users.*, users_profile.* FROM users, users_profile \
                 WHERE users.user_id = users_profile.user_id'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Process the response.
        users = []
        for row in rows:
            users.append(self._create_user_list_object(row))
        return users

    def get_user(self, nickname):
        '''
        Extracts all the information of a user.

        :param str nickname: The nickname of the user to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the user given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement for retrieving the user information
        query2 = 'SELECT users.*, users_profile.* FROM users, users_profile \
                  WHERE users.user_id = ? \
                  AND users_profile.user_id = users.user_id'
          #Variable to be used in the second query.
        user_id = None
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #Extract the user id
        row = cur.fetchone()
        if row is None:
            return None
        user_id = row["user_id"]
        # Execute the SQL Statement to retrieve the user invformation.
        # Create first the valuse
        pvalue = (user_id, )
        #execute the statement
        cur.execute(query2, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        return self._create_user_object(row)

    def delete_user(self, nickname):
        '''
        Remove all user information of the user with the nickname passed in as
        argument.

        :param str nickname: The nickname of the user to remove.

        :return: True if the user is deleted, False otherwise.

        '''
        #Create the SQL Statements
          #SQL Statement for deleting the user information
        query = 'DELETE FROM users WHERE nickname = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (nickname,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    def modify_user(self, nickname, user):
        '''
        Modify the information of a user.

        :param str nickname: The nickname of the user to modify
        :param dict user: a dictionary with the information to be modified. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {'public_profile':{'registrationdate':,'signature':'',
                                       'avatar':''},
                    'restricted_profile':{'firstname':'','lastname':'',
                                          'email':'', 'website':'','mobile':'',
                                          'skype':'','age':'','residence':'',
                                          'gender':'', 'picture':''}
                    }

                where:

                * ``registrationdate``: UNIX timestamp when the user registered
                    in the system (long integer)
                * ``signature``: text chosen by the user for signature
                * ``avatar``: name of the image file used as avatar
                * ``firstanme``: given name of the user
                * ``lastname``: family name of the user
                * ``email``: current email of the user.
                * ``website``: url with the user's personal page. Can be None
                * ``mobile``: string showing the user's phone number. Can be
                    None.
                * ``skype``: user's nickname in skype. Can be None.
                * ``residence``: complete user's home address.
                * ``picture``: file which contains an image of the user.
                * ``gender``: User's gender ('male' or 'female').
                * ``birthday``: string containing the birthday of the user.

            Note that all values are string if they are not otherwise indicated.

        :return: the nickname of the modified user or None if the
            ``nickname`` passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
                #Create the SQL Statements
           #SQL Statement for extracting the userid given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement to update the user_profile table
        query2 = 'UPDATE users_profile SET firstname = ?,lastname = ?, \
                                           email = ?,website = ?, \
                                           picture = ?,mobile = ?, \
                                           skype = ?,birthday = ?,residence = ?, \
                                           gender = ?,signature = ?,avatar = ?\
                                           WHERE user_id = ?'
        #temporal variables
        user_id = None
        p_profile = user['public_profile']
        r_profile = user['restricted_profile']
        _firstname = r_profile.get('firstname', None)
        _lastname = r_profile.get('lastname', None)
        _email = r_profile.get('email', None)
        _website = r_profile.get('website', None)
        _picture = r_profile.get('picture', None)
        _mobile = r_profile.get('mobile', None)
        _skype = r_profile.get('skype', None)
        _birthday = r_profile.get('birthday', None)
        _residence = r_profile.get('residence', None)
        _gender = r_profile.get('gender', None)
        _signature = p_profile.get('signature', None)
        _avatar = p_profile.get('avatar', None)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #Only one value expected
        row = cur.fetchone()
        #if does not exist, return
        if row is None:
            return None
        else:
            user_id = row["user_id"]
            #execute the main statement
            pvalue = (_firstname, _lastname, _email, _website, _picture,
                      _mobile, _skype, _birthday ,_residence, _gender,
                      _signature, _avatar, user_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            #Check that I have modified the user
            if cur.rowcount < 1:
                return None
            return nickname

    def append_user(self, nickname, user):
        '''
        Create a new user in the database.

        :param str nickname: The nickname of the user to modify
        :param dict user: a dictionary with the information to be modified. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {'public_profile':{'registrationdate':,'signature':'',
                                       'avatar':''},
                    'restricted_profile':{'firstname':'','lastname':'',
                                          'email':'', 'website':'','mobile':'',
                                          'skype':'','birthday':'','residence':'',
                                          'gender':'', 'picture':''}
                    }

                where:

                * ``registrationdate``: UNIX timestamp when the user registered
                    in the system (long integer)
                * ``signature``: text chosen by the user for signature
                * ``avatar``: name of the image file used as avatar
                * ``firstanme``: given name of the user
                * ``lastname``: family name of the user
                * ``email``: current email of the user.
                * ``website``: url with the user's personal page. Can be None
                * ``mobile``: string showing the user's phone number. Can be
                    None.
                * ``skype``: user's nickname in skype. Can be None.
                * ``residence``: complete user's home address.
                * ``picture``: file which contains an image of the user.
                * ``gender``: User's gender ('male' or 'female').
                * ``birthday``: string containing the birthday of the user.

            Note that all values are string if they are not otherwise indicated.

        :return: the nickname of the modified user or None if the
            ``nickname`` passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
        #Create the SQL Statements
          #SQL Statement for extracting the userid given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement to create the row in  users table
        query2 = 'INSERT INTO users(nickname,regDate,lastLogin,timesviewed)\
                  VALUES(?,?,?,?)'
          #SQL Statement to create the row in user_profile table
        query3 = 'INSERT INTO users_profile (user_id, firstname,lastname, \
                                             email,website, \
                                             picture,mobile, \
                                             skype,birthday,residence, \
                                             gender,signature,avatar)\
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
        #temporal variables for user table
        #timestamp will be used for lastlogin and regDate.
        timestamp = time.mktime(datetime.now().timetuple())
        timesviewed = 0
        #temporal variables for user profiles
        p_profile = user['public_profile']
        r_profile = user['restricted_profile']
        _firstname = r_profile.get('firstname', None)
        _lastname = r_profile.get('lastname', None)
        _email = r_profile.get('email', None)
        _website = r_profile.get('website', None)
        _picture = r_profile.get('picture', None)
        _mobile = r_profile.get('mobile', None)
        _skype = r_profile.get('skype', None)
        _birthday = r_profile.get('birthday', None)
        _residence = r_profile.get('residence', None)
        _gender = r_profile.get('gender', None)
        _signature = p_profile.get('signature', None)
        _avatar = p_profile.get('avatar', None)
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to extract the id associated to a nickname
        pvalue = (nickname,)
        cur.execute(query1, pvalue)
        #No value expected (no other user with that nickname expected)
        row = cur.fetchone()
        #If there is no user add rows in user and user profile
        if row is None:
            #Add the row in users table
            # Execute the statement
            pvalue = (nickname, timestamp, timestamp, timesviewed)
            cur.execute(query2, pvalue)
            #Extrat the rowid => user-id
            lid = cur.lastrowid
            #Add the row in users_profile table
            # Execute the statement
            pvalue = (lid, _firstname, _lastname, _email, _website,
                      _picture, _mobile, _skype, _birthday,_residence, _gender,
                      _signature, _avatar)
            cur.execute(query3, pvalue)
            self.con.commit()
            #We do not do any comprobation and return the nickname
            return nickname
        else:
            return None

    # UTILS
    def get_friends(self, nickname):
        '''
        Get a list with friends of a user.

        :param str nickname: nickname of the target user
        :return: a list of users nicknames or None if ``nickname`` is not in the
            database
        '''
        raise NotImplementedError("")

    def get_user_id(self, nickname):
        '''
        Get the key of the database row which contains the user with the given
        nickname.

        :param str nickname: The nickname of the user to search.
        :return: the database attribute user_id or None if ``nickname`` does
            not exit.
        :rtype: str

        '''

        '''
        TASK5 TODO :
        * Implement this method.
        HINTS:
          * Check the method get_message as an example.
          * The value to return is a string and not a dictionary
          * You can access the columns of a database row in the same way as
            in a python dictionary: row [attribute] (Check the exercises slides
            for more information)
          * There is only one possible user_id associated to a nickname
          * HOW TO TEST: Use the database_api_tests_user. The following tests
            must pass without failure or error:
                * test_get_user_id
                * test_get_user_id_unknown_user
        '''
        query = 'SELECT user_id from users WHERE nickname = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the  main statement
        pvalue = (nickname,)
        cur.execute(query, pvalue)
        #Extract the results. Just one row expected.
        row = cur.fetchone()
        if row is None:
            return None
        else:
            return row["user_id"]

    def contains_user(self, nickname):
        '''
        :return: True if the user is in the database. False otherwise
        '''
        return self.get_user_id(nickname) is not None
