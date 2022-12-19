from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template('home.html')

@app.route("/result", methods=['POST'])
def result():
    name = str(request.form.get('name'))
    url = 'https://finance.yahoo.com/quote/' + name + '?p=' + name + '&.tsrc=fin-srch'
    headers = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        'Accept-Language': 'en'
    }
    response = requests.get(url, headers=headers)
    a = int(response.status_code)
    if (a != 200):
        b = ''
        return render_template('home.html', b=b)
    soup = BeautifulSoup(response.text, "html.parser")
    if (soup.find('h1', {"class": "D(ib) Fz(18px)"}) is None):
        b = ''
        return render_template('home.html', b=b)
    company = soup.find('h1', {"class": "D(ib) Fz(18px)"}).text
    income = 0
    c = 0
    if (len(soup.find('fin-streamer', {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.split(',')) > 1):
        price = float(soup.find('fin-streamer', {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.split(',')[0]) * 1000 + float(soup.find('fin-streamer', {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text.split(',')[1])
    else:
        price = soup.find('fin-streamer', {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
    dailyRange = soup.find_all('td', {"class": "Ta(end) Fw(600) Lh(14px)"})[4].text
    if (soup.find_all('td', {"class": "C($primaryColor) W(51%)"})[15].text == '1y Target Est' and soup.find_all('td', {"class": "Ta(end) Fw(600) Lh(14px)"})[15].text != 'N/A'):
        if (len(soup.find_all('td', {"class": "Ta(end) Fw(600) Lh(14px)"})[15].text.split(',')) > 1):
            targetEst = float(soup.find_all('td', {"class": "Ta(end) Fw(600) Lh(14px)"})[15].text.split(',')[0]) * 1000 + float(soup.find_all('td', {"class": "Ta(end) Fw(600) Lh(14px)"})[15].text.split(',')[1])
        else:
            targetEst = soup.find_all('td', {"class": "Ta(end) Fw(600) Lh(14px)"})[15].text
        income = round(float(targetEst) - float(price), 2)
    else:
        c = 1
        targetEst = 'не указана'
        income = 'её нет'

    url1 = 'https://finance.yahoo.com/quote/' + name + '/history'
    response1 = requests.get(url1, headers=headers)
    soup1 = BeautifulSoup(response1.text, "html.parser")
    priceM = []
    for i in range(4, 126, 6):
        priceM.append(soup1.find_all('td', {"class": "Py(10px) Pstart(10px)"})[i].text)
    y = []
    plt.switch_backend('Agg')
    fig = plt.figure(figsize=(16, 5))
    for i in range(len(priceM)):
        y.append(soup1.find_all('td', {"class": "Py(10px) Ta(start) Pend(10px)"})[i].text.split(',')[0])
    for i in range(len(priceM)):
        priceM[i] = float(priceM[i])
    priceM1 = priceM[::-1]
    y1 = y[::-1]
    plt.grid()
    plt.plot(y1, priceM1)
    plt.xlabel('Дата')
    plt.ylabel('Цена в $')
    buf = BytesIO()
    fig.savefig(buf, format='png')
    data = base64.b64encode(buf.getbuffer()).decode('ascii')

    url2 = 'https://finance.yahoo.com/quote/' + name +'/holders'
    response2 = requests.get(url2, headers=headers)
    soup2 = BeautifulSoup(response2.text, "html.parser")
    holders = []
    holderName = []
    if (soup2.find('td', {"class": "Ta(start) Pend(10px)"}) is None):
        f = 1
        return render_template('result.html', company=company, price=price, dailyRange=dailyRange, targetEst=targetEst, income=income,
        picture=data, f=f, c=c)
    f = 0
    other = 100.0
    for i in range(0, 10):
        holderName.append(soup2.find_all('td', {"class": "Ta(start) Pend(10px)"})[i].text)
    for i in range(2, 41, 4):
        holders.append(float(soup2.find_all('td', {"class": "Ta(end) Pstart(10px)"})[i].text.split('%')[0]))
        other -= float(soup2.find_all('td', {"class": "Ta(end) Pstart(10px)"})[i].text.split('%')[0])
    holders.append(other)
    holderName.append('Other')
    fig2 = plt.figure(figsize=(20, 10))
    plt.pie(holders, explode=(0,0,0,0,0.1,0.2,0.4,0.3,0.2,0.1,0.1) ,autopct='%.1f%%')
    plt.legend(holderName, loc='center left', fontsize=10, bbox_to_anchor=(1, 0, 0.5, 1))
    buf2 = BytesIO()
    fig2.savefig(buf2, format='png')
    data2 = base64.b64encode(buf2.getbuffer()).decode('ascii')

    return render_template('result.html', company=company, price=price, dailyRange=dailyRange, targetEst=targetEst, income=income,
    picture=data, picture2=data2, f=f, c=c)


@app.route("/ticker")
def ticker():
    return render_template('ticker.html')

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)