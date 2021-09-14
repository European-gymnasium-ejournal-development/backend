import create.config
create.config.upload_keys()

import app
from cheroot.wsgi import Server, PathInfoDispatcher

d = PathInfoDispatcher({'/': app.app})
server = Server(('127.0.0.1', 5000), d, numthreads=1000)


if __name__ == '__main__':
    try:
        from app.ApiHandlers.Admin import update_all
        update_all.restart()
        server.start()

    except KeyboardInterrupt:
        server.stop()
