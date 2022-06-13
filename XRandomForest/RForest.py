from sklearn import tree
from sklearn.tree import plot_tree
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier

import matplotlib.pyplot as plt
import numpy as np
import json
import csv
import glob


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

    for train_idx, val_idx in kfolds.split(features, targets):
        rfc = RandomForestClassifier(class_weight='balanced')
        rfc.fit(features[train_idx], targets[train_idx])

        dtc = tree.DecisionTreeClassifier(class_weight='balanced')
        dtc.fit(features[train_idx], targets[train_idx])

        plt.figure(figsize=(10, 6))
        plot_tree(dtc, feature_names=feature_names, class_names=target_names, filled=True)

        print(f'Random Forest Score : {rfc.score(features[val_idx], targets[val_idx])}')
        print(f'Single Tree Score : {dtc.score(features[val_idx], targets[val_idx])}')
        print()

    plt.show()







