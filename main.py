import create.config
create.config.upload_keys()

import app
from cheroot.wsgi import Server, PathInfoDispatcher

d = PathInfoDispatcher({'/': app.app})
server = Server(('0.0.0.0', 5000), d)


if __name__ == '__main__':
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
