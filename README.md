# fast_api_hw
Данный сервис - Выполненное 3-е домашнее задание по предмету "Прикладной Python".

В ходе данной работы был разработан сервис для сокращения длинных ссылок. Для хранения данных используется `PostgreSQL`

## Реализованные методы:
 - Авторизация (регистрация, получение текущего пользователя):
  ![auth](https://github.com/user-attachments/assets/abae954c-1493-41c1-8c3e-e2edcebf61a5)
 - Создание короткой ссылки (`POST /links/shorten`) (с возможностью задать время жизни и короткую ссылку):
   ![add_link](https://github.com/user-attachments/assets/74cf8c52-3e95-4301-a712-a6dd9812b377)
 - Открыть оригинальную ссылку по короткой (`GET /links/{short_code}`):
  ![op](https://github.com/user-attachments/assets/8d89dae0-d407-4276-80ce-d22d9d484e84)
 - Удалить короткую ссылку (`DELETE /links/{short_code}`):
  ![del](https://github.com/user-attachments/assets/42ba507c-8c80-4c52-9476-032d0ff72d9d)
 - Обновить короткую ссылку (`PUT /links/{short_code}`):
   ![upd](https://github.com/user-attachments/assets/9d11fd38-4961-4e16-bb8b-281682e22005)
 - Получить статистику по короткой ссылке (`GET /links/{short_code}/stats`):
   ![st](https://github.com/user-attachments/assets/b09498b4-68db-475e-bb4a-5de047f20cc9)
 - Поиск короткой ссылки по оригинальной (`GET /links/search?original_url={url}`):
   ![find](https://github.com/user-attachments/assets/73184359-b78b-438d-9f90-0d625f300afb)
- Автоматическое удаление неиспользуемых ссылок:
   ![auto_del](https://github.com/user-attachments/assets/dffd08c6-0701-4412-852b-aeeb4b4551a0)

## Используемые таблицы в `PostgreSQL`:
users:
| Колонка | Пераметры | Описание |
| --------|-----------|----------|
| login | Not NULL text PRIMARY KEY| Логин пользователя |
| password | Not NULL text | Пароль |

links:
| Колонка | Пераметры | Описание |
| --------|-----------|----------|
| id | int NOT NULL PRIMARY KEY| Идентификатор |
| save_url | text NOT NULL | Длинная сслыка для сохранения |
| short_url | text NOT NULL | Короткая ссылка |
| created_by_login | BOOLEAN NOT NULL | Создал ли ссылку авторизованный пользователь или нет |
| exp_time | timestamp without timezone | Дата/Время жизни ссылки |

stats:
| Колонка | Пераметры | Описание |
| --------|-----------|----------|
| id | int NOT NULL PRIMARY KEY| Идентификатор ссылки (таблица links) |
| date_created | timestamp without timezone NOT NULL | Дата/Время создания ссылки |
| use_count | int NOT NULL| Кол-во использования |
| date_last | timestamp without timezone | Дата/Время последнего использования ссылки |

## Docker:
Была реализована контейнеризация сервиса с помощью Docker. Созданы образы контенеров для БД `PostgreSQL` и сервиса FAST api
![image](https://github.com/user-attachments/assets/533e35ed-3daf-405a-8858-270745b717f6)

Контейнеры запущены со следующими параметрами: 

![image](https://github.com/user-attachments/assets/6ee08741-2228-4957-8124-b21835378009)
![image](https://github.com/user-attachments/assets/89172f9f-1776-40ed-8ccf-b0f22f790892)

Сеть в контейнере Fast API работает в режиме хоста, а сеть контейнера `PostgreSQL` в режиме моста. Для контенера с базой данных сделан проброс порта на хостовую машину.

![image](https://github.com/user-attachments/assets/9c773f67-a740-406a-83ea-489bee94760d)

Логи запущенных контейнеров:

![image](https://github.com/user-attachments/assets/990b409c-3cbf-4a58-aabc-0d3b397c6a35)
![image](https://github.com/user-attachments/assets/74af81f8-6014-4d41-b92f-4996fdae805d)



