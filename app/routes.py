import codecs
import datetime
import os
from flask_restful import reqparse
from app.ApiHandlers import JWTVerification
from app import app, api
from flask import send_from_directory, redirect
from app.ApiHandlers import HelloHandler, Login, RefreshToken, Grades, Logs, Marks, Students, Subjects, Admin, Teachers, \
    Report, ExcelExport


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/main')
def main():
    return serve_index()


@app.route('/admin')
def admin():
    return serve_index()


@app.route('/excel_export/<grade_name>')
def export_excel(grade_name):
    return serve_index()


@app.route('/export/<type>/<id>/<date_from>/<date_to>')
def export(type, id, date_from, date_to):
    print(type, id, date_from, date_to)
    return serve_index()


@app.route('/download_report/<key>')
def download_report(key):
    print("download_report")

    # Проверяем валидность ключа
    filename = Report.check_key(key)
    # Если валиден, то возвращаем файл пользователю
    if filename:
        abspath = os.path.abspath(".\\reports")
        response = send_from_directory(abspath, str(filename), as_attachment=True)
        # задаем куки с данными об этом файле, чтобы пользователь знал, когда ему придет файл
        response.set_cookie("downloaded_report", key)

        return response
    else:
        # иначе перенаправляем пользователя на основную страницу
        return redirect('/main')


@app.route('/download_logs/<date_from>/<date_to>/<key>')
def download_logs(date_from, date_to, key):
    # декодируем ключ доступа к файлу логов
    key = codecs.decode(key, "hex").decode('utf-8')
    # проверяем, хорош ли ключ
    status = JWTVerification.check_access_token(key)
    if not status[0]:
        return redirect('/admin')

    # пробуем распарсить данные из запроса
    try:
        date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d")
    except Exception:
        return redirect('/admin')

    if date_from > date_to:
        return redirect('/admin')

    # собираем файл
    path = os.path.join(os.path.join('logs', 'tmp'), 'prepared.log')
    result_file = open(path, 'w')


    # идем по всем датам от начала до конца и вписываем все логи
    current_date = date_from
    while current_date <= date_to:
        filename = os.path.join('logs', current_date.strftime("%Y-%m-%d") + ".log")
        if os.path.exists(filename):
            source = open(filename, 'r')
            data = source.readlines()
            result_file.write(current_date.strftime("%Y-%m-%d") + '\n')
            result_file.write(''.join(data))
        current_date += datetime.timedelta(days=1)

    # сохраняем и отправляем файл
    result_file.close()
    abspath = os.path.abspath(os.path.join('.\\logs', 'tmp'))
    return send_from_directory(abspath, 'prepared.log', as_attachment=True)


# добавляем ресурсы API-шников
api.add_resource(HelloHandler.HelloHandler, '/api/hello')
api.add_resource(Login.Login, '/api/login')
api.add_resource(RefreshToken.RefreshToken, '/api/refresh_token')
api.add_resource(Grades.GradesApi, '/api/grades')
api.add_resource(Marks.MarksApi, '/api/marks')
api.add_resource(Students.StudentsApi, '/api/students')
api.add_resource(Subjects.SubjectsApi, '/api/subjects')
api.add_resource(Logs.LogsApi, '/api/logs')
api.add_resource(Admin.GetUpdateTimeApi, '/api/update_time')
api.add_resource(Admin.ResetUpdateTimeApi, '/api/reset_update_time')
api.add_resource(Admin.ReadLogsApi, '/api/read_logs')
api.add_resource(Admin.SetTeacherRightsApi, '/api/reset_rights')
api.add_resource(Admin.GetTeachersApi, '/api/get_teachers')
api.add_resource(Teachers.TeachersApi, '/api/teacher')
api.add_resource(Login.Logout, '/api/logout')
api.add_resource(Report.ReportApi, '/api/report')
api.add_resource(Students.GetStudentApi, '/api/get_student')
api.add_resource(ExcelExport.ExcelExport, '/api/excel_export')
