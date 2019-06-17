from flask import Flask
from flask import url_for, render_template, request, redirect
import sqlite3
import json
import pandas
import matplotlib.pyplot as plt
from collections import Counter
import nltk
# nltk.download("punkt")


CONN = sqlite3.connect('corpora.db', check_same_thread=False)


def add_to_dict(word, d, name):
    if word not in d:
        d[word] = [name]
    else:
        d[word].append(name)


def text_proc(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    for token in tokens:
        if not str(token).isalpha():
            tokens.remove(token)
    return tokens


def proc(conn, name, text, dialect, author, writer, year):
    global D_1, D_2, D_3
    tokens = text_proc(text)
    for token in tokens:
        f = open('words.csv', 'a', encoding='utf-8')
        print(token, dialect, name, sep='\t', file=f)
        f.close()

    conn.execute('INSERT INTO texts(name, text, dialect, author, writer, year,'
                 ' tokens) VALUES (?, ?, ?, ?, ?, ?, ?)', (name, text, dialect,
                                                           author, writer,
                                                           year,
                                                           json.dumps(tokens)))
    conn.commit()


app = Flask(__name__)


@app.route('/')
def index():
    urls = {'Узнать больше о корпусе': url_for('info'),
            'Добавить новые тексты в корпус': url_for('add'),
            'Искать в корпусе': url_for('search')}

    return render_template('index.html', urls=urls)


@app.route('/search')
def search():
    urls = {'Главная страница': url_for('index')}
    texts = {}
    if request.args:
        word = request.args['word']
        dialect = request.args['dialect']

        with open('words.csv', 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines()]
            for line in lines:
                line = line.split('\t')
                if line[0] == word and line[1] == dialect:
                    name = line[2]
                    ans = CONN.execute('SELECT * FROM texts WHERE name =(?)',
                                       (name, ))
                    texts[name] = ans.fetchone()
        f.close
        return redirect(url_for('thanks', urls=urls, texts=texts))

    return render_template('search.html', urls=urls)


@app.route('/add')
def add():

    if request.args:
        name = request.args['name']
        text = request.args['text']
        dialect = request.args['dialect']
        author = request.args['author']
        writer = request.args['writer']
        year = request.args['year']
        proc(CONN, name, text, dialect, author, writer, year)
        CONN.commit()
    return render_template('add.html')


@app.route('/thanks')
def thanks():
    urls = {'Искать в корпусе': url_for('search'),
            'Добавить новые тексты в корпус': url_for('add'),
            'Узнать больше о корпусе': url_for('info')}
    return render_template('index.html')


@app.route('/info')
def info():
    years = []
    for year in CONN.execute('SELECT year FROM texts').fetchall():
        years.append(year[0])
    plt.title("Распределение текстов по годам")
    plt.hist(years)
    plt.savefig('static/year.png')
    plt.clf()

    dialects = []
    for dialect in CONN.execute('SELECT dialect FROM texts').fetchall():
        dialects.append(dialect[0])
    dialect_counts = Counter(dialects)

    df = pandas.DataFrame.from_dict(dialect_counts, orient='index')
    df.plot(kind='bar')
    plt.title("Распределение текстов по карельским наречиям")
    plt.tight_layout()
    plt.savefig('static/dialect.png')
    plt.clf()

    urls = {'Главная страница': url_for('index')}
    return render_template('info.html', urls=urls)


if __name__ == '__main__':
    app.run(debug=True)
