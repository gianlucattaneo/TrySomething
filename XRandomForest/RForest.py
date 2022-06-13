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


def get_true_url(image_name, class_, dataset_path='res/total.json'):
    image_name = image_name.replace('.png', '')
    with open(dataset_path, 'r') as f:
        content = f.read()
        sites = json.loads(content)['sites']

    for true_url in sites[class_]:
        if image_name in true_url:
            return true_url


def load_folds(path='Folds'):
    tmp = {
        'authorized': [],
        'unauthorized': []
    }
    template = {
        'validation': tmp,
        'train': tmp
    }

    folds = {}
    for csv_path in glob.glob(f'{path}/*.csv'):
        fold_name = csv_path.split('\\')[-1].replace('.csv', '')
        folds[fold_name] = template

        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                set_ = 'validation' if row['set'] == 'validation' else 'train'
                class_ = 'authorized' if row['label'] == 'authorized' else 'unauthorized'
                url = get_true_url(row['url'], class_)
                folds[fold_name][set_][class_].append(url)
    return folds


def comparison_graph(scores1, scores2, label1, label2, n_folds, title):
    plt.title(title)

    max_v = round(max(max(scores1), max(scores2)),2)
    min_v = round(min(min(scores1), min(scores2)),2)
    min_v = math.floor(min_v * 10) / 10

    print(min_v)

    x_range = range(0, n_folds)
    y_range = np.arange(min_v - 0.01, max_v + 0.05, 0.01)

    plt.hlines(y_range, min(x_range), max(x_range), 'black', ':', linewidth=0.1)
    plt.plot(x_range, scores1, 'g', label=label1)
    plt.plot(x_range, scores2, 'r', label=label2)
    plt.xlabel('folds')
    plt.xticks(x_range)
    plt.yticks(y_range)
    plt.legend()
    plt.show()
    plt.clf()


if __name__ == '__main__':
    # folds = load_folds()
    #
    # print(folds['Fold1']['validation'])

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

    with open('../Stats/total.csv', mode='r') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        for row in reader:
            tmp = []
            for feat in feature_names:
                tmp.append(float(row[feat]))
            features.append(tmp)
            targets.append(0 if row['class'] == 'authorized' else 1)

    n_features = len(np.unique(feature_names))
    n_classes = len(np.unique(target_names))

    features = np.array(features)
    targets = np.array(targets)

    kfolds = StratifiedKFold(n_splits=5, shuffle=True)
    max_depth = 2

    rf_scores = []
    st_scores = []

    for train_idx, val_idx in kfolds.split(features, targets):
        rfc = RandomForestClassifier(class_weight='balanced', max_depth=max_depth, n_estimators=100)
        rfc.fit(features[train_idx], targets[train_idx])

        dtc = tree.DecisionTreeClassifier(class_weight='balanced', max_depth=max_depth)
        dtc.fit(features[train_idx], targets[train_idx])

        # plt.figure(figsize=(10, 6))
        # plot_tree(dtc, feature_names=feature_names, class_names=target_names, filled=True)

        rf_scores.append(rfc.score(features[val_idx], targets[val_idx]))
        st_scores.append(dtc.score(features[val_idx], targets[val_idx]))

        print(f'Random Forest Score : {rf_scores[-1]}')
        print(f'Single Tree Score : {st_scores[-1]}')
        print()

    comparison_graph(scores1=rf_scores,scores2=st_scores, label1='Random Forest Score',
                     label2='Single Tree Score', n_folds=5,title='TITOLO')
