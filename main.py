import create.config
create.config.upload_keys()

import app
from cheroot.wsgi import Server, PathInfoDispatcher
from app.ApiHandlers.Admin import update_all
d = PathInfoDispatcher({'/': app.app})
server = Server(('0.0.0.0', 5000), d, numthreads=1000)


if __name__ == '__main__':
    try:

        update_all.restart()
        server.start()

    except KeyboardInterrupt:
        server.stop()
