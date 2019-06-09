import gensim
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import style
from networkx.algorithms import community


def get_words(filename):
    wfile = open(filename, 'r', encoding='utf-8')
    words = wfile.read().split('\n')
    wfile.close()
    return words


def get_model():
    """urllib.request.urlretrieve(
        "http://rusvectores.org/static/models/rusvectores2/" +
        "ruscorpora_mystem_cbow_300_2_2015.bin.gz",
        "ruscorpora_mystem_cbow_300_2_2015.bin.gz")"""

    m = 'ruscorpora_mystem_cbow_300_2_2015.bin.gz'
    model = gensim.models.KeyedVectors.load_word2vec_format(m, binary=True)
    return model


def find_neighbors(start_words, field):
    model = get_model()
    neighbors = set()

    for word in start_words:
        for neighbor, sim in model.most_similar(positive=word, topn=10):
            if neighbor.endswith('_S') and sim >= 0.5:
                neighbors.add(neighbor)
                field.add_node(neighbor[:-2])
                field.add_edge(word[:-2], neighbor[:-2], weight=sim)
    return neighbors


def make_graph(start_word):
    field = nx.Graph()
    field.add_node(start_word[:-2])

    neighbors = find_neighbors([start_word], field)
    neighbors = find_neighbors(neighbors, field)
    return field


def top_cnt(cnt):
    nodes = sorted(cnt, key=cnt.get, reverse=True)
    return nodes[:5]


def get_cnt(field):
    degree_cnt = ' '.join(top_cnt(nx.degree_centrality(field)))
    betweenness_cnt = ' '.join(top_cnt(nx.betweenness_centrality(field)))
    closeness_cnt = ' '.join(top_cnt(nx.closeness_centrality(field)))
    eigencentrality = ' '.join(top_cnt(nx.eigenvector_centrality(field)))

    d = {'Центральные узлы по degree centrality ': degree_cnt,
         'Центральные узлы по betweenneess centrality ': betweenness_cnt,
         'Центральные узлы по closeness centrality ': closeness_cnt,
         'Центральные узлы по eigencentrality ': eigencentrality}
    return d


def get_info(field):
    d = {
        'Количество узлов ': field.number_of_nodes(),
        'Количество рёбер ': field.number_of_edges(),
        'Плотность графа ': nx.density(field),
        'Диаметр ': nx.diameter(field),
        'Радиус ': nx.radius(field),
        'Коэффициент кластеризации ': nx.average_clustering(field),
        'Коэффициент ассортативности ':
            nx.degree_pearson_correlation_coefficient(field)}
    return d


def get_comm(field):
    communities_generator = community.girvan_newman(field)
    top_level_communities = next(communities_generator)
    next_level_communities = next(communities_generator)
    return sorted(map(sorted, next_level_communities))


def get_colors(field, comms):
    colors = {}

    for i, comms in enumerate(comms):
        for node in comms:
            colors[node] = i / len(comms)

    node_colors = [colors[node] for node in field.node()]
    edge_colors = [((colors[node1] + colors[node2]) / 2)
                   for node1, node2 in field.edges()]
    return node_colors, edge_colors


def draw_graph(field, comms):
    style.use('ggplot')
    pos = nx.spring_layout(field)
    node_colors, edge_colors = get_colors(field, comms)

    cnt = nx.degree_centrality(field)
    node_sizes = [cnt[word] * 1000 for word in field.nodes()]

    nx.draw_networkx_nodes(field, pos, node_size=node_sizes,
                           node_color=node_colors)
    nx.draw_networkx_labels(field, pos, font_size=15)
    nx.draw_networkx_edges(field, pos, edge_color=edge_colors)

    plt.axis('off')
    plt.savefig('static/res.png')


def main():
    start_word = input()
    field = make_graph(start_word)
    centr = get_cnt(field)
    info = get_info(field)
    comm = get_comm(field)
    draw_graph(field, comm)


if __name__ == "__main__":
    main()
