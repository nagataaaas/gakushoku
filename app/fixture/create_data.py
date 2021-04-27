import json
import datetime
import random

def special_menu():
    menu = {}
    with open('special_menu.txt', 'r', encoding='utf-8') as f:
        menu_text = f.read().split('\n')
    date_list = menu_text[::5]
    a_menu_name_list = menu_text[1::5]
    b_menu_name_list = menu_text[3::5]

    for date, a_menu_name, b_menu_name in zip(date_list, a_menu_name_list,
                                              b_menu_name_list):
        date = [datetime.datetime.strptime(x, '%m月%d日') for x in date.split()]
        a_menu_name = a_menu_name.split()
        b_menu_name = b_menu_name.split()

        for i in range(len(date)):
            menu[date[i].replace(year=2021).isoformat()] = {
                'A': {
                    'name': a_menu_name[i],
                    'nutrition': {
                        'energy': random.randint(600, 1000),
                        'protein': round(random.randint(10, 25) + random.random(), 2),
                        'fat': round(random.randint(20, 50) + random.random(), 2),
                        'salt': round(random.randint(2, 5) + random.random(), 2)
                    }
                },
                'B': {
                    'name': b_menu_name[i],
                    'nutrition': {
                        'energy': random.randint(600, 1000),
                        'protein': round(random.randint(10, 25) + random.random(), 2),
                        'fat': round(random.randint(20, 50) + random.random(), 2),
                        'salt': round(random.randint(2, 5) + random.random(), 2)
                    }}}
    with open('special.json', 'w', encoding='utf-8') as f:
        json.dump(menu, f, ensure_ascii=False)


def permanent_menu():
    menu = []
    with open('permanent.txt', 'r', encoding='utf-8') as f:
        names, prices, energies, proteins, fats, salts = f.read().split('\n\n')
    for name, price, energy, protein, fat, salt in zip(names.split(), prices.split(), energies.split(),
                                                       proteins.split(), fats.split(), salts.split()):
        menu.append({'name': name,
                     'price': int(price[1:]),
                     'nutrition': {
                         'energy': int(energy[:-4]),
                         'protein': float(protein[:-1]),
                         'fat': float(fat[:-1]),
                         'salt': float(salt[:-1]),
                     }})
    with open('permanent.json', 'w', encoding='utf-8') as f:
        json.dump(menu, f, ensure_ascii=False)


if __name__ == '__main__':
    special_menu()
    permanent_menu()
