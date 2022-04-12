import datetime
import json
import sys
from unittest.mock import MagicMock

sys.path.append('./')

import pytest
from fastapi.testclient import TestClient

import app.controller as controller
import app.scheme as scheme
from app.api import app
from app.config import MAX_SOLD_OUT_POST_PER_DAY, MAX_CONGESTION_POST_PER_DAY
from app.load_fixture import (create_database, clear_database, load_special, load_permanent)
from app.model import SessionLocal
from app.fixture.create_data import (permanent_menu, special_menu)


class TestController:
    test_sub = 'test_sub'

    def setup_method(self, method):
        self.db = SessionLocal()

        clear_database()
        create_database()
        permanent_data = permanent_menu()
        special_data = special_menu()

        ps = load_permanent(permanent_data)
        ls = load_special(special_data)

        # load_like(400, ps + ls)

        self.menu_ids = ps + ls

    def teardown_method(self, method):
        self.db.close()

    def test_get_permanent(self):
        permanent = controller.all_permanent(self.db)
        permanent_menu_names = sorted(['カレーライス', 'カツカレー', '親子丼', 'カツ丼', 'カレーうどん',
                                       '塩ラーメン', 'かけうどん', 'かけそば', 'チャーハン', 'ライス(210g)'])
        assert isinstance(permanent, scheme.PermanentModel)
        assert sorted(menu.name for menu in permanent.menus) == permanent_menu_names

    def test_get_no_special(self):
        specials = controller.get_special([], self.db)
        assert specials.schedules == []

    def test_get_single_special(self):
        specials = controller.get_special([datetime.date(2021, 4, 14)], self.db)
        assert specials.schedules[0].month == 4
        assert specials.schedules[0].day == 14

        assert specials.schedules[0].a_menu.name == "春野菜の塩あんかけ皿うどん"
        assert specials.schedules[0].a_menu.price == 380
        assert specials.schedules[0].a_menu.like_count == 0
        assert specials.schedules[0].a_menu.is_sold_out is False

    def test_get_specials(self):
        specials = controller.get_special([datetime.date(2021, 4, 14), datetime.date(2021, 4, 15)], self.db)
        assert specials.schedules[0].month == 4
        assert specials.schedules[0].day == 14

        assert specials.schedules[1].month == 4
        assert specials.schedules[1].day == 15

        assert len(specials.schedules) == 2

    def test_get_holiday_specials(self):
        specials = controller.get_special([datetime.date(2021, 4, 14), datetime.date(2021, 4, 15),
                                           datetime.date(2021, 4, 17)], self.db)
        assert specials.schedules[0].month == 4
        assert specials.schedules[0].day == 14

        assert specials.schedules[1].month == 4
        assert specials.schedules[1].day == 15

        assert len(specials.schedules) == 2

    def test_like_this_invalid_id(self):
        result = controller.like_this('this_is_invalid', self.test_sub, self.db)
        assert result is False

    def test_like_this(self):
        result = controller.like_this(self.menu_ids[0], self.test_sub, self.db)
        assert result is True

    def test_like_this_permanent_updated(self):
        result = controller.like_this(self.menu_ids[0], self.test_sub, self.db)
        assert result is True
        permanent = controller.all_permanent(self.db)
        for perm in permanent.menus:
            if perm.id == self.menu_ids[0]:
                assert perm.like_count == 1
            else:
                assert perm.like_count == 0

    def test_like_this_special_updated(self):
        result = controller.like_this('9fea3eccf63c5f65bea172060293be9f', self.test_sub, self.db)
        assert result is True
        specials = controller.get_special([datetime.date(2021, 4, 14)], self.db)
        assert specials.schedules[0].a_menu.like_count == 1
        assert specials.schedules[0].b_menu.like_count == 0

    def test_like_this_duplication(self):
        controller.like_this(self.menu_ids[0], self.test_sub, self.db)
        result = controller.like_this(self.menu_ids[0], self.test_sub, self.db)
        assert result is False

    def test_dislike_this(self):
        controller.like_this(self.menu_ids[0], self.test_sub, self.db)
        result = controller.dislike_this(self.menu_ids[0], self.test_sub, self.db)
        assert result is True

    def test_dislike_this_invalid_id(self):
        result = controller.dislike_this('this_is_invalid', self.test_sub, self.db)
        assert result is False

    def test_dislike_this_not_exist(self):
        result = controller.dislike_this(self.menu_ids[0], self.test_sub, self.db)
        assert result is False

    def test_get_likes_by_sub_no_like(self):
        result = controller.get_likes_by_sub(self.test_sub, self.db)
        assert result == []

    def test_get_likes_by_sub_single_like(self):
        controller.like_this(self.menu_ids[0], self.test_sub, self.db)
        result = controller.get_likes_by_sub(self.test_sub, self.db)
        assert result == [self.menu_ids[0]]

    def test_get_likes_by_sub_multiple_like(self):
        controller.like_this(self.menu_ids[0], self.test_sub, self.db)
        controller.like_this(self.menu_ids[1], self.test_sub, self.db)
        controller.like_this(self.menu_ids[2], self.test_sub, self.db)
        result = controller.get_likes_by_sub(self.test_sub, self.db)
        assert sorted(result) == sorted([self.menu_ids[0], self.menu_ids[1], self.menu_ids[2]])

    def test_is_valid_menu_id(self):
        for id_ in self.menu_ids:
            assert controller.is_valid_menu_id(id_, self.db) is True
        for id_ in range(10):
            assert controller.is_valid_menu_id(str(id_), self.db) is False

    def test_get_menu(self):
        for id_ in self.menu_ids:
            assert isinstance(controller.get_menu(id_, self.db), scheme.MenuModel)
        for id_ in range(10):
            assert controller.get_menu(str(id_), self.db) is None

    def test_set_sold_out(self):
        for i, id_ in enumerate(self.menu_ids):
            assert controller.set_sold_out(id_, True, str(i), self.db) is True
        for id_ in self.menu_ids:
            assert controller.get_menu(id_, self.db).is_sold_out is True

    def test_get_congestion(self):
        assert controller.get_congestion(self.db) == 0

    def test_set_congestion(self):
        controller.set_congestion(0, self.test_sub, self.db)
        assert controller.get_congestion(self.db) == 0
        controller.set_congestion(1, self.test_sub, self.db)
        assert controller.get_congestion(self.db) == 1
        controller.set_congestion(2, self.test_sub, self.db)
        assert controller.get_congestion(self.db) == 2

    def test_set_congestion_max_request(self):
        for _ in range(MAX_CONGESTION_POST_PER_DAY):
            assert controller.set_congestion(0, self.test_sub, self.db) == True
        assert controller.set_congestion(0, self.test_sub, self.db) == False


