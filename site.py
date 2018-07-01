from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
from date_compute import time_converter

app = Flask('FlightSite')

@app.route('/')
def home():
  return render_template('home.html', errors={})

@app.route('/SearchNodm')
def search_nodm():
  nodm = request.args.get('nodm', '')
  if re.match('^\w{3,4}$', nodm):
    url = 'https://pilotweb.nas.faa.gov/PilotWeb/notamRetrievalByICAOAction.do'
    params = { 
      'method': 'displayByICAOs', 
      'reportType': 'RAW', 
      'formatType': 'DOMESTIC',
      'retrieveLocId': nodm, 
      'actionType': 'notamRetrievalByICAOs' 
    }
    try:
      html_result = requests.get(url, params=params, timeout=5)
      parsed = BeautifulSoup(html_result.text, 'html.parser')
      all_nodms = parsed.select('#resultsHomeLeft #notamRight span')
      processed_nodms = [n.text.replace('!', '') for n in all_nodms]
      return render_template('search.html', data=processed_nodms, nodm=nodm)
    except Exception as e:
      print(e)
      return render_template('home.html', errors={'nodm_error':'Network Error'})
  else:
    return render_template('home.html', errors={'nodm_error':'Invalid NODM'})

@app.route('/ConvertTime')
def convert_time():
  dep_time_str = request.args.get('DepTime', '')
  ete_str = request.args.get('ETE', '')
  eta_str = time_converter(dep_time_str, ete_str)
  return render_template('time.html', eta=eta_str, ete=ete_str, dep_time=dep_time_str)

app.run()
