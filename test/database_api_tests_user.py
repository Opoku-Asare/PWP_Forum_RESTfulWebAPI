'''
Created on 13.02.2014
Modified on 01.02.2016
Database interface testing for all users related methods.
The user has a data model represented by the following User dictionary:
    {'public_profile': {'registrationdate': ,'nickname': ''
                       'signature': '','avatar': ''},
    'restricted_profile': {'firstname': '','lastname': '','email': '',
                          'website': '','mobile': '','skype': '',
                          'birthday': '','residence': '','gender': '',
                          'picture': ''}
    }
    where:
     - registrationdate: UNIX timestamp when the user registered in
                         the system
     - nickname: nickname of the user
     - signature: text chosen by the user for signature
     - avatar: name of the image file used as avatar
     - firstanme: given name of the user
     - lastname: of the user
     - email: current email of the user.
     - website: url with the user's personal page
     - mobile: string showing the user's phone number
     - skype: user's nickname in skype
     - residence: complete user's home address.
     - picture: file which contains an image of the user.
     - gender: User's gender ('male' or 'female').
     - birthday: int with the birthday of the user.


List of users has the following data model:
[{'nickname':'', 'registrationdate':''}, {'nickname':'', 'registrationdate':''}]


@author: ivan
'''
import unittest, sqlite3
from forum import database

#Path to the database file, different from the deployment db
DB_PATH = 'db/forum_test.db'
ENGINE = database.Engine(DB_PATH)

#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
USER1_NICKNAME = 'Mystery'
USER1_ID = 1
USER1 = {'public_profile': {'registrationdate': 1362015937,
                            'nickname': USER1_NICKNAME,
                            'signature': 'Well, hello there! Blah ...',
                            'avatar': 'avatar_2.gif'},
         'restricted_profile': {'firstname': 'Mystery', 'lastname': 'Williams',
                                'email': 'jane@imaginecompany.com',
                                'birthday': '1998-01-22',
                                'residence': 'New York', 'gender': 'Female',
                                'picture': 'photo1.jpg', 'website': None,
                                'mobile': None, 'skype': None}
         }
MODIFIED_USER1 = {'public_profile': {'registrationdate': 1362015937,
                                     'nickname': USER1_NICKNAME,
                                     'signature': 'New signature',
                                     'avatar': 'new_avatar.jpg'},
                  'restricted_profile': {'firstname': 'Mystery',
                                         'lastname': 'Williams',
                                         'email': 'new_email@myname',
                                         'birthday': '1940-01-22',
                                         'residence': 'Bank of Zurich, Spain',
                                         'gender': 'Female',
                                         'picture': 'new_picture.jpg',
                                         'website': 'http: //www.mynewsite.com',
                                         'mobile': "8002020",
                                         'skype': 'mystery'}
                  }
USER2_NICKNAME = 'HockeyFan'
USER2_ID = 5
USER2 = {'public_profile': {'registrationdate': 1394357686,
                            'nickname': USER2_NICKNAME,
                            'signature': 'Washington Capitals rule!',
                            'avatar': 'avatar_7.jpg'},
         'restricted_profile': {'firstname': 'Dan', 'lastname': 'Nicholls',
                                'email': 'dan@gmail.com',
                                'birthday': '1981-12-22',
                                'website': 'http://www.hockeyfan.com/',
                                'residence': 'Washington DC', 'gender': 'Male',
                                'picture': 'photo8.png', 'mobile': None,
                                'skype': None},
         }
NEW_USER_NICKNAME = 'sully'
NEW_USER = {'public_profile': {'signature': 'I am blue',
                               'avatar': 'na_vi.jpg'},
            'restricted_profile': {'firstname': 'Jake', 'lastname': 'Sully',
                                   'email': 'sully@rda.com',
                                   'birthday': '2011-12-10',
                                   'website': 'http: //www.pandora.com/',
                                   'residence': 'USA', 'gender': 'Male',
                                   'picture': 'na_vi2.png',
                                   'mobile': "83232323",
                                   'skype': 'jakesully'},
            }
USER_WRONG_NICKNAME = 'Batty'
INITIAL_SIZE = 5


class UserDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Users related methods.
    '''
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
            database file
        '''
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        '''Remove the testing database'''
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()

    def setUp(self):
        '''
        Populates the database
        '''
        #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()

    def test_users_table_created(self):
        '''
        Checks that the table initially contains 5 users (check
        forum_data_dump.sql). NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        print '('+self.test_users_table_created.__name__+')', \
              self.test_users_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query1 = 'SELECT * FROM users'
        query2 = 'SELECT * FROM users_profile'
        #Connects to the database.
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query1)
            users = cur.fetchall()
            #Assert
            self.assertEquals(len(users), INITIAL_SIZE)
            #Check the users_profile:
            cur.execute(query2)
            users = cur.fetchall()
            #Assert
            self.assertEquals(len(users), INITIAL_SIZE)

    def test_create_user_object(self):
        '''
        Check that the method create_user_object works return adequate values
        for the first database row. NOTE: Do not use Connection instace to
        extract data from database but call directly SQL.
        '''
        print '('+self.test_create_user_object.__name__+')', \
              self.test_create_user_object.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT users.*, users_profile.* FROM users, users_profile \
                 WHERE users.user_id = users_profile.user_id'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        #I am doing operations after with, so I must explicitly close the
        # the connection to be sure that no locks are kepts. The with, close
        # the connection when it has gone out of scope
        #try:
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            #Extrac the row
            row = cur.fetchone()
    #finally:
        #    con.close()
        #Test the method
        user = self.connection._create_user_object(row)
        self.assertDictContainsSubset(user, USER1)

    def test_get_user(self):
        '''
        Test get_user with id Mystery and HockeyFan
        '''
        print '('+self.test_get_user.__name__+')', \
              self.test_get_user.__doc__

        #Test with an existing user
        user = self.connection.get_user(USER1_NICKNAME)
        self.assertDictContainsSubset(user, USER1)
        user = self.connection.get_user(USER2_NICKNAME)
        self.assertDictContainsSubset(user, USER2)

    def test_get_user_noexistingid(self):
        '''
        Test get_user with  msg-200 (no-existing)
        '''
        print '('+self.test_get_user_noexistingid.__name__+')', \
              self.test_get_user_noexistingid.__doc__

        #Test with an existing user
        user = self.connection.get_user(USER_WRONG_NICKNAME)
        self.assertIsNone(user)

    def test_get_users(self):
        '''
        Test that get_users work correctly and extract required user info
        '''
        print '('+self.test_get_users.__name__+')', \
              self.test_get_users.__doc__
        users = self.connection.get_users()
        #Check that the size is correct
        self.assertEquals(len(users), INITIAL_SIZE)
        #Iterate throug users and check if the users with USER1_ID and
        #USER2_ID are correct:
        for user in users:
            if user['nickname'] == USER1_NICKNAME:
                self.assertDictContainsSubset(user, USER1['public_profile'])
            elif user['nickname'] == USER2_NICKNAME:
                self.assertDictContainsSubset(user, USER2['public_profile'])

    def test_delete_user(self):
        '''
        Test that the user Mystery is deleted
        '''
        print '('+self.test_delete_user.__name__+')', \
              self.test_delete_user.__doc__
        resp = self.connection.delete_user(USER1_NICKNAME)
        self.assertTrue(resp)
        #Check that the users has been really deleted throug a get
        resp2 = self.connection.get_user(USER1_NICKNAME)
        self.assertIsNone(resp2)
        #Check that the user does not have associated any message
        resp3 = self.connection.get_messages(nickname=USER1_NICKNAME)
        self.assertEquals(len(resp3), 0)

    def test_delete_user_noexistingnickname(self):
        '''
        Test delete_user with  Batty (no-existing)
        '''
        print '('+self.test_delete_user_noexistingnickname.__name__+')', \
              self.test_delete_user_noexistingnickname.__doc__
        #Test with an existing user
        resp = self.connection.delete_user(USER_WRONG_NICKNAME)
        self.assertFalse(resp)

    def test_modify_user(self):
        '''
        Test that the user Mystery is modifed
        '''
        print '('+self.test_modify_user.__name__+')', \
              self.test_modify_user.__doc__
        #Get the modified user
        resp = self.connection.modify_user(USER1_NICKNAME, MODIFIED_USER1)
        self.assertEquals(resp, USER1_NICKNAME)
        #Check that the users has been really modified through a get
        resp2 = self.connection.get_user(USER1_NICKNAME)
        resp_p_profile = resp2['public_profile']
        resp_r_profile = resp2['restricted_profile']
        #Check the expected values
        p_profile = MODIFIED_USER1['public_profile']
        r_profile = MODIFIED_USER1['restricted_profile']
        self.assertEquals(p_profile['signature'],
                          resp_p_profile['signature'])
        self.assertEquals(p_profile['avatar'], resp_p_profile['avatar'])
        self.assertEquals(r_profile['birthday'], resp_r_profile['birthday'])
        self.assertEquals(r_profile['email'], resp_r_profile['email'])
        self.assertEquals(r_profile['website'], resp_r_profile['website'])
        self.assertEquals(r_profile['residence'], resp_r_profile['residence'])
        self.assertEquals(r_profile['mobile'], resp_r_profile['mobile'])
        self.assertEquals(r_profile['skype'], resp_r_profile['skype'])
        self.assertEquals(r_profile['picture'], resp_r_profile['picture'])
        self.assertDictContainsSubset(resp2, MODIFIED_USER1)

    def test_modify_user_noexistingnickname(self):
        '''
        Test modify_user with  user Batty (no-existing)
        '''
        print '('+self.test_modify_user_noexistingnickname.__name__+')', \
              self.test_modify_user_noexistingnickname.__doc__
        #Test with an existing user
        resp = self.connection.modify_user(USER_WRONG_NICKNAME, USER1)
        self.assertIsNone(resp)

    def test_append_user(self):
        '''
        Test that I can add new users
        '''
        print '('+self.test_append_user.__name__+')', \
              self.test_append_user.__doc__
        nickname = self.connection.append_user(NEW_USER_NICKNAME, NEW_USER)
        self.assertIsNotNone(nickname)
        self.assertEquals(nickname, NEW_USER_NICKNAME)
        #Check that the messages has been really modified through a get
        resp2 = self.connection.get_user(nickname)
        self.assertDictContainsSubset(NEW_USER['restricted_profile'],
                                      resp2['restricted_profile'])
        self.assertDictContainsSubset(NEW_USER['public_profile'],
                                      resp2['public_profile'])

    def test_append_existing_user(self):
        '''
        Test that I cannot add two users with the same name
        '''
        print '('+self.test_append_existing_user.__name__+')', \
              self.test_append_existing_user.__doc__
        nickname = self.connection.append_user(USER1_NICKNAME, NEW_USER)
        self.assertIsNone(nickname)

    def test_get_user_id(self):
        '''
        Test that get_user_id returns the right value given a nickname
        '''
        print '('+self.test_get_user_id.__name__+')', \
              self.test_get_user_id.__doc__
        id = self.connection.get_user_id(USER1_NICKNAME)
        self.assertEquals(USER1_ID, id)
        id = self.connection.get_user_id(USER2_NICKNAME)
        self.assertEquals(USER2_ID, id)

    def test_get_user_id_unknown_user(self):
        '''
        Test that get_user_id returns None when the nickname does not exist
        '''
        print '('+self.test_get_user_id.__name__+')', \
              self.test_get_user_id.__doc__
        id = self.connection.get_user_id(USER_WRONG_NICKNAME)
        self.assertIsNone(id)

    def test_not_contains_user(self):
        '''
        Check if the database does not contain users with id Batty
        '''
        print '('+self.test_contains_user.__name__+')', \
              self.test_contains_user.__doc__
        self.assertFalse(self.connection.contains_user(USER_WRONG_NICKNAME))

    def test_contains_user(self):
        '''
        Check if the database contains users with nickname Mystery and HockeyFan
        '''
        print '('+self.test_contains_user.__name__+')', \
              self.test_contains_user.__doc__
        self.assertTrue(self.connection.contains_user(USER1_NICKNAME))
        self.assertTrue(self.connection.contains_user(USER2_NICKNAME))

if __name__ == '__main__':
    print 'Start running user tests'
    unittest.main()
