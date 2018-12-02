import datetime

from flask import Flask
from flask import url_for, render_template, request, redirect
from json2html import json2html
import matplotlib.pyplot as plt


def arr(gender, age, edlevel, gender_ar, age_ar, edlevel_ar):
    # обработка данных из файла с результатами для построения диаграмм
    if gender.startswith('М'):  # мужской пол
        gender_ar[0] += 1
    else:  # женский
        gender_ar[1] += 1

    if age.startswith('До'):
        age_ar[0] += 1  # Возрастная категория до 18
    elif age.startswith('18'):
        age_ar[1] += 1  # 18 - 25
    elif age.startswith('26'):
        age_ar[2] += 1  # 26 - 35
    elif age.startswith('36'):
        age_ar[3] += 1  # 36 - 47
    else:  # 48+
        age_ar[4] += 1

    if edlevel.startswith('Не') and 'ср' in edlevel:
        edlevel_ar[0] += 1  # Неоконченное среднее образование
    elif edlevel.startswith('С'):
        edlevel_ar[1] += 1  # Среднее
    elif edlevel.startswith('В'):
        edlevel_ar[3] += 1  # Неоконченное высшее
    else:  # Высшее
        edlevel_ar[2] += 1


app = Flask(__name__)


@app.route('/')
def index():
    if request.args:
        gender = request.args['gender']
        age = request.args['age']
        edlevel = request.args['edlevel']
        accent = request.args['accent']
        f = open('results.csv', 'a', encoding='utf-8')
        print(gender, age, edlevel, accent, sep='\t', file=f)
        f.close()
        return redirect(url_for('thanks', gender=gender, age=age,
                                edlevel=edlevel, accent=accent))
    return render_template('index.html')


@app.route('/thanks')
def thanks():
    gender = request.args['gender']
    age = request.args['age']
    edlevel = request.args['edlevel']
    accent = request.args['accent']

    urls = {'Главная страница': url_for('index'),
            'Страница статистики': url_for('stats'),
            'Страница с выводом всех данных': url_for('for_json'),
            'Страница с поиском': url_for('search')}
    return render_template('thanks.html', gender=gender, age=age,
                           edlevel=edlevel, accent=accent, urls=urls)


@app.route('/stats')
def stats():
    glabels = ['Мужской', 'Женский']
    alabels = ['До 18', '18 - 25', '25 - 35', '36 - 47', '48+']
    elabels = ['Неоконченное среднее', 'Среднее',
               'Неоконченное высшее', 'Высшее']

    gender_ju = [0] * 2  # 0 - м, 1 - ж, далее аналогично
    gender_o = [0] * 2
    gender_both = [0] * 2
    age_ju = [0] * 5  # 0 - До 18, 1 - 18-25 и т.д.
    age_o = [0] * 5
    age_both = [0] * 5
    edlevel_ju = [0] * 4
    edlevel_o = [0] * 4
    edlevel_both = [0] * 4
    with open('results.csv', 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines()]
    for line in lines:
        line = line.split('\t')
        gender = line[0]
        age = line[1]
        edlevel = line[2]
        accent = line[3]
        if 'Ю' in accent:  # Вариант произнесения НьЮтон
            arr(gender, age, edlevel, gender_ju, age_ju, edlevel_ju)
        elif accent.startswith('Оба'):  # Оба варианта
            arr(gender, age, edlevel, gender_both, age_both, edlevel_both)
        else:  # Вариант произнесения НьютОн
            arr(gender, age, edlevel, gender_o, age_o, edlevel_o)

    plt.title("Распределение пола респондентов, НьЮтон")
    plt.pie(gender_ju, labels=glabels, shadow=True)
    plt.savefig('static/gender_ju.png')
    plt.clf()

    plt.title("Распределение пола респондентов, НьютОн")
    plt.pie(gender_o, labels=glabels, shadow=True)
    plt.savefig('static/gender_o.png')
    plt.clf()

    plt.title("Распределение пола респондентов, оба варианта")
    plt.pie(gender_o, labels=glabels, shadow=True)
    plt.savefig('static/gender_both.png')
    plt.clf()

    plt.title("Распределение возрастов респондентов, НьЮтон")
    plt.pie(age_ju, labels=alabels, shadow=True)
    plt.savefig('static/age_ju.png')
    plt.clf()

    plt.title("Распределение возрастов респондентов, НьютОн")
    plt.pie(age_o, labels=alabels, shadow=True)
    plt.savefig('static/age_o.png')
    plt.clf()

    plt.title("Распределение возрастов респондентов, оба варианта")
    plt.pie(age_both, labels=alabels, shadow=True)
    plt.savefig('static/age_both.png')
    plt.clf()

    plt.title("Распределение уровня образования респондентов, НьЮтон")
    plt.pie(edlevel_ju, labels=elabels, shadow=True)
    plt.savefig('static/edlevel_ju.png')
    plt.clf()

    plt.title("Распределение уровня образования респондентов, НьютОн")
    plt.pie(edlevel_o, labels=elabels, shadow=True)
    plt.savefig('static/edlevel_o.png')
    plt.clf()

    plt.title("Распределение уровня образования, оба варианта")
    plt.pie(edlevel_both, labels=elabels, shadow=True)
    plt.savefig('static/edlevel_both.png')

    urls = {'Главная страница': url_for('index'),
            'Страница с выводом всех данных': url_for('for_json'),
            'Страница с поиском': url_for('search')}

    return render_template('stats.html', urls=urls)


@app.route('/json')
def for_json():
    res = []
    with open('results.csv', 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines()]
    for line in lines:
        line = line.split('\t')
        res.append({'Вариант ударения': line[3], 'Пол': line[0],
                    'Возраст': line[1], 'Уровень образования': line[2]})
    data = json2html.convert(json=res)
    return render_template('json.html', data=data)


@app.route('/search')
def search():
    if request.args:
        gender = request.args['gender']
        age = request.args['age']
        return redirect(url_for('results', gender=gender, age=age))
    return render_template('search.html')


@app.route('/results')
def results():
    res = []
    gender = request.args['gender']
    age = request.args['age']
    with open('results.csv', 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines()]
    for line in lines:
        line = line.split('\t')
        if line[0] == gender and line[1] == age:
            res.append({'Вариант ударения': line[3], 'Пол': line[0],
                        'Возраст': line[1], 'Уровень образования': line[2]})
    data = json2html.convert(json=res)

    urls = {'Главная страница': url_for('index'),
            'Страница статистики': url_for('stats'),
            'Страница с выводом всех данных': url_for('for_json'),
            'Страница с поиском': url_for('search')}
    return render_template('results.html', gender=gender,
                           age=age, data=data, urls=urls)


if __name__ == '__main__':
    app.run(debug=True)
