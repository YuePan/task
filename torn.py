import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.escape
import task_engine
import intent_detector


BING_Request = "https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web?"\
        "Query=%%27%s%%27&Market=%%27en-US%%27&$top=10&$format=json"

BING_Key = "Lk/BUx4rCRwLfX/Ti0ArjKvgwn3AS7+mXmUfCyjpNcM"




class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie("user")




class MainHandler(BaseHandler):

    def get(self, path):
        print("path=%s" % path)
        self.redirect("/search?query=")




class LoginHandler(BaseHandler):

    def get(self):
        name = self.get_argument("name")
        print("LoginHandler, name=%s" % name)
        self.set_secure_cookie("user", name)
        self.write({"name":name})




class DataHandler(BaseHandler):

    def get(self, path):
        query = self.get_argument("query")
        print("DataHandler, query=%s" % query)

        task = ""
        terms = query.split()
        for term in terms:
            t = term.lower()
            if t.startswith("ta:"):
                task = t[3:]
                break
        if task:
            ret_data = {"task": task}
        else:
            re = self.request
            ret_data = {"redirect": re.protocol + "://" +
                    re.host + "/search?query=" + query}
        self.write(ret_data)




class TaskHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self, task):
        task = self.get_argument("task")
        micro = self.get_argument("micro")
        microidx = int(micro) if micro else 0
        method = self.get_argument("method")
        methodidx = int(method) if method else 0
        query = self.get_argument("query")
        print("TaskHandler, task micro method=", task, microidx, methodidx)
        if not task:
            task = intent_detector.get_task(query, [])
        task_desc = yield task_engine.get_desc(task, microidx, methodidx)
        if not task_desc:
            self.send_error(400, reason="task not supported yet")
        else:
            self.set_secure_cookie(str(microidx), method)
            self.render('task.html', 
                task=task_desc["task"],
                micros=task_desc["micros"],
                methods=task_desc["methods"],
                ops=task_desc["ops"],
                active_micro=microidx,
                active_method=methodidx)




class SearchHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self, params):
        query = self.get_argument("query")
        print("SearchHandler, query=%s" % query)
        if query:
            http = tornado.httpclient.AsyncHTTPClient()
            request = tornado.httpclient.HTTPRequest(
                BING_Request % tornado.escape.url_escape(query),
                auth_username=BING_Key,
                auth_password=BING_Key)
            response = yield http.fetch(request)
            print("Request: " + BING_Request % query)
            if response.error:
                raise tornado.web.HTTPError(500)
            json = tornado.escape.json_decode(response.body)
            items = json['d']['results']
            print("Fetched " + str(len(items)) + " results from Bing Web Search")
            #task = intent_detector.get_task(query, items)
            #task_desc = yield task_engine.get_desc(task)
            self.render("serp.html",
                        user=self.current_user,
                        #task=task_desc["task"],
                        #micros=task_desc["micros"],
                        #methods=task_desc["methods"],
                        #ops=task_desc["ops"],
                        #iactive_micro=micro,
                        #active_method=method,
                        items=items)
        else:
            self.render("serp.html",
                        user=self.current_user, items=[])
                        #task=None, micros=[], methods=[], ops={})
                        #active_micro=-1, active_method=None)





application = tornado.web.Application([
    (r"/login", LoginHandler),
    (r"/search?(.+)", SearchHandler),
    (r"/task(.*)", TaskHandler),
    (r"/data/(.*)", DataHandler),
    (r"(.*)", MainHandler),
], cookie_secret="secret cookie")




if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
