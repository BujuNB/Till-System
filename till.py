#!/usr/bin/env python
"""
Very simple HTTP server in python.
Usage::
    ./dummy-web-server.py [<port>]
Send a GET request::
    curl http://localhost
Send a HEAD request::
    curl -I http://localhost
Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer

import base64
import sqlite3
from datetime import datetime

def build_action_refill(where,what):
    text = "<action>\n"
    text += "<type>refill</type>\n"
    text += "<where>"+where+"</where>\n"
    text += "<what>"+base64.b64encode(what)+"</what>\n"
    text += "</action>\n"
    return text

def build_action_append(where,what):
    text = "<action>\n"
    text += "<type>append</type>\n"
    text += "<where>"+where+"</where>\n"
    text += "<what>"+base64.b64encode(what)+"</what>\n"
    text += "</action>\n"
    return text

def build_action_total(value):
    text = "<action>\n"
    text += "<type>total</type>\n"
    text += "<value>"+str(value)+"</value>\n"
    text += "</action>\n"
    return text

def build_action_reset():
    text = "<action>\n"
    text += "<type>reset</type>\n"
    text += "</action>\n"
    return text

    
class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):

        parts = self.path.split("?",1);
        
        if (self.path == '/'):
            self.send_response(200)
            fname = 'till.html';
            file = open(fname,"r")
            text = file.read()
            self.send_header('Content-type', 'text/html')
        elif (self.path == '/till.css'):
            fname = 'till.css';
            file = open(fname,"r")
            text = file.read()
            self.send_header('Content-type', 'text/css')
            self.send_response(200)
        elif (self.path == '/till2.html'):
            self.send_response(200)
            fname = 'till2.html';
            file = open(fname,"r")
            text = file.read()
            self.send_header('Content-type', 'text/html')
        elif (self.path == '/till.js'):
            self.send_response(200)
            fname = 'till.js';
            file = open(fname,"r")
            text = file.read()
            self.send_header('Content-type', 'application/javascript')
        elif (parts[0] == '/action'):
            self.send_response(200)

            subtext = "";
            global transaction_ID
            info_list = [];
            c_total = 0
            transactiontext = '<br>'
            changetext = "Change &pound;"
            changevalue = "%8.2f" % 0.00
            for p in parts[1].split("&"):
                subtext = subtext + p +"<br>";
                x = p.split("=");
                info_list.append(x[1]);
            print(info_list)
            
            
            # when the action is plu
            if info_list[0] == 'plu':
                cursor.execute('SELECT name, price FROM products WHERE plu = ?;', (info_list[3],));
                X = cursor.fetchone()
                current_price = int(X[1]) * int(info_list[2]);
                current_item = X[0]
                
                cursor.execute('SELECT productid FROM products WHERE pos = ? AND shift = ?;',
                               (info_list[3], c_shift));
                currentid = int(cursor.fetchone()[0]);

                # when the refund is happen
                if info_list[1] == '4':
                    if (current_item, currentid) not in c_transaction.keys():
                        pass
                    else:
                        if c_transaction[(current_item, currentid)][0] - int(info_list[2]) < 0:
                            pass
                        elif c_transaction[(current_item, currentid)][0] - int(info_list[2]) == 0:
                            del c_transaction[(current_item, currentid)]
                        else:
                            c_transaction[(current_item, currentid)][0] -= int(info_list[2])
                            c_transaction[(current_item, currentid)][1] -= current_price
        
                # when the refund is not happen
                else:
                    if (current_item, currentid) in c_transaction.keys():
                        c_transaction[(current_item, currentid)][0] += int(info_list[2])
                        c_transaction[(current_item, currentid)][1] += current_price
                    else:
                        c_transaction[(current_item, currentid)] = [int(info_list[2]),current_price]
            
            
            # when the action is cash
            if info_list[0] == 'cash':
                cursor.execute('SELECT name FROM payment_method WHERE methodid = ?;',
                               (info_list[2],));
                method_name = cursor.fetchone()[0]
                
                if info_list[3] == '0':
                    pass
                else:
                    for i in c_transaction.keys():
                        c_total += c_transaction[i][1]
                    changevalue = 0.00
                    changevalue = float(int(info_list[3]) - c_total)
                    changevalue /= 100.00
                    changevalue = "%8.2f" % changevalue
                
                c_list = list(c_transaction.keys())
               
                for i in c_list:
                    c_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute('INSERT INTO t_record VALUES (?,?,?,?,?,?);',
                                   (transaction_ID, c_time, i[0], i[1], c_transaction[i][0], method_name, ));
                    db.commit()
                    
                for i in c_list:
                    del c_transaction[i]

                transaction_ID += 1
            
            # when the action is program
            if info_list[0] == 'program':
                if info_list[4] == '2':
                    c_shift = '-2';
                elif info_list[4] == '0' and int(info_list[3]) <= 12:
                    c_shift = '-2';
                else:
                    c_shift = info_list[4]

                cursor.execute('SELECT price FROM products WHERE pos = ? AND shift = ?;',
                               (info_list[3], c_shift));
                current_price = int(cursor.fetchone()[0]) * int(info_list[2]);
                
                cursor.execute('SELECT productid FROM products WHERE pos = ? AND shift = ?;',
                               (info_list[3], c_shift));
                currentid = int(cursor.fetchone()[0]);

                if c_shift != '0':
                    if c_shift == '-2':
                        current_shape = 'Medium'
                    else:
                        cursor.execute('SELECT name FROM shift WHERE shiftid = ?;', (c_shift,));
                        current_shape = cursor.fetchone()[0]
                    cursor.execute('SELECT name FROM products WHERE pos = ?;', (info_list[3],));
                    current_name = cursor.fetchone()[0]
                    current_item = str(current_shape) + ' ' + str(current_name)
                else:
                    cursor.execute('SELECT name FROM products WHERE pos = ?;', (info_list[3],));
                    current_item = cursor.fetchone()[0]
                
                # when the refund is happen
                if info_list[1] == '4':
                    if (current_item, currentid) not in c_transaction.keys():
                        pass
                    else:
                        if c_transaction[(current_item, currentid)][0] - int(info_list[2]) < 0:
                            pass
                        elif c_transaction[(current_item, currentid)][0] - int(info_list[2]) == 0:
                            del c_transaction[(current_item, currentid)]
                        else:
                            c_transaction[(current_item, currentid)][0] -= int(info_list[2])
                            c_transaction[(current_item, currentid)][1] -= current_price

                # when the refund is not happen
                else:
                    if (current_item, currentid) in c_transaction.keys():
                        c_transaction[(current_item, currentid)][0] += int(info_list[2])
                        c_transaction[(current_item, currentid)][1] += current_price
                    else:
                        c_transaction[(current_item, currentid)] = [int(info_list[2]),current_price]


            # when the action is clr
            if info_list[0] == 'clr':
                for i in c_transaction.keys():
                    del c_transaction[i]
            
            
            print(c_transaction)
            for i in c_transaction.keys():
                c_total += c_transaction[i][1]
                transactiontext += str(i[0]) + ' ' + str(c_transaction[i][0]) + '<br>'
            
            text  = '<?xml version="1.0" encoding="UTF-8"?>\n'
            text += "<response>\n"
            text += build_action_total(c_total);
            text += build_action_append("target", subtext);
            text += build_action_append("target", transactiontext);
            text += build_action_refill("title", changetext + str(changevalue));
            text += build_action_reset();

            text += "</response>\n"
            self.send_header('Content-type', 'application/xml')
            
        else:
            self.send_response(404)
            fname = '404.html';
            file = open(fname,"r")
            text = file.read()
            self.send_header('Content-type', 'text/html')
            
        self.end_headers()
        self.wfile.write(text)

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
        
def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    
    transaction_ID = 1
    c_transaction = {}
    # connect the databas and stores all the tables in a list
    db = sqlite3.connect('products.db')
    cursor = db.cursor()
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()