client = TestClient(app)


class TestAPI:
    test_token = ('eyJhbGciOiJSUzI1NiIsImtpZCI6Ijc3NDU3MzIxOGM2ZjZhMmZlNTBlMjlhY2JjNjg2NDMyODYzZmM5YzMiLCJ0eXAiOi'
                  'JKV1QifQ.eyJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiYXpwIjoiMTA0NjY4MTMwMDMwMC0yc2gzMG50czB1NTA1d'
                  'XN0Ympkc280M3A1Z2FhcGg3dC5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsImF1ZCI6IjEwNDY2ODEzMDAzMDAtMnN'
                  'oMzBudHMwdTUwNXVzdGJqZHNvNDNwNWdhYXBoN3QuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTU3N'
                  'TcwOTMwMzcyNTYxMDA1MTIiLCJoZCI6InMuYWthc2hpLmFjLmpwIiwiZW1haWwiOiJlMTcyOEBzLmFrYXNoaS5hYy5qcCI'
                  'sImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoiZzQ4NHBXNjRVVndhZm9jVVNxOE9XUSIsIm5hbWUiOiLmsLjnl'
                  'LDlpKflkowiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EtL0FPaDE0R2lfREpYcTN'
                  'aMTZZc0xFOHJHSEFPNnRPTmRZeU5MTWtIZ01qbUFqPXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6IuWkp-WSjCIsImZhbWlseV9uY'
                  'W1lIjoi5rC455SwIiwibG9jYWxlIjoiamEiLCJpYXQiOjE2MTgzMjUzMTQsImV4cCI6MTYxODMyODkxNCwianRpIjoiZTI'
                  '2YjQyYTcxYjBmYjdjM2Y2ODgyNzE3NDkzMDNkMTA3MzU0NzIzMiJ9.hLYybrt0mb-St-mDGbryZukfWeHeBRw4zeCq2mzE'
                  '5Ee_7BRG4pLnc_OJZYajVHiGk9FeUZWwAJ0sO6DLuGz-4fPt7Eg9vPUfs4vae4uNsSH2dya4FW-DRueXEOW6HYMq_2wfP9'
                  'p87w9pTa7TLPbrtwp8gAfVsWiSxchm5gSYh9D9wWibMQNl2_HieSI4GZGWDLp4I4tRj2LQmjIXlWs48dyTwVkGe8ppcTJ0'
                  'R-YK4PzgfjFNRULBWD5iry6yufOGRbGf71_v9S0hEH-ik-ITwKJXkSz9fBktotWy6GVbLfOrw8eqavQiermPeRUWwzfU2C'
                  'nIY1VqKT6rgID1dtyQ5Q'
                  )
    test_sub = 'test_sub'

    @pytest.fixture()
    def set(self):
        clear_database()
        create_database()

        with open('app/fixture/permanent.json', 'r', encoding='utf-8') as f:
            permanent_json = json.load(f)
        with open('app/fixture/special.json', 'r', encoding='utf-8') as f:
            special_json = json.load(f)

        ps = load_permanent(permanent_json)
        ls = load_special(special_json)

        # load_like(400, ps + ls)

        self.menu_ids = ps + ls
        yield

    def test_index(self):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_api_menu_no_date(self):
        resp = client.get('/api/v1/menu')
        assert resp.status_code == 400

    def test_api_menu_invalid_date(self):
        resp = client.get('/api/v1/menu?date=4:32')
        assert resp.status_code == 400

        resp = client.get('/api/v1/menu?date=this:bad')
        assert resp.status_code == 400

        resp = client.get('/api/v1/menu?date=thisbad')
        assert resp.status_code == 400

    def test_api_menu_single(self):
        resp = client.get('/api/v1/menu?date=4:14')
        assert resp.status_code == 200

        data = resp.json()
        assert len(data['schedules']) == 1
        assert data['schedules'][0]['a_menu']['id'] == '9fea3eccf63c5f65bea172060293be9f'
        assert data['schedules'][0]['month'] == 4
        assert data['schedules'][0]['day'] == 14

    def test_api_menu_multi(self):
        resp = client.get('/api/v1/menu?date=4:14&date=4:15&date=4:17')
        assert resp.status_code == 200

        data = resp.json()
        assert len(data['schedules']) == 2
        assert data['schedules'][0]['a_menu']['id'] == '9fea3eccf63c5f65bea172060293be9f'
        assert data['schedules'][0]['month'] == 4
        assert data['schedules'][0]['day'] == 14

        assert data['schedules'][1]['a_menu']['id'] == 'ba1b53f0fcaa5aae96259b0a78edc6b4'
        assert data['schedules'][1]['month'] == 4
        assert data['schedules'][1]['day'] == 15

    def test_api_permanent(self):
        resp = client.get('/api/v1/menu/permanent')
        assert resp.status_code == 200

        data = resp.json()
        assert len(data['menus']) == 10
        permanent_menu_names = sorted(['カレーライス', 'カツカレー', '親子丼', 'カツ丼', 'カレーうどん',
                                       '塩ラーメン', 'かけうどん', 'かけそば', 'チャーハン', 'ライス(210g)'])
        assert sorted(menu['name'] for menu in data['menus']) == permanent_menu_names

    def test_api_sold_out(self, set):
        resp = client.post(f'/api/v1/sold-out', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token,
            'is_sold_out': True
        }))
        assert resp.status_code == 200

        resp = client.get('/api/v1/menu?date=4:14')
        assert resp.status_code == 200

        data = resp.json()
        assert len(data['schedules']) == 1
        assert data['schedules'][0]['a_menu']['id'] == '9fea3eccf63c5f65bea172060293be9f'
        assert data['schedules'][0]['a_menu']['is_sold_out'] == True

        resp = client.post(f'/api/v1/sold-out', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token,
            'is_sold_out': False
        }))
        assert resp.status_code == 200

        resp = client.get('/api/v1/menu?date=4:14')
        assert resp.status_code == 200

        data = resp.json()
        assert len(data['schedules']) == 1
        assert data['schedules'][0]['a_menu']['id'] == '9fea3eccf63c5f65bea172060293be9f'
        assert data['schedules'][0]['a_menu']['is_sold_out'] == False

    def test_api_sold_out_request_max_reach(self, set):
        for _ in range(MAX_SOLD_OUT_POST_PER_DAY):
            resp = client.post(f'/api/v1/sold-out', data=json.dumps({
                'menu_id': '9fea3eccf63c5f65bea172060293be9f',
                'token': self.test_token,
                'is_sold_out': True
            }))
            assert resp.status_code == 200
        resp = client.post(f'/api/v1/sold-out', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token,
            'is_sold_out': True
        }))
        assert resp.status_code == 429

    def test_api_sold_out_request_max_reach_next_day(self, set, monkeypatch):
        for _ in range(MAX_SOLD_OUT_POST_PER_DAY):
            resp = client.post('/api/v1/sold-out', data=json.dumps({
                'menu_id': '9fea3eccf63c5f65bea172060293be9f',
                'token': self.test_token,
                'is_sold_out': True
            }))
            assert resp.status_code == 200
        resp = client.post('/api/v1/sold-out', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token,
            'is_sold_out': True
        }))
        assert resp.status_code == 429

        datetime_mock = MagicMock(wraps=datetime.datetime)
        datetime_mock.today.return_value = datetime.datetime.now() + datetime.timedelta(days=1)
        monkeypatch.setattr(datetime, "datetime", datetime_mock)

        resp = client.post('/api/v1/sold-out', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token,
            'is_sold_out': True
        }))
        assert resp.status_code == 200

    def test_api_like_me_empty(self, set):
        resp = client.get(f'/api/v1/like/me?token={self.test_token}')
        assert resp.status_code == 200
        data = resp.json()

        assert data['likes'] == []

    def test_api_like(self, set):
        resp = client.post('/api/v1/like', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token
        }))
        assert resp.status_code == 200
        resp = client.get(f'/api/v1/like/me?token={self.test_token}')
        data = resp.json()

        assert data['likes'] == ['9fea3eccf63c5f65bea172060293be9f']

        resp = client.post('/api/v1/like', data=json.dumps({
            'menu_id': '6d35e3e784b0500db166b88fe8c793c5',
            'token': self.test_token
        }))
        assert resp.status_code == 200
        resp = client.get(f'/api/v1/like/me?token={self.test_token}')
        data = resp.json()

        assert sorted(data['likes']) == sorted(['9fea3eccf63c5f65bea172060293be9f', '6d35e3e784b0500db166b88fe8c793c5'])

    def test_api_like_duplicate(self, set):
        client.post('/api/v1/like', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token
        }))
        resp = client.post('/api/v1/like', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token
        }))
        assert resp.status_code == 409
        resp = client.get(f'/api/v1/like/me?token={self.test_token}')
        data = resp.json()

        assert data['likes'] == ['9fea3eccf63c5f65bea172060293be9f']

    def test_api_like_delete(self, set):
        client.post('/api/v1/like', data=json.dumps({
            'menu_id': '9fea3eccf63c5f65bea172060293be9f',
            'token': self.test_token
        }))
        client.post('/api/v1/like', data=json.dumps({
            'menu_id': '6d35e3e784b0500db166b88fe8c793c5',
            'token': self.test_token
        }))

        resp = client.get(f'/api/v1/like/me?token={self.test_token}')
        data = resp.json()

        assert sorted(data['likes']) == sorted(['9fea3eccf63c5f65bea172060293be9f', '6d35e3e784b0500db166b88fe8c793c5'])

        client.delete(f'/api/v1/like?token={self.test_token}&menu_id=6d35e3e784b0500db166b88fe8c793c5')
        resp = client.get(f'/api/v1/like/me?token={self.test_token}')
        data = resp.json()

        assert data['likes'] == ['9fea3eccf63c5f65bea172060293be9f']

        client.delete(f'/api/v1/like?token={self.test_token}&menu_id=9fea3eccf63c5f65bea172060293be9f')
        resp = client.get(f'/api/v1/like/me?token={self.test_token}')
        data = resp.json()

        assert data['likes'] == []

    def test_api_like_delete_no_target(self, set):
        resp = client.delete(f'/api/v1/like?token={self.test_token}&menu_id=9fea3eccf63c5f65bea172060293be9f')
        assert resp.status_code == 409

        resp = client.get(f'/api/v1/like/me?token={self.test_token}')
        data = resp.json()

        assert data['likes'] == []

    def test_api_get_congestion(self, set):
        resp = client.get(f'/api/v1/congestion')
        assert resp.status_code == 200

        assert resp.json()['congestion'] == 0

    def test_api_set_congestion(self, set):
        resp = client.post(f'/api/v1/congestion', data=json.dumps({
            'congestion': 1,
            'token': self.test_token
        }))
        assert resp.status_code == 200

        resp = client.get(f'/api/v1/congestion')
        assert resp.json()['congestion'] == 1

        resp = client.post(f'/api/v1/congestion', data=json.dumps({
            'congestion': 3,
            'token': self.test_token
        }))
        assert resp.status_code == 400

        resp = client.get(f'/api/v1/congestion')
        assert resp.json()['congestion'] == 1

    def test_api_set_congestion_max_request(self, set):
        for _ in range(MAX_CONGESTION_POST_PER_DAY):
            resp = client.post(f'/api/v1/congestion', data=json.dumps({
                'congestion': 1,
                'token': self.test_token
            }))
            assert resp.status_code == 200

        resp = client.post(f'/api/v1/congestion', data=json.dumps({
            'congestion': 1,
            'token': self.test_token
        }))
        assert resp.status_code == 400

    def test_websocket_sold_out(self, set):
        ws_client = TestClient(app)
        with ws_client.websocket_connect("/api/v1/ws") as ws_connection:
            client.post(f'/api/v1/sold-out', data=json.dumps({
                'menu_id': '9fea3eccf63c5f65bea172060293be9f',
                'token': self.test_token,
                'is_sold_out': True
            }))
            data = ws_connection.receive_json()
            assert data == {'id': '9fea3eccf63c5f65bea172060293be9f',
                            'is_sold_out': True,
                            'method': 'sold_out'}

            client.post(f'/api/v1/sold-out', data=json.dumps({
                'menu_id': '9fea3eccf63c5f65bea172060293be9f',
                'token': self.test_token,
                'is_sold_out': False
            }))
            data = ws_connection.receive_json()
            assert data == {'id': '9fea3eccf63c5f65bea172060293be9f',
                            'is_sold_out': False,
                            'method': 'sold_out'}

    def test_websocket_congestion(self, set):
        ws_client = TestClient(app)
        with ws_client.websocket_connect("/api/v1/ws") as ws_connection:
            client.post(f'/api/v1/congestion', data=json.dumps({
                'congestion': 1,
                'token': self.test_token
            }))
            data = ws_connection.receive_json()
            assert data == {'congestion': 1,
                            'method': 'congestion'}

            client.post(f'/api/v1/congestion', data=json.dumps({
                'congestion': 0,
                'token': self.test_token
            }))
            data = ws_connection.receive_json()
            assert data == {'congestion': 0,
                            'method': 'congestion'}


if __name__ == '__main__':
    pytest.main()
