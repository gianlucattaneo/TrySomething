import glob
import csv
import os
import shutil

if __name__ == '__main__':
    path = 'Splits/'
    images_path = '/Users/gianlucacattaneo/Desktop/Balanced/'

    for a in ['True', 'False']:
        for b in ['Positive', 'Negative']:
            os.makedirs(path + a + b)

    for csv_path in glob.glob('csv_res/*.csv'):
        with open(csv_path, 'r') as csv_file:
            csv_dict = csv.DictReader(csv_file, delimiter=';')
            for row in csv_dict:
                url = row['Url']
                label = row['Label']
                guess = row['Guess']
                target = path + ('True' if label == guess else 'False')
                target += 'Positive' if guess == '0' else 'Negative'

                target = f'{target}/{url}'
                source = f'{images_path}{"authorized" if label == "0" else "unauthorized"}/{url}'

                shutil.copy(src=source, dst=target)

