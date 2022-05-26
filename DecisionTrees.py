from sklearn import tree
from sklearn.datasets import load_iris
from sklearn.tree import plot_tree
from sklearn.inspection import DecisionBoundaryDisplay

import matplotlib.pyplot as plt
import numpy as np
import csv


def test():
    iris = load_iris()
    t = tree.DecisionTreeClassifier()
    t.fit(iris.data, iris.target)

    plot_tree(t, feature_names=iris.feature_names, class_names=iris.target_names, filled=True, rounded=True)
    plt.show()


def gennaro():
    iris = load_iris()

    n_features = len(np.unique(iris.feature_names))

    n_classes = len(np.unique(iris.target_names))
    plot_colors = 'ryb'
    plot_step = 0.02

    for pairidx, pair in enumerate([[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]):
        X = iris.data[:, pair]
        y = iris.target

        clf = tree.DecisionTreeClassifier().fit(X, y)

        ax = plt.subplot(2, 3, pairidx + 1)
        plt.tight_layout(h_pad=0.5, w_pad=0.5, pad=2.5)
        DecisionBoundaryDisplay.from_estimator(
            clf,
            X,
            cmap=plt.cm.RdYlBu,
            response_method="predict",
            ax=ax,
            xlabel=iris.feature_names[pair[0]],
            ylabel=iris.feature_names[pair[1]],
        )

        for i, color in zip(range(n_classes), plot_colors):
            idx = np.where(y == i)
            plt.scatter(
                X[idx, 0],
                X[idx, 1],
                c=color,
                label=iris.target_names[i],
                cmap=plt.cm.RdYlBu,
                edgecolor="black",
                s=15,
            )

    plt.suptitle("Decision surface of decision trees trained on pairs of features")
    plt.legend(loc="lower right", borderpad=0, handletextpad=0)
    _ = plt.axis("tight")
    plt.show()


if __name__ == '__main__':
    feature_names = ['meta_count', 'url_length', 'google_verified', 'domain', 'url_numbers']
    target_names = ['authorized', 'unauthorized']
    features = []
    targets = []

    with open('Stats/total.csv', mode='r') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        print(reader.fieldnames)
        for row in reader:
            tmp = []
            for feat in feature_names:
                tmp.append(int(row[feat]))
            features.append(tmp)
            targets.append(0 if row['class'] == 'authorized' else 1)

    n_features = len(np.unique(feature_names))
    n_classes = len(np.unique(target_names))
    features = np.array(features)
    targets = np.array(targets)
    plot_colors = 'ryb'
    plot_step = 0.02

    clf = tree.DecisionTreeClassifier().fit(features, targets)

    plot_tree(clf, feature_names=feature_names, class_names=target_names, filled=True, rounded=True)
    plt.show()
    plt.clf()

    pairs = []
    for i in range(n_features):
        for j in range(i, n_features):
            if i != j:
                pairs.append([i, j])

    for pair_idx, pair in enumerate(pairs):
        X = features[:, pair]
        y = targets

        clf = tree.DecisionTreeClassifier().fit(X, y)

        ax = plt.subplot(5, 3, pair_idx + 1)
        plt.tight_layout(h_pad=0.5, w_pad=0.5, pad=2.5)
        DecisionBoundaryDisplay.from_estimator(
            clf,
            X,
            cmap=plt.cm.RdYlBu,
            response_method="predict",
            ax=ax,
            xlabel=feature_names[pair[0]],
            ylabel=feature_names[pair[1]]
        )

        for i, color in zip(range(n_classes), plot_colors):
            idx = np.where(y == i)
            plt.scatter(
                X[idx, 0],
                X[idx, 1],
                c=color,
                label=target_names[i],
                cmap=plt.cm.RdYlBu,
                edgecolor="black",
                s=15
            )

    plt.suptitle("Decision surface of decision trees trained on pairs of features")
    plt.legend(loc="lower right", borderpad=0, handletextpad=0)
    _ = plt.axis("tight")
    plt.show()




