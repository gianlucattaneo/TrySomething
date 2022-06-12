import glob
import json

def get_url_array(json_):
    if 'sites' in json_:
        if 'authorized' in json_['sites']:
            if 'authorized' in json_['sites']:
                return json_['sites']
    else:
        raise Exception('Json non valido')


if __name__ == '__main__':

    new_dataset = {
        'sites': {
            'authorized': [],
            'unauthorized': []
        }
    }

    classes = ['authorized', 'unauthorized']
    dataset_path = "C:/Users/Gianluca/Desktop/BilanciatoV2"

    with open('../res/total.json', 'r') as f:
        content = f.read()
        sites = get_url_array(json.loads(content))

    for class_ in classes:
        tmp = []
        for image_name in glob.glob(f'{dataset_path}/{class_}/*.png'):
            url = image_name.split('\\')[1].replace('.png', '')
            for true_url in sites[class_]:
                if url in true_url:
                    new_dataset['sites'][class_].append(true_url)
                    break

    print(len(new_dataset['sites']['authorized']))
    print(len(new_dataset['sites']['unauthorized']))

    for url in new_dataset['sites']['authorized']:
        if url in new_dataset['sites']['unauthorized']:
            print(f'{url} duplicato')

    with open('../res/bilanciato_v2.json', 'w') as json_file:
        json.dump(new_dataset, fp=json_file, indent=2)
