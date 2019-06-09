from flask import Flask
from flask import url_for, render_template, request, redirect
from HW7 import *


def get_start_word(fish):

    if fish.startswith('Кара'):
        word = 'карась_S'
    elif fish.startswith('Карп'):
        word = 'карп_S'
    elif fish.startswith('Ко'):
        word = 'корюшка_S'
    elif fish.startswith('Л'):
        word = 'лещ_S'
    elif fish.startswith('О'):
        word = 'окунь_S'
    elif fish.startswith('Со'):
        word = 'сом_S'
    elif fish.startswith('Су'):
        word = 'судак_S'
    elif fish.startswith('Щ'):
        word = 'щука_S'
    elif fish.startswith('Я'):
        word = 'язь_S'
    return word


app = Flask(__name__)


@app.route('/')
def index():
    if request.args:
        urls = {'Главная страница': url_for('index')}

        fish = request.args['fish']
        start_word = get_start_word(fish)
        field = make_graph(start_word)
        c = get_cnt(field)
        info = get_info(field)
        return render_template('results.html', urls=urls,
                               fish=fish, c=c, info=info)
    return render_template('index.html')


@app.route('/results')
def stats():
    urls = {'Главная страница': url_for('index')}
    fish = request.args['fish']
    start_word = get_start_word(fish)
    field = make_graph(start_word)
    c = get_cnt(field)
    info = get_info(field)
    comm = get_comm(field)
    draw_graph(field, comm)

    return render_template('results.html', urls=urls, fish=fish,
                           c=c, info=info)


if __name__ == '__main__':
    app.run(debug=True)
