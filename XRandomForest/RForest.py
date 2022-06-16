from sklearn import tree
from sklearn.tree import plot_tree
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier

import matplotlib.pyplot as plt
import numpy as np
import json
import csv
import glob
import math


def get_true_url(image_name, class_, dataset_path='../Stats/total.csv', redirects='../res/original_names.csv'):
    image_name = image_name.replace('.png', '').lower()
    true_name = image_name
    with open(redirects, 'r') as f:
        true_names = csv.DictReader(f, delimiter=';')
        for row in true_names:
            if image_name in row['original']:
                true_name = row['redirect'].replace("http://", "") \
                    .replace("https://", "") \
                    .split("/")[0] \
                    .split("?")[0] \
                    .split(":")[0]
                break

    with open(dataset_path, 'r') as f:
        content = csv.DictReader(f, delimiter=";")
        for row in content:
            if true_name in row['url']:
                return row['url']


def load_folds(order, path='Folds'):
    folds = {}
    for csv_path in glob.glob(f'{path}/*.csv'):
        fold_name = csv_path.split('\\')[-1].split('/')[-1].replace('.csv', '')
        folds[fold_name] = {
            'validation': [],
            'train': []
        }
        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                set_ = 'validation' if row['set'] == 'validation' else 'train'
                class_ = 'authorized' if row['label'] == 'authorized' else 'unauthorized'
                url = get_true_url(row['url'], class_)
                if url:
                    folds[fold_name][set_].append(order.index(url))

    return folds


def comparison_graph(scores1, scores2, label1, label2, n_folds, title):
    plt.title(title)

    max_v = round(max(max(scores1), max(scores2)), 2)
    min_v = round(min(min(scores1), min(scores2)), 2)
    min_v = math.floor(min_v * 10) / 10

    x_range = range(0, n_folds)
    y_range = np.arange(min_v - 0.01, max_v + 0.05, 0.01)

    plt.hlines(y_range, min(x_range), max(x_range), 'black', ':', linewidth=0.1)
    plt.plot(x_range, scores1, 'g', label=label1)
    plt.plot(x_range, scores2, 'r', label=label2)
    plt.xlabel('Folds')
    plt.xticks(x_range)
    plt.yticks(np.arange(min_v - 0.01, max_v + 0.05, 0.05))
    plt.legend()
    plt.show()


if __name__ == '__main__':
    feature_names = ['https',
                     'meta_count',
                     'url_length',
                     'google_verified',
                     'domain',
                     'url_numbers',
                     'special_chars',
                     'ip_location',
                     'trustpilot_review',
                     'instagram',
                     'facebook',
                     'twitter',
                     'pinterest']
    target_names = ['authorized', 'unauthorized']
    features = []
    targets = []

    url_order = []

    with open('../Stats/total.csv', mode='r') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        for index, row in enumerate(reader):
            tmp = []
            for feat in feature_names:
                tmp.append(float(row[feat]))
            url_order.append(row['url'])
            features.append(tmp)
            targets.append(0 if row['class'] == 'authorized' else 1)

    folds = load_folds(order=url_order)

    n_features = len(np.unique(feature_names))
    n_classes = len(np.unique(target_names))

    features = np.array(features)
    targets = np.array(targets)

    rf_scores = []
    st_scores = []

    # kfolds = StratifiedKFold(n_splits=5, shuffle=True)
    # for train_idx, val_idx in kfolds.split(features, targets):

    for fold in folds:
        train_idx = folds[fold]['train']
        val_idx = folds[fold]['validation']

        rfc = RandomForestClassifier(class_weight='balanced', n_estimators=100)
        rfc.fit(features[train_idx], targets[train_idx])

        dtc = tree.DecisionTreeClassifier(class_weight='balanced')
        dtc.fit(features[train_idx], targets[train_idx])

        # plt.figure(figsize=(10, 6))
        # plot_tree(dtc, feature_names=feature_names, class_names=target_names, filled=True)

        rf_scores.append(rfc.score(features[val_idx], targets[val_idx]))
        st_scores.append(dtc.score(features[val_idx], targets[val_idx]))

        print(f'Random Forest Score : {rf_scores[-1]}')
        print(f'Single Tree Score : {st_scores[-1]}')
        print()

    comparison_graph(scores1=rf_scores, scores2=st_scores, label1='Random Forest Score',
                     label2='Single Tree Score', n_folds=5, title='Random Forest vs Decision Tree Comparison')
