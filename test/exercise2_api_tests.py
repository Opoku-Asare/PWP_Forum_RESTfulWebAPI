'''
Created on 26.01.2013
Modified on 18.02.2016
@author: ivan
'''
import unittest, copy
import json

import flask

import forum.resources as resources
import forum.database as database

DB_PATH = 'db/forum_test.db'
ENGINE = database.Engine(DB_PATH)

#Tell Flask that I am running it in testing mode.
resources.app.config['TESTING'] = True
#Database Engine utilized in our testing
resources.app.config.update({'Engine': ENGINE})

#Other database parameters.
initial_messages = 20
initial_users = 5


class ResourcesAPITestCase(unittest.TestCase):
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
        #Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        '''
        Remove all records from database
        '''
        ENGINE.clear()


class MessagesTestCase (ResourcesAPITestCase):

    url = '/forum/api/messages/'

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Messages)

    def test_get_messages(self):
        '''
        Checks that GET Messages return correct status code and data format
        '''
        print '('+self.test_get_messages.__name__+')', self.test_get_messages.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
            link = data['links']
            self.assertEquals(link[0]['title'], 'Users list')
            self.assertEquals(link[0]['rel'], 'related')
            self.assertEquals(link[0]['href'],
                              resources.api.url_for(resources.Users))
            messages = data['messages']
            self.assertEquals(len(messages), initial_messages)
            #Just check one message the rest are constructed in the same way
            message0 = messages[0]
            self.assertIn('title', message0)
            link0 = message0['link']
            #The link contains a url to a message
            self.assertIn(resources.api.url_for(resources.Messages),
                          link0['href'])

class UsersTestCase (ResourcesAPITestCase):

    url = '/forum/api/users/'

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Users)

    def test_get_users(self):
        '''
        Checks that GET users return correct status code and data format
        '''
        print '('+self.test_get_users.__name__+')', self.test_get_users.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
            link = data['links']
            self.assertEquals(link[0]['title'], 'Messages list')
            self.assertEquals(link[0]['rel'], 'related')
            self.assertEquals(link[0]['href'], resources.api.url_for(resources.Messages))
            users = data['users']
            self.assertEquals(len(users), initial_users)
            #Just check one users the rest are constructed in the same way
            users0 = users[0]
            self.assertIn('nickname', users0)
            self.assertIn('link', users0)
            link0 = users0['link']
            for attr in ('title', 'rel', 'href'):
                self.assertIn(attr, link0)
            #The link contains a url to a user
            self.assertIn(resources.api.url_for(resources.User,
                                                nickname=users0['nickname']),
                          link0['href'])

class MessageTestCase (ResourcesAPITestCase):
    
    #ATTENTION: json.loads return unicode
    url = '/forum/api/messages/msg-1/'
    url_wrong = '/forum/api/messages/msg-290/'
    message_1_request = {u"title":u"CSS: Margin problems with IE (II)",
                 u"body": u"I HAVE TRIED MODIFYING THE PADDING AND IT DOES NOT WORK EITHER",
                 u"sender":u"AxelW"}
    messg_1_req_mod = {u"title": u"CSS: Margin problems with IE (II)",
                                  u"body": u"I have tried modifiying the \
                                   padding and it does not work either",
                                  u"editor":u"Admin"}
    messg_1_req_mod_wrong = {u"title":u"CSS: Margin problems with IE (II)",
                                        u"editor":u"Admin"}
    messg_1_req_wrong = {u"title":u"CSS: Margin problems with IE (II)"}
    message_1_response =  {u"message":{
                                u"title":u"CSS: Margin problems with IE (II)",
                                u"body":u"I HAVE TRIED MODIFYING THE PADDING AND IT DOES NOT WORK EITHER",
                                u"sender":{u"href":"/forum/api/users/AxelW/",
                                           u"rel":u"author",
                                           u"title":u"AxelW"}
                                     },
                           u"links":[{u'title':u'parent', u'rel':u'up', u'href':u'/forum/api/messages/msg-1/', u'method':u'GET'},
                                     {u'title':u'Messages list', u'rel':u'collection', u'href': u'/forum/api/messages/',u'method':u'GET'},
                                     {u'href': u'/forum/api/messages/msg-21/', u'rel': u'self'},
                                     {u'href': u'/forum/api/messages/msg-21/', u'rel': u'edit'}]
                           }

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.Message)

    def test_wrong_url(self):
        '''
        Checks that GET Message return correct status code if given a
        wrong message
        '''
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

    def test_get_message(self):
        '''
        Checks that GET Message return correct status code and data format
        '''
        print '('+self.test_get_message.__name__+')', self.test_get_message.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)
            #The data is formed by links and message
            links = data['links']
            message = data['message']

            #Check that the link format is correct
            self.assertEquals(len(links), 3)
            link0 = links[0]
            self.assertEquals(link0['title'], 'Messages list')
            self.assertEquals(link0['rel'], 'collection')
            self.assertEquals(link0['href'], resources.api.url_for(resources.Messages))

            #Check that the message contains all required attributes
            for attribute in ('body', 'title', 'sender'):
                self.assertIn(attribute, message)

            #Check that the sender format is correct
            sender = message['sender']
            for attribute in ('href', 'rel', 'title'):
                self.assertIn(attribute, sender)

            #Check that we provide the correct user
            self.assertEquals(resources.api.url_for(resources.User,
                                                    nickname=sender['title']),
                              sender['href'])

    def test_add_reply_unexisting_message(self):
        '''
        Try to add a reply to an unexisting message
        '''
        print '('+self.test_add_reply_unexisting_message.__name__+')', self.test_add_reply_unexisting_message.__doc__
        resp = self.client.post(self.url_wrong,
                                data=json.dumps(self.messg_1_req_wrong),
                                headers={"Content-Type": "application/json"})
        self.assertEquals(resp.status_code, 404)

    def test_add_reply_wrong_message(self):
        '''
        Try to add a reply to a message sending wrong data
        '''
        print '('+self.test_add_reply_wrong_message.__name__+')', self.test_add_reply_wrong_message.__doc__
        resp = self.client.post(self.url,
                                data=json.dumps(self.messg_1_req_wrong),
                                headers={"Content-Type": "application/json"})
        self.assertEquals(resp.status_code, 400)

    def test_add_message(self):
        '''
        Add a new message and check that I receive the same data
        '''
        print '('+self.test_add_message.__name__+')', self.test_add_message.__doc__
        resp = self.client.post(self.url,
                                data=json.dumps(self.message_1_request),
                                headers={"Content-Type": "application/json"})
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        message_url = resp.headers['Location']
        #Check that the message is stored
        resp2 = self.client.get(message_url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        self.assertDictContainsSubset(self.message_1_response['message'], data['message'])
        self.assertItemsEqual(self.message_1_response['links'], data['links'])

    def test_modify_message(self):
        '''
        Modify an exsiting message and check that the message has been modified correctly in the server
        '''
        print '('+self.test_modify_message.__name__+')', self.test_modify_message.__doc__
        resp = self.client.put(self.url,
                               data=json.dumps(self.messg_1_req_mod),
                               headers={"Content-Type": "application/json"})
        self.assertEquals(resp.status_code, 204)
        #Check that the message has been modified
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        #Check that the title and the body of the message has been modified with the new data
        self.assertDictContainsSubset(self.messg_1_req_mod, data['message'])
        #self.assertEquals(data['message']['title'],message_1_request)

    def test_modify_unexisting_message(self):
        '''
        Try to modify a message that does not exist
        '''
        print '('+self.test_modify_unexisting_message.__name__+')', self.test_modify_unexisting_message.__doc__
        resp = self.client.put(self.url_wrong,
                                data=json.dumps(self.messg_1_req_mod),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 404)

    def test_modify_wrong_message(self):
        '''
        Try to modify a message sending wrong data
        '''
        print '('+self.test_modify_wrong_message.__name__+')', self.test_modify_wrong_message.__doc__
        resp = self.client.put(self.url,
                                data=json.dumps(self.messg_1_req_mod_wrong),
                                headers={"Content-Type":"application/json"})
        self.assertEquals(resp.status_code, 400)

    def test_delete_message(self):
        '''
        Checks that Delete Message return correct status code if corrected delete
        '''
        print '('+self.test_delete_message.__name__+')', self.test_delete_message.__doc__
        resp = self.client.delete(self.url)
        self.assertEquals(resp.status_code, 204)
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_unexisting_message(self):
        '''
        Checks that Delete Message return correct status code if given a wrong address
        '''
        print '('+self.test_delete_unexisting_message.__name__+')', self.test_delete_unexisting_message.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

class UserTestCase (ResourcesAPITestCase):
    user1 = 'AxelW'
    user2 = 'Jacobino'
    url1 = '/forum/api/users/%s/'% user1
    url2 = '/forum/api/users/%s/'% user2
    url_wrong = '/forum/api/users/unknown/'

    user = {u"public_profile":{
                                u"signature":u"What is born in Palencia stays in Palencia",
                                u"avatar":u"file2.jpg"
                                        },
                     u"restricted_profile":{u"firstname":u"Peter", 
                          u"lastname":u"DonNadie",
                          u"birthday":u'2010-10-01',
                          u"gender":u"Male",
                          u"residence":u"Palencia, Spain",
                          u"email":u"john@notanyone.com",
                          u"website":u"http://nothingisnothin.com"}
            }

    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__
        with resources.app.test_request_context(self.url1):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.User)

    def test_wrong_url(self):
        '''
        Checks that GET Message return correct status code if given a wrong message
        '''
        print '('+self.test_wrong_url.__name__+')', self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

    def test_get_format(self):
        '''
        Checks that the format of user is correct

        '''
        print '('+self.test_get_format.__name__+')', self.test_get_format.__doc__
        #TO be authorized the I must include the header Authorization with name of the user or admin
        resp = self.client.get(self.url1)
        data = json.loads(resp.data)
        self.assertIn('links', data)
        self.assertIn('user', data)
        #Check that user has public_profile, restricted_profile, history
        for attribute in ('nickname', 'registrationdate'):
            self.assertIn(attribute, data['user'])

    def test_add_user(self):
        '''
        Checks that the user is added correctly

        '''
        print '('+self.test_add_user.__name__+')', self.test_add_user.__doc__
        resp = self.client.put(self.url2,
                               data=json.dumps(self.user),
                               headers={"Content-Type": "application/json"})
        #print resp.data
        self.assertEquals(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        resp2 = self.client.get(self.url2)
        self.assertEquals(resp2.status_code, 200)

    def test_add_user_missing_mandatory(self):
        '''
        Test that it returns error when is missing a mandatory data
        '''
        print '('+self.test_add_user_missing_mandatory.__name__+')', self.test_add_user_missing_mandatory.__doc__
        mandatory = ['firstname', 'lastname', 'birthday', 'residence', 'gender','email']
        #Iterate through all the attributes from the list, remove one of them in
        #each iteration. Be sure that always return status code 400
        for attribute in mandatory:
            user = copy.deepcopy(self.user)
            del user['restricted_profile'][attribute]
            resp = self.client.put(self.url2,
                                   data=json.dumps(user),
                                   headers={"Content-Type": "application/json"})
            self.assertEquals(resp.status_code, 400)
      
    def test_add_existing_user(self):
        '''
        Testign that trying to add an existing user will fail

        '''
        print '('+self.test_add_existing_user.__name__+')', self.test_add_existing_user.__doc__
        resp = self.client.put(self.url1,
                               data=json.dumps(self.user),
                               headers={"Content-Type": "application/json"})
        self.assertEquals(resp.status_code, 409)

class HistoryTestCase (ResourcesAPITestCase):
   
    url = '/forum/api/users/AxelW/history/'
    messages_number = 2
    url_nickname = 'AxelW'
    url2 = '/forum/api/users/Mystery/history/'
    messages2_number = 2
    url3 = '/forum/api/users/AxelW/history/?length=1'
    messages3_number = 1

    url4 =  '/forum/api/users/AxelW/history/?after=1362317481'
    messages4_number = 1
    url5 =  '/forum/api/users/AxelW/history/?before=1362317481'
    messages5_number = 1
    url6 = '/forum/api/users/AxelW/history/?before=1362317481&after=1362217481'

    
    def test_url(self):
        '''
        Checks that the URL points to the right resource
        '''
        #NOTE: self.shortDescription() shuould work.
        print '('+self.test_url.__name__+')', self.test_url.__doc__, 
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.History)
    
    def test_get_history_number_values(self):
        '''
        Checks that GET history return correct status code and number of values
        '''
        print '('+self.test_get_history_number_values.__name__+')', self.test_get_history_number_values.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            self.assertIn('messages',data)
            messages = data['messages']
            self.assertEquals(len(messages),self.messages_number)

            resp = client.get(self.url2)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            self.assertIn('messages',data)
            messages = data['messages']
            self.assertEquals(len(messages),self.messages2_number)

            resp = client.get(self.url3)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            self.assertIn('messages',data)
            messages = data['messages']
            self.assertEquals(len(messages),self.messages3_number)
            
    
    def test_get_history_timestamp_values(self):
        '''
        Checks that GET history return correct status code and format
        '''
        print '('+self.test_get_history_timestamp_values.__name__+')', self.test_get_history_timestamp_values.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url4)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            self.assertIn('messages',data)
            messages = data['messages']
            self.assertEquals(len(messages),self.messages4_number)

            resp = client.get(self.url5)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            self.assertIn('messages',data)
            messages = data['messages']
            self.assertEquals(len(messages),self.messages5_number)

            resp = client.get(self.url6)
            self.assertEquals(resp.status_code,404)

    
    def test_get_history(self):
        '''
        Checks that GET history return correct status code and number of values
        '''
        print '('+self.test_get_history.__name__+')', self.test_get_history.__doc__
        #I use this because I need the app context to use the api.url_for
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEquals(resp.status_code,200)
            data = json.loads(resp.data)
            link = data['links']
            self.assertEquals(link[0]['title'], 'Sender')
            self.assertEquals(link[0]['rel'], 'parent')
            self.assertEquals(link[0]['href'], resources.api.url_for(resources.User,nickname=self.url_nickname))
            self.assertEquals(link[0]['method'], 'GET')
            self.assertEquals(link[1]['title'], 'Users')
            self.assertEquals(link[1]['rel'], 'collection')
            self.assertEquals(link[1]['href'], resources.api.url_for(resources.Users))
            self.assertEquals(link[0]['method'], 'GET')

            messages = data['messages']
            
            #Just check one message the rest are constructed in the same way
            message0 = messages [0]
            link0 = message0['link']
            self.assertIn('title',link0)
            self.assertIn('href',link0)
            self.assertIn('rel',link0)

if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()