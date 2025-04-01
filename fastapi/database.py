from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
import asyncpg
from models import UserDB, UrlDB, StatsDB
from datetime import datetime

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def fetch_data(fetch_q):
    # Подключение к базе данных
    conn = await asyncpg.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
        )
    
    try:
        # Выполнение запроса
        result = await conn.fetch(fetch_q)
        return result
        
    finally:
        # Закрытие соединения
        await conn.close()

async def execute_data(exe_q):
    # Подключение к базе данных
    conn = await asyncpg.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
        )
    
    try:
        # Выполнение запроса
        result = await conn.execute(exe_q)
        print(result)
        return result
        
    finally:
        # Закрытие соединения
        await conn.close()

async def get_all_users():
    sel = 'SELECT * FROM users'
    res = await fetch_data(sel)
    users = [UserDB(**dict(row)) for row in res]
    return users

async def get_all_urls():
    sel = 'SELECT * FROM urls'
    res = await fetch_data(sel)
    urls = [UrlDB(**dict(row)) for row in res]
    return urls

async def find_users(log, password):
    sel = f"SELECT * FROM users WHERE login = '{log}' and password = '{password}'"
    res = await fetch_data(sel)
    users = [UserDB(**dict(row)) for row in res]
    return users

async def find_url(url):
    sel = f"SELECT * FROM urls WHERE save_url = '{url}'"
    res = await fetch_data(sel)
    urls = [UrlDB(**dict(row)) for row in res]
    return urls

async def find_short_url(url):
    sel = f"SELECT * FROM urls WHERE short_url = '{url}'"
    res = await fetch_data(sel)
    urls = [UrlDB(**dict(row)) for row in res]
    return urls

async def find_stats(id):
    sel = f"SELECT * FROM stats WHERE id = {id}"
    res = await fetch_data(sel)
    stats = [StatsDB(**dict(row)) for row in res]
    print(stats)
    return stats

async def insert_users(user: UserDB):
    query = f"INSERT INTO users(login, password) VALUES ('{user.login}', '{user.password}')"
    await execute_data(query)

async def insert_stats(s: StatsDB):
    query = f"INSERT INTO stats(id, date_created, use_count) VALUES ({s.id}, '{s.date_created}', {s.use_count})"
    await execute_data(query)

async def insert_urls(u: UrlDB):
    query = f"INSERT INTO urls(id, save_url, short_url, created_by_login) VALUES ({u.id}, '{u.save_url}', '{u.short_url}', '{u.created_by_login}')"
    await execute_data(query)

async def update_stats(s: StatsDB):
    query = f"UPDATE stats SET use_count = {s.use_count}, date_last = '{s.date_last}' WHERE id = {s.id}"
    await execute_data(query)

async def update_urls_short(u: UrlDB):
    query = f"UPDATE urls SET short_url = '{u.short_url}' WHERE save_url = '{u.save_url}'"
    await execute_data(query)

async def update_urls_exp_time(u: UrlDB):
    query = f"UPDATE urls SET exp_time = '{u.exp_time}' WHERE save_url = '{u.save_url}'"
    await execute_data(query)

async def delete_stats(s: int):
    query = f"DELETE FROM stats WHERE id = {s}"
    await execute_data(query)

async def delete_urls(u: UrlDB):
    query = f"DELETE FROM urls WHERE save_url = '{u.save_url}'"
    await execute_data(query)

async def delete_urls_id(u: int):
    query = f"DELETE FROM urls WHERE id = {u}"
    await execute_data(query)

async def get_url_for_delete(time_del: datetime):
    sel = f"SELECT * FROM urls WHERE exp_time < '{time_del}'"
    res = await fetch_data(sel)
    urls = [UrlDB(**dict(row)) for row in res]
    return urls

async def get_stats_for_delete(now: datetime, N: int):
    sel = f"SELECT id FROM (SELECT id, EXTRACT (DAY FROM('{now}' - date_last)) as diff FROM stats) AS r WHERE diff > {N}"
    res = await fetch_data(sel)
    ids = [dict(row) for row in res]
    return ids