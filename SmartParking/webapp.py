import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import sqlite3
from sqlite3 import Error
import json


class WebApp(object):
    dbsqlite = 'data/db.sqlite3'
    dbjson = 'data/db.json'

    def __init__(self):
        self.env = Environment(
                loader=PackageLoader('webapp', 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
                )


########################################################################################################################
#   Utilities

    def set_user(self, username=None):
        if username == None:
            cherrypy.session['user'] = {'is_authenticated': False, 'username': ''}
        else:
            cherrypy.session['user'] = {'is_authenticated': True, 'username': username}


    def get_user(self):
        if not 'user' in cherrypy.session:
            self.set_user()
        return cherrypy.session['user']


    def render(self, tpg, tps):
        template = self.env.get_template(tpg)
        return template.render(tps)


    def db_connection(db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return None


    def do_authenticationDB(self, usr, pwd):
        #user = self.get_user()
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        sql = "select password from users where username == '{}'".format(usr)
        cur = db_con.execute(sql)
        row = cur.fetchone()
        if row != None:
            if row[0] == pwd:
                self.set_user(usr)
        db_con.close()


    def do_authenticationJSON(self, usr, pwd):
        #user = self.get_user()
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr and u['password'] == pwd:
                self.set_user(usr)
                break


    def do_registerJSON(self, usr, pwd):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr:
                return False
        db_json["users"].append({"username": usr, "password": pwd})
        json.dump(db_json, open(WebApp.dbjson, 'w'))
        return True


########################################################################################################################
#   Controllers

    @cherrypy.expose
    def index(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('home.html', tparams)


    @cherrypy.expose
    def about(self):
        tparams = {
            'title': 'Sobre',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('about.html', tparams)


    @cherrypy.expose
    def login(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Entrar',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('login.html', tparams)
        else:
            self.do_authenticationJSON(username, password)
            #self.do_authenticationDB(username, password)
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Entrar',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('login.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("/")


    @cherrypy.expose
    def logout(self):
        self.set_user()
        raise cherrypy.HTTPRedirect("/")


    @cherrypy.expose
    def signup(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Registar',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('signup.html', tparams)
        else:
            if not self.do_registerJSON(username, password):
                tparams = {
                    'title': 'Registar',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('signup.html', tparams)
            else:
                self.do_authenticationJSON(username, password)
                raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def autenticateinout(self):
        if not self.get_user()['is_authenticated']:
            self.home()
        else:
            tparams = {
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('autenticateinout.html', tparams)

    @cherrypy.expose
    def findpark(self):
        if not self.get_user()['is_authenticated']:
            self.home()
        else:
            tparams = {
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('findpark.html', tparams)

    @cherrypy.expose
    def qrcodegen(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('qrcodegen.html', tparams)

    @cherrypy.expose
    def home(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('home.html', tparams)


    @cherrypy.expose
    def shut(self):
        cherrypy.engine.exit()


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        },
        'global': {
        	'server.socket_host': '0.0.0.0',
        	'server.socket_port': int(os.environ.get('PORT', 5000)),
		}
    }
    cherrypy.quickstart(WebApp(), '/', conf)
