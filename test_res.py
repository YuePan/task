from tornado import gen
import tornado.ioloop
import tornado.web
import task_engine

import tornadoredis

class MainHandler(tornado.web.RequestHandler):
    
    @gen.coroutine 
    def get(self):
        desc = yield task_engine.get_desc('task:back_home')
        self.write(desc)


class SideHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        POOL = tornadoredis.ConnectionPool(host='C7N6YX1')
        c = tornadoredis.Client(connection_pool=POOL)
        foo = yield gen.Task(c.get, 'foo')
        yield gen.Task(c.disconnect)
        print('foo=', foo)
        self.write(foo)
        

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/side", SideHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
