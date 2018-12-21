import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import sqlite3
from sqlite3 import Error
import json
import time


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
        # user = self.get_user()
        db_con = WebApp.db_connection(WebApp.dbsqlite)
        sql = "select password from users where username == '{}'".format(usr)
        cur = db_con.execute(sql)
        row = cur.fetchone()
        if row != None:
            if row[0] == pwd:
                self.set_user(usr)
        db_con.close()

    def do_authenticationJSON(self, usr, pwd):
        # user = self.get_user()
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
        db_json["users"].append({"username": usr, "password": pwd, "park":  "", "timestamp": ""})
        json.dump(db_json, open(WebApp.dbjson, 'w'))
        return True

    def check_userHasReserve(self, usr):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr:
                if u['park'] == "":
                    return False
                else:
                    return True

    def check_userReserveStart(self, usr):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr:
                if u['timestamp'] == "":
                    return False
                else:
                    return True

    def do_getReserveTime(self, usr):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr:
                return float(u['timestamp'])

    def do_getUserReserve(self, usr):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr:
                return u['park']

    def do_parkReserve(self, usr, park_name):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        parks = db_json['parks']
        for p in parks:
            if p['name'] == park_name:
                if p['free_spaces'] <= 0:
                    return False
                else:
                    for u in users:
                        if u['username'] == usr:
                            p['free_spaces'] -= 1
                            u['park'] = park_name
                            json.dump(db_json, open(WebApp.dbjson, 'w'))
                            return True
        return False

    def do_startreserve(self, usr):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr:
                u['timestamp'] = time.time()
                break
        json.dump(db_json, open(WebApp.dbjson, 'w'))

    def do_endreserve(self, usr):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        parks = db_json['parks']
        park_name = ""
        for u in users:
            if u['username'] == usr:
                park_name = u['park']
                u['park'] = ""
                u['timestamp'] = ""
                break
        for p in parks:
            if p['name'] == park_name:
                p['free_spaces'] += 1
                break
        json.dump(db_json, open(WebApp.dbjson, 'w'))

    def do_timedif(self, usr):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        for u in users:
            if u['username'] == usr:
                return time.time() - float(u['timestamp'])

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
            # self.do_authenticationDB(username, password)
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Entrar',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('login.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("/home")

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
            if not self.check_userHasReserve(self.get_user()['username']):
                raise cherrypy.HTTPRedirect("/home")
            else:
                r = self.do_getUserReserve(self.get_user()['username'])
                if self.check_userReserveStart(self.get_user()['username']):
                    t = self.do_timedif(self.get_user()['username'])
                    s = str(int(t//3600)) + "h " + str(int(t//60)) + "min"
                    tparams = {
                        'title': r,
                        'errors': True,
                        'user': self.get_user(),
                        'year': s,
                    }
                    return self.render('autenticateinout.html', tparams)
                else:
                    tparams = {
                        'title': r,
                        'errors': False,
                        'user': self.get_user(),
                        'year': datetime.now().year,
                    }
                    return self.render('autenticateinout.html', tparams)

    @cherrypy.expose
    def startreserve(self):
        self.do_startreserve(self.get_user()['username'])
        raise cherrypy.HTTPRedirect("/home")

    @cherrypy.expose
    def closereserve(self):
        r = self.do_getUserReserve(self.get_user()['username'])
        t = self.do_timedif(self.get_user()['username'])
        s = str(int(t // 3600)) + "h " + str(int(t // 60)) + "min"
        tparams = {
            'title': r,
            'user': self.get_user(),
            'year': s,
        }
        self.do_endreserve(self.get_user()['username'])
        return self.render('closereserve.html', tparams)

    @cherrypy.expose
    def findpark(self):
        if not self.get_user()['is_authenticated']:
            self.home()
        else:
            if self.check_userHasReserve(self.get_user()['username']):
                raise cherrypy.HTTPRedirect("/home")
            else:
                tparams = {
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('findpark.html', tparams)

    @cherrypy.expose
    def reserve(self, park=None):
        if park is None or park == "":
            tparams = {
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('findpark.html', tparams)
        else:
            if self.do_parkReserve(self.get_user()['username'], park):
                raise cherrypy.HTTPRedirect("/home")
            else:
                tparams = {
                    'errors': True,
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
        r = self.do_getUserReserve(self.get_user()['username'])
        if r != "":
            if self.check_userReserveStart(self.get_user()['username']):
                t = self.do_timedif(self.get_user()['username'])
                s = str(int(t // 3600)) + "h " + str(int(t // 60)) + "min"
                tparams = {
                    'title': r,
                    'errors': True,
                    'user': self.get_user(),
                    'year': s,
                }
                return self.render('home.html', tparams)
            else:
                tparams = {
                    'title': r,
                    'errors': True,
                    'user': self.get_user(),
                    'year': "",
                }
                return self.render('home.html', tparams)
        else:
            tparams = {
                'errors': False,
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
