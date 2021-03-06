# backend
Server side of site

Для установки необходимых библиотек выполните команду 

`pip install -r requirements.txt`

Здесь располагается сервер сайта для отображения оценок и составления отчетов.
Для начала работы необходимо запустить start.bat или main.py

## Общее устройство:
Загрузка контента на сайте происходит динамически. 
То есть страница изначально пустая, а потом по шаблонам 
с помощью React собирается и заполняется данными.

Все получение данных происходит не при получении страницы и ее html, css, js кода,
а отдельно уже в js через API сайта. Это сделано для безопасности.

В API используется JWT для проверки наличия доступа у клиента к данным.

На сервере используется Flask, FlaskSQLAlchemy, MySQL и FlaskRestFUL

Скачивание файлов устроено немного странным методом:

По запросу на скачивание пользователь получает ключ для скачивания,
а сервер создает файл. В ключе зашифровано имя файла и особый хеш.
После этого пользователь переходит на страницу /download_report/<key> и 
там получает файл.

### База данных
Таблицы:
   1. students (id: int, name: string, grade_name: string)
   2. subjects (id: int, name: string)
   3. teachers (id: int, name: string, email: string, access_level: string)
   4. tasks (id: int, type: int (summative: 1, formative: 0), 
   subject_id: int, description: string, timestamp: datetime)
   5. marks (id: int, student_id: int, task_id: int, criteria: int, 
   mark: string, max_mark: string, comment: string)
   6. subject_to_student 
   (пары вида предмет-ученик, означает что ученик посещает предмет)
   (id: int, subject_id: int, student_id: int)
   7. subjects_to_teachers 
   (пары вида предмет-учитель, означает что учитель преподает предмет)
   (id: int, subject_id: int, teacher_id: int)
   8. jsrefreshtokens (таблица с JW refresh-токенами - не больше одного на одного учителя) 
   (teacher_email: string, token: string)

## Файлы
1. `main.py` - запуск сервера
2. `settings.env` - параметры запуска (google client id, например)
3. `start.bat` - файл, готовый для запуска сервера
4. `resources/` - файлы, необходимые для работы программы: 
иконки и шрифты для создания отчета
5. `ManageBackApi/` - файлы для обновления БД. 
Получают данные из Managebac и сохраняют в БД
    1. `DB_students.py` - синхронизация студентов
    2. `DB_teachers.py` - синхронизация преподавателей
    3. `DB_subjects_STS.py` - синхронизация всего остального 
    (оценок, предметов, заданий и их связей)
    4. `update_all.py` - запуск и регулярное обновление БД
    (было бы здорово переписать на schedule, но пока все ручками сделано)
6. `reports/` - все отчеты сохраняются сюда (и пока не очищаются)
7. `logs/` - все логи сохраняются сюда и не очищаются. 
В папке `logs/tmp/` лежит последний сгенерированный файл 
с объединенными логами (для скачивания админом)
8. `create/config.py` - конфиг и основные параметры проекта. В основном константы
9. `app/routes.py` - настройки роутинга (стандартное для flask)
10. `app/Database/` - все файлы базы данных
    1. `Inspection.py` - выводит всё из БД. Используется для дебага
    2. Остальные файлы реализуют работу с одноименными таблицами. 
    И предоставляют функции для удобной работы
11. `app/ApiHandlers/` - функции API. Основная логика приложения
    1. `Admin.py` - весь функционал админа
    2. `ExcelExport.py` - два вида создания excel-файлов: по ученику и по классу
    3. `Grades.py` - получение списка классов
    4. `JWTVerification.py` - проверка JW-токена на корректность
    5. `LastUpdate.py` - когда было последнее обновление БД
    6. `Login.py` - вход по google-токену
    7. `Logs.py` - сохранение логов
    8. `Marks.py` - получение списка оценок
    9. `RefreshToken.py` - обновление access-токена
    10. `Report.py` - генерация pdf-отчета
    11. `Students.py` - получение учеников по классу
    12. `Subjects.py` - получение предметов по ученику
    13. `Teachers.py` - получение данных о том, кто вошел на сайт (о себе)
    14. `verification.py` - вход по google-аккаунту
