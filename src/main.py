import requests
import random
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
import psycopg2
import queue
import json
import threading
from multiprocessing.dummy import Pool


seen = queue.Queue()
cores: int = 4
pool = Pool(cores)
limit: int = 4600000

conn: psycopg2 = \
    psycopg2.connect(user='salvadorguzman', password='', host='127.0.0.1', port='5432', database='personal')


def insert_startup(cursor: psycopg2, data: List[str]) -> None:
    sql_insert_chann: str = f'INSERT INTO personal.startups.angel_list ' \
                       '(id, company_name, high_concept, product_desc, slug_url, logo_url, to_s, ' \
                       'video_url, video_thumbnail, twitter_url, blog_url, company_url, ' \
                       'facebook_url, linkedin_url, producthunt_url) ' \
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' \
                       'ON CONFLICT(id) DO NOTHING'

    cursor.execute(sql_insert_chann, data)


def insert_null(cursor: psycopg2, num: int) -> None:
    sql_insert_chann: str = f'INSERT INTO personal.startups.angel_list ' \
        '(id, company_name, high_concept, product_desc, slug_url, logo_url, to_s, ' \
        'video_url, video_thumbnail, twitter_url, blog_url, company_url, ' \
        'facebook_url, linkedin_url, producthunt_url) ' \
        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' \
        'ON CONFLICT(id) DO NOTHING'

    data: List[Optional[int]] = [num] + ([None] * 14)
    cursor.execute(sql_insert_chann, data)


def none_or_str(s: str):
    if s is None:
        return None
    else:
        return s.replace('\0', '')


def json_to_array(js: json) -> List[str]:
    return [
        js['id'],
        none_or_str(js['company_name']),
        none_or_str(js['high_concept']),
        none_or_str(js['product_desc']),
        none_or_str(js['slug_url']),
        none_or_str(js['logo_url']),
        none_or_str(js['to_s']),
        none_or_str(js['video_url']),
        none_or_str(js['video_thumbnail']),
        none_or_str(js['twitter_url']),
        none_or_str(js['blog_url']),
        none_or_str(js['company_url']),
        none_or_str(js['facebook_url']),
        none_or_str(js['linkedin_url']),
        none_or_str(js['producthunt_url']),
    ]


def print_daemon() -> None:
    while True:
        msg_payload: Tuple[int, str, bool] = seen.get(block=True)
        print(msg_payload)

        id: int = msg_payload[0]
        msg: str = msg_payload[1]
        good: bool = msg_payload[2]

        cursor: psycopg2 = conn.cursor()
        if good:
            js: json = json.loads(msg)
            arr: List[str] = json_to_array(js['startup'])

            insert_startup(cursor, arr)
        else:
            insert_null(cursor, id)

        conn.commit()
        cursor.close()


def get_from_id(startup_id: str) -> str:
    url: str = f'https://angel.co/startups/{startup_id}'
    headers: Dict[str, str] = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '__cfduid=d3dc49bc18740a2b0facc0657340947dc1553140011; _angellist=b5825fc5399971693c4f4c72cf389cde; __cf_bm=51bfcb61da5c15821ad592b81c40b6bbf211a0ef-1553140012-1800-AUXXK8THCpdD/r9r9ghDhDK9p8yhqpTXdxY27mqDQY3W5EtAFXMuYWE44Rzfs4oXi/15JU6825T5PI6fWewiMmc=; _ga=GA1.2.28918781.1553140014; _gid=GA1.2.308356328.1553140014; _gat=1; ajs_user_id=null; ajs_group_id=null; ajs_anonymous_id=%22b5825fc5399971693c4f4c72cf389cde%22; _fbp=fb.1.1553140014995.307173727; amplitude_idundefinedangel.co=eyJvcHRPdXQiOmZhbHNlLCJzZXNzaW9uSWQiOm51bGwsImxhc3RFdmVudFRpbWUiOm51bGwsImV2ZW50SWQiOjAsImlkZW50aWZ5SWQiOjAsInNlcXVlbmNlTnVtYmVyIjowfQ==; amplitude_id_add5896bb4e577b77205df2195a968f6angel.co=eyJkZXZpY2VJZCI6ImY4ODhkYzZhLWMwNmItNGE5OC05NGJiLTYxYjdmYmQ2MDk1NlIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTU1MzE0MDAxNTQ5MSwibGFzdEV2ZW50VGltZSI6MTU1MzE0MDAxNTQ5MSwiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6MCwic2VxdWVuY2VOdW1iZXIiOjB9',
        'dnt': '1',
        'referer': 'https://angel.co/realscout',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'x-csrf-token': '0VTeHIWpUOOsq6/acpdy6NlFeoh9WIL9isBrHpHF+EavUvkiIQSIBUA920dXB/U61QGDBdcGRLDA9UgSTf4YXg==',
        'x-requested-with': 'XMLHttpRequest'
    }

    params: Dict[str, str] = {
        'src': 'startup_profile_lib',
        'associations[]': 'product_screenshots',
        'new_startup_profile': 1
    }

    r: requests.Response = requests.get(url, headers=headers, params=params, timeout=5)

    if r.status_code == 200:
        return r.text
    else:
        return ""


def payload(i: int) -> None:
    startup_id: str = str(i)
    text: str = get_from_id(startup_id)

    seen.put((i, text, len(text) != 0))


def query_incumbent() -> Set[str]:
    cursor: psycopg2 = conn.cursor()
    cursor.execute('SELECT DISTINCT id FROM personal.startups.angel_list')
    records = cursor.fetchall()

    ignore: Set[str] = set()
    for i in records:
        ignore.add(i[0])

    cursor.close()
    return ignore


def main():
    threading.Thread(target=print_daemon, daemon=True).start()
    nums_set: Set[str] = set(str(x) for x in range(1, 1000000))
    nums_incumbent: Set[str] = query_incumbent()
    print(len(nums_incumbent), 'retrieved from table')

    nums: List[str] = list(nums_set.difference(nums_incumbent))

    random.shuffle(nums)
    pool.map(payload, nums)


if __name__ == '__main__':
    main()
