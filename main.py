from app import app
from ManageBackApi import update_all

if __name__ == '__main__':
    print(str('М'.encode('utf-8').hex()))

    update_all.restart()
    app.run(port=5000)


