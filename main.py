#!/usr/bin/python
#-*- coding: utf-8 -*-
__author__ = 'torresmateo'
from escpos import *
import platform
from lx300printer.json_document import JsonDocument
from lx300printer.spanish_constants import *
from flask import Flask, render_template, request, redirect, url_for, Response
import json
import usb.core
import os

app = Flask(__name__)

@app.route("/print/", methods=['POST'])
def print_document():
    json_str = request.form['text']
    print type(json_str)
    response_str = "Your printer should be making some noise!!"
    print_fp = open("print.txt", "w")
    # try:
    if platform.system() == 'Windows':
        if "verbatim" in request.form.keys():
            json_str = json_str.encode('utf8')
            for character in spanish_characters:
                json_str = json_str.replace(character, spanish_characters[character])
            print_fp.write(json_str)
        else:
            document = JsonDocument(json_str)
            print document.get_printable_string()
            print_fp.write(document.get_printable_string())
        print_fp.close()
        os.system('RawPrinterConsole print.txt')
    else:
        epson = printer.Usb(0x4b8, 0x5)
        epson.set(codepage='iso8859_9', font='c')
        if "verbatim" in request.form.keys():
            json_str = json_str.encode('utf8')
            for character in spanish_characters:
                json_str = json_str.replace(character, spanish_characters[character])
            epson._raw(json_str)
        else:
            document = JsonDocument(json_str)
            epson._raw(document.get_printable_string())
    #except Exception, e:
    #    response_str = "Error: " + str(e)
    #finally:
    #    try:
    #        epson.close()
    #    except NameError:
    #        pass

    return response_str




@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        json_str = request.form["text"]
        if "verbatim" in request.form.keys():
            return redirect(url_for('print_document'), code=307)
        else:
            document = JsonDocument(json_str)
            print type(document.get_printable_string())
            # from http://stackoverflow.com/questions/13303464/can-flask-using-jinja2-render-templates-using-windows-1251-encoding
            r = Response()
            r.data = render_template('preview.html', text=document.main_string, json_str=json.dumps(json_str))
            return r
    else:
        return render_template('index.html')


def store_config(conf_dict):
    config_file = open('config.txt', 'W')
    config_file.write(json.dumps(conf_dict))
    config_file.close()

@app.route("/config", methods=['POST', 'GET'])
def config():
    if request.method == 'POST':
        configuration = {}
        configuration['printer'] = 'test'
        store_config(configuration)
        return "Not yet implemented!!"
    else:
        all_devices = usb.core.find(find_all=True)
        dev = {}
        for device in all_devices:
            dev[(hex(device.idVendor), hex(device.idProduct))] = device.product
        return render_template('config.html', dev=dev)

if __name__ == "__main__":
    app.run(debug=True, port=52738, host='0.0.0.0')
