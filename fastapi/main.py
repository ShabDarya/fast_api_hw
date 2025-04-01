import uvicorn
from fastapi import FastAPI
from fastapi import APIRouter
import asyncio
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import Optional
from models import Token, UserDB, UrlDB, StatsDB, shorten_string
from auth_defs import authenticate_user, create_access_token, get_password_hash, get_current_user, credentials_exception
from config import ACCESS_TOKEN_EXPIRE_MINUTES, N
import database
import webbrowser

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import  OAuth2PasswordRequestForm

from typing import Annotated
from datetime import datetime, timedelta

app = FastAPI()

@app.post("/token")
async def login_for_access_token(
    # аннотируем данные формы авторизации
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Функция авторизации пользователя. В случае успеха возвращает токен доступа"""
    users = await database.get_all_users()

    # проходим проверку подлинности
    user = authenticate_user(users, form_data.username, form_data.password)
    print(form_data)
    if not user:
        # не прошли проверку, отдаем HTTP-ошибку
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # устанавливаем время жизни токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # генерируем токен доступа
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model=UserDB)
async def read_users_me(
    current_user: Optional[UserDB] = Depends(get_current_user)
): 
    """Получение своих данных (авторизированного пользователя)"""

    if current_user:
        return current_user
    else:        
        raise credentials_exception 

@app.post("/users/add")
async def users_add(u: UserDB):
    p = get_password_hash(u.password)
    u.password = p
    r = await database.insert_users(u)

links_route = APIRouter()

@links_route.post("/shorten", response_model=UserDB) 
async def create_link(link: str, current_user: Optional[UserDB] = Depends(get_current_user), alias: Optional[str] = None, expires_at: Optional[datetime] = None): #создает короткую ссылку
    #пользователь вводит, проверка на наличие уже такой ссылки. Если есть, то возвращаем старую, если нет, то создаем записи в 2 таблицы
    try:
        if current_user:
            log = True
        else:
            log = False

        urls = await database.find_url(link)

        if(len(urls) > 0):
            data = [{"alias": urls[0].short_url}]
            json_data = jsonable_encoder(data)
            return JSONResponse(content=json_data, status_code=200)
        else:
            if alias is not None:
                check_short = await database.find_short_url(alias)
                if len(check_short) > 0:
                    data = [{"message": 'Have short code in database'}]
                    json_data = jsonable_encoder(data)
                    return JSONResponse(content=json_data, status_code=404)
            else:
                check = False
                while(not check):
                    i = 4
                    alias = shorten_string (link, i)
                    check_short = await database.find_short_url(alias)
                    if len(check_short) > 0:
                        i +=1
                    else: check = True

            if expires_at is None or expires_at > datetime.now():    
                ur = await database.get_all_urls()
                await database.insert_urls(UrlDB(id = len(ur)+1, save_url=link, short_url=alias, exp_time=expires_at, created_by_login=log))
                await database.insert_stats(StatsDB(id = len(ur)+1, date_created=datetime.now(), use_count=0))
                data = [{"url": link, "alias": alias}]
                json_data = jsonable_encoder(data)
                return JSONResponse(content=json_data, status_code=200)

            else:
                data = [{"message": 'URL expire.'}]
                json_data = jsonable_encoder(data)
                return JSONResponse(content=json_data, status_code=404)
    except:
        data = [{"message": "Error"}]
        json_data = jsonable_encoder(data)
        return JSONResponse(content=json_data, status_code=400)

@links_route.get("/search") 
async def find_link_api(original_url: str): # Поиск ссылки по оригиналу
    urls = await database.find_url(original_url)

    if(len(urls) > 0):
        data = [{"alias": urls[0].short_url}]
        json_data = jsonable_encoder(data)
        return JSONResponse(content=json_data, status_code=200)
    else:
        data = [{"message": 'No url in database'}]
        json_data = jsonable_encoder(data)
        return JSONResponse(content=json_data, status_code=404)

@links_route.get("/{short_code}") 
async def open_link(short_code: str): #перенаправляет на оригинальный id
    c = 0
    try:
        urls = await database.find_short_url(short_code)
        url = urls[0]
        stat_url = await database.find_stats(url.id)
    
        await database.update_stats(StatsDB(id = stat_url[0].id, use_count=stat_url[0].use_count + 1 , date_last=datetime.now(), date_created=stat_url[0].date_created))
        c = 1
        webbrowser.open(url.save_url, new=2)

        data = [{"message": 'OK'}]
        json_data = jsonable_encoder(data)
        return JSONResponse(content=json_data, status_code=200)
    except:
        if c == 0:
            data = [{"message": 'No short code  in database'}]
            json_data = jsonable_encoder(data)
            return JSONResponse(content=json_data, status_code=404)
        else:
            data = [{"message": "Can't open url"}]
            json_data = jsonable_encoder(data)
            return JSONResponse(content=json_data, status_code=400)
    
@links_route.delete("/{short_code}") # Удаляет связь
async def remove_link(short_code: str, current_user: Optional[UserDB] = Depends(get_current_user)):
    #удалить в urls и stats, если есть авторизация + проверка на существование таких записей
    if current_user:
        urls = await database.find_short_url(short_code)
        if len(urls) > 0:
            print('rr')
            u = urls[0]
            await database.delete_stats(u.id)
            await database.delete_urls(u)
            
            data = [{"message": 'OK'}]
            json_data = jsonable_encoder(data)
            return JSONResponse(content=json_data, status_code=200)
        else:
            data = [{"message": 'No short code  in database'}]
            json_data = jsonable_encoder(data)
            return JSONResponse(content=json_data, status_code=404)     
    else:
        raise credentials_exception


@links_route.put("/{short_code}") # Обновляет url
async def update_link(new_short: str, link: str, current_user: Optional[UserDB] = Depends(get_current_user)):
    #редактировать urls + в статс +1 пишем с новой датой, проверка на существование
    if current_user:
        urls = await database.find_url(link)
        if len(urls) > 0:
            u = urls[0]
            u.short_url = new_short
            await database.update_urls_short(u)
            stat_url = await database.find_stats(u.id)
            await database.update_stats(StatsDB(id = stat_url[0].id, use_count=stat_url[0].use_count + 1 , date_last=datetime.now(), date_created=stat_url[0].date_created))

            data = [{"message": 'OK'}]
            json_data = jsonable_encoder(data)
            return JSONResponse(content=json_data, status_code=200)
        else:
            data = [{"message": 'No link  in database'}]
            json_data = jsonable_encoder(data)
            return JSONResponse(content=json_data, status_code=404)     
    else:
        raise credentials_exception

@links_route.get("/{short_code}/stats")
async def open_stats(short_code: str): # Статистика по ссылке
    try:
        urls = await database.find_short_url(short_code)
        if len(urls) == 0:
            data = [{"message": 'No short code in database'}]
            json_data = jsonable_encoder(data)
            return JSONResponse(content=json_data, status_code=404)
        url = urls[0]
        stat_url = await database.find_stats(url.id)
        stat = stat_url[0]

        json_data = jsonable_encoder(stat)
        return JSONResponse(content=json_data, status_code=200)
    except Exception as e:
        print
        data = [{"message": e}]
        json_data = jsonable_encoder(data)
        return JSONResponse(content=json_data, status_code=400)

async def check_and_delete_urls():
    while True:
        print('Проверка urls на expired')
        urls = await database.get_url_for_delete(datetime.now())
        if (len(urls) > 0):
            for u in urls:
                await database.delete_stats(u.id)
                await database.delete_urls(u)
        print('Проверка urls на expired закончена')
        await asyncio.sleep(300) #проверяем каждые 5 минут

async def check_and_delete_nonuse_url():
    while True:
        print('Проверка urls на неиспользуемость')
        stat = await database.get_stats_for_delete(datetime.now(), N)
        for s in stat:
            print(s['id'])
            await database.delete_stats(s['id'])
            await database.delete_urls_id(s['id'])
        print('Проверка urls на неиспользуемость закончена')
        await asyncio.sleep(86400) #засыпаем на сутки


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(check_and_delete_urls())
    asyncio.create_task(check_and_delete_nonuse_url())



## Реализуйте роутер с префиксом /api/v1/models
app.include_router(links_route, prefix="/links")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


