import datetime
import json
import random

from model import Menu


def special_menu() -> dict[datetime.date, dict[str, Menu]]:
    menu = {}
    all_dishes = [
        {'name': '大判唐揚げとデミグラスコロッケ', 'nutrition': {'energy': 883, 'protein': 12.26, 'fat': 37.33, 'salt': 2.49}},
        {'name': '天津飯(塩味)', 'nutrition': {'energy': 850, 'protein': 17.69, 'fat': 45.06, 'salt': 4.36}},
        {'name': 'とんてき(四日市)', 'nutrition': {'energy': 673, 'protein': 19.52, 'fat': 24.45, 'salt': 4.34}},
        {'name': '春野菜と豚肉の生姜焼き', 'nutrition': {'energy': 883, 'protein': 12.84, 'fat': 49.2, 'salt': 4.16}},
        {'name': 'ジャンボ鱈フライタルタルソース', 'nutrition': {'energy': 965, 'protein': 18.01, 'fat': 38.73, 'salt': 4.74}},
        {'name': '煮込みハンバーグ', 'nutrition': {'energy': 807, 'protein': 17.2, 'fat': 31.48, 'salt': 3.31}},
        {'name': '黒毛和牛メンチかつデミソース', 'nutrition': {'energy': 838, 'protein': 22.72, 'fat': 20.03, 'salt': 5.55}},
        {'name': '豚塩カルビ丼', 'nutrition': {'energy': 874, 'protein': 11.77, 'fat': 31.82, 'salt': 5.55}},
        {'name': '銀ヒラスの酒麹漬け', 'nutrition': {'energy': 854, 'protein': 14.05, 'fat': 44.22, 'salt': 2.22}},
        {'name': 'チキンカツの和風おろしあん', 'nutrition': {'energy': 715, 'protein': 15.36, 'fat': 38.7, 'salt': 4.35}},
        {'name': 'カニクリームコロッケと海老カツ', 'nutrition': {'energy': 936, 'protein': 24.72, 'fat': 46.23, 'salt': 2.62}},
        {'name': '三色丼', 'nutrition': {'energy': 699, 'protein': 21.36, 'fat': 42.67, 'salt': 5.06}},
        {'name': '酢鶏', 'nutrition': {'energy': 813, 'protein': 23.86, 'fat': 50.64, 'salt': 4.54}},
        {'name': '鶏の照り焼き', 'nutrition': {'energy': 918, 'protein': 13.77, 'fat': 20.61, 'salt': 2.61}},
        {'name': '春野菜の塩あんかけ皿うどん', 'nutrition': {'energy': 992, 'protein': 18.09, 'fat': 44.35, 'salt': 4.77}},
        {'name': '豆腐ハンバーグジンジャーソース', 'nutrition': {'energy': 740, 'protein': 22.21, 'fat': 34.1, 'salt': 4.32}},
        {'name': 'きんぴら豚焼肉', 'nutrition': {'energy': 968, 'protein': 21.43, 'fat': 37.58, 'salt': 4.06}},
        {'name': 'いかの天ぷらピリ辛葱ソース', 'nutrition': {'energy': 759, 'protein': 21.69, 'fat': 42.89, 'salt': 4.53}},
        {'name': '銀鮭の酒粕漬け', 'nutrition': {'energy': 608, 'protein': 14.71, 'fat': 28.26, 'salt': 5.08}},
        {'name': '牛丼', 'nutrition': {'energy': 764, 'protein': 16.77, 'fat': 22.07, 'salt': 4.62}},
        {'name': '味噌とんかつ', 'nutrition': {'energy': 871, 'protein': 15.59, 'fat': 33.77, 'salt': 4.68}},
        {'name': '照焼チキン丼', 'nutrition': {'energy': 651, 'protein': 14.77, 'fat': 40.26, 'salt': 3.67}},
        {'name': '鯖の味噌煮', 'nutrition': {'energy': 975, 'protein': 16.19, 'fat': 31.46, 'salt': 2.78}},
        {'name': '豚肉の黒胡椒スパイス炒め', 'nutrition': {'energy': 735, 'protein': 18.74, 'fat': 29.67, 'salt': 3.14}},
        {'name': '塩レモン唐揚げ', 'nutrition': {'energy': 752, 'protein': 10.07, 'fat': 37.76, 'salt': 4.59}},
        {'name': '牛肉豆腐', 'nutrition': {'energy': 885, 'protein': 24.11, 'fat': 27.96, 'salt': 2.33}},
        {'name': '豚肉と茄子味噌炒めと焼き餃子', 'nutrition': {'energy': 744, 'protein': 21.95, 'fat': 36.14, 'salt': 4.05}},
        {'name': 'ミートドリア', 'nutrition': {'energy': 936, 'protein': 13.11, 'fat': 37.37, 'salt': 3.46}},
        {'name': 'カルボナーラハンバーグ温玉のせ', 'nutrition': {'energy': 674, 'protein': 25.33, 'fat': 30.83, 'salt': 5.64}},
        {'name': 'アジの唐揚げ', 'nutrition': {'energy': 792, 'protein': 20.72, 'fat': 46.98, 'salt': 3.95}},
        {'name': 'ささみチーズカツ', 'nutrition': {'energy': 876, 'protein': 23.5, 'fat': 31.85, 'salt': 2.87}},
        {'name': '照焼チキン丼', 'nutrition': {'energy': 619, 'protein': 10.89, 'fat': 34.73, 'salt': 2.83}},
        {'name': 'プルコギ', 'nutrition': {'energy': 852, 'protein': 24.55, 'fat': 47.37, 'salt': 3.49}},
        {'name': 'たっぷりコーンフライと焼き栗コロッケと焼きそば', 'nutrition': {'energy': 822, 'protein': 17.64, 'fat': 45.6, 'salt': 2.64}},
        {'name': 'グリルハーブチキン', 'nutrition': {'energy': 678, 'protein': 20.23, 'fat': 37.45, 'salt': 4.26}},
        {'name': 'メンチカツエッグタルタルソース', 'nutrition': {'energy': 859, 'protein': 11.63, 'fat': 50.59, 'salt': 3.71}},
        {'name': '根菜ハンバーグと白身魚フライ', 'nutrition': {'energy': 836, 'protein': 20.99, 'fat': 40.0, 'salt': 5.73}},
        {'name': '海老入り野菜かき揚げ丼', 'nutrition': {'energy': 785, 'protein': 13.65, 'fat': 31.55, 'salt': 5.65}}]
    dishes = {}
    random.shuffle(all_dishes)
    start = datetime.date.today() - datetime.timedelta(days=len(all_dishes) / 2)
    for i in range(len(all_dishes) // 2):
        while start.weekday() >= 5:  # skip weekends
            start += datetime.timedelta(days=7 - start.weekday())
        a = all_dishes[i * 2]
        b = all_dishes[i * 2 + 1]
        a = Menu(name=a['name'], price=380, **a['nutrition'], is_permanent=False)
        b = Menu(name=b['name'], price=320, **b['nutrition'], is_permanent=False)
        if a.name in dishes:
            a = dishes[a.name]
        if b.name in dishes:
            b = dishes[b.name]
        today_data = {'A': a,
                      'B': b}
        menu[start] = today_data
        start += datetime.timedelta(days=1)
    return menu


def permanent_menu() -> list[Menu]:
    menu = []
    with open('app/permanent.json', 'r', encoding='utf-8') as f:
        for dish in json.load(f):
            menu.append(Menu(name=dish['name'], price=dish['price'], **dish['nutrition'], is_permanent=True))
    return menu


if __name__ == '__main__':
    special_menu()
    permanent_menu()
