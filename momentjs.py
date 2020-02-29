from jinja2 import Markup
import datetime
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-dates-and-times-legacy
#use eg:{{ momentjs(history.date).format('LL') }}
class momentjs(object):
    def __init__(self, timestamp=datetime.datetime.now()):
        if isinstance(timestamp, str): #string(YYYY-MM-DD) eg. cookie entrie
            self.timestamp = datetime.date(*[int(s) for s in timestamp.split('-')])
        else:
            self.timestamp = timestamp

    def render(self, format):
        return Markup("<script>\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")
