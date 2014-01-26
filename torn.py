import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.escape




BING_Request = "https://api.datamarket.azure.com/Bing/Search/Web?"\
        "Query=%%27%s%%27&$top=10&$format=json"

BING_Key = "Lk/BUx4rCRwLfX/Ti0ArjKvgwn3AS7+mXmUfCyjpNcM"




class MainHandler(tornado.web.RequestHandler):


    def get(self, path):
        print("path=%s" % path)
        self.redirect("/search?query=")




class DataHandler(tornado.web.RequestHandler):

    def get(self, path):
        value = self.get_argument("value")
        print("DataHandler, value=%s" % value)

        isTask = False
        if value.find("ts:") == 0:
            isTask = True

        if (isTask):
            ret_data = {"value": value}
        else:
            re = self.request
            ret_data = {"redirect": re.protocol + "://" + 
                    re.host + "/search?query=" + value}
        self.write(ret_data)




class TaskHandler(tornado.web.RequestHandler):

    def get(self, task):
        pass




class SearchHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self, params):
        query = self.get_argument("query")
        print("SearchHandler, query=%s" % query)
        if not (query is None) and query != "":
            http = tornado.httpclient.AsyncHTTPClient()
            request = tornado.httpclient.HTTPRequest(
                BING_Request % tornado.escape.url_escape(query),
                auth_username=BING_Key,
                auth_password=BING_Key)
            http.fetch(request, callback=self.on_response)
            print("Request: " + BING_Request % query)
        else:
            self.render("serp.html", steps=[], items=[])


    def on_response(self, response):
        if response.error: raise tornado.web.HTTPError(500)
        json = tornado.escape.json_decode(response.body)
        items = json['d']['results']
        print("Fetched " + str(len(items)) + " results from Bing Web Search")
        steps = [{"Id":"11", "Title":"Step 1", "Content":"bala, bala1"},
                 {"Id":"12", "Title":"Step 2", "Content":"bala, bala2"},
                 {"Id":"13", "Title":"Step 3", "Content":"bala, bala3"}]
        self.render("serp.html", steps=steps, items=items)
        #self.finish()
        



application = tornado.web.Application([
    (r"/search?(.+)", SearchHandler),
    (r"/data/(.*)", DataHandler),
    (r"/(.+)", MainHandler),
])




if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
