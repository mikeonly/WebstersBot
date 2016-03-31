# -*- coding: utf-8 -*-
import StringIO
import json
import logging
import random
import urllib
import urllib2


# for sending images
from PIL import Image
import multipart

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

import splitter
import sender
import dictionary

TOKEN = open('private/token','rb').read().strip()
URL = 'https://api.telegram.org/bot'

# Maximum length of text message in Telegram
MAX = 4000

d = dictionary.Dic('web1913')
feedqueue = []


class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(URL + TOKEN + '/' + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(URL + TOKEN + '/' + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(URL + TOKEN + '/' + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('Request body: \n\n %s' % body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        def reply(text=None):
            if text:
                resp = ''
                for part in splitter.split(text, MAX):
                    resp += part
                    check = sender.send(
                                'POST',
                                URL + TOKEN + '/' + 'sendMessage',
                                {
                                'text': part.encode('utf-8'),
                                'chat_id': chat_id
                                }
                                )
                    if check:
                        logging.error(check.read())
                    else:
                        logging.info('Sent response: \n\n%s' % resp)
            else:
                sender.send(
                            'POST',
                            URL + TOKEN + '/' + 'sendMessage',
                            {
                            'text': 'Bot tries to send you an empty message.',
                            'chat_id': chat_id
                            }
                            )

        def feedback():
            check = sender.send(
                'POST',
                URL + TOKEN + '/' + 'forwardMessage',
                {
                'chat_id': 926288,
                'from_chat_id': chat_id,
                'message_id': message_id
                }
                )
            if check:
                logging.error(check.read())
            else:
                logging.info('Forwarded as a feedback:\n\n%s' % text)

        if text.startswith('/'):  # Commands start with /
            if text == '/start':
                reply('Bot is serving.')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot ceased serving.')
                setEnabled(chat_id, False)
            elif text == '/info':
                reply(u'@WebstersBot defines English words for you.\n\nDefinitions are taken from Webster’s Revised Unabridged Dictionary (1913).\n\nTry to look up an ordinary word to unravel finer, vivid and sometimes rare (or obsolete) definitions.')
            elif text == '/help':
                reply(u'Try sending an English word to get it’s weakly formated definition.')
            elif text.startswith('/feedback ') or text.startswith('/feedback'):
                if text == '/feedback':
                    global feedqueue
                    reply(u'Write your message below.')
                    feedqueue += [chat_id]
                else:
                    feedback()
                    reply(u'Thank you. Your message has been sent.')
            else:
                reply('Not a command yet.')
        elif chat_id in feedqueue:
            reply(u'Thank you for your feedback. Your message has been sent.')
            feedback()
            feedqueue.remove(chat_id)
        else:
            if getEnabled(chat_id):
                try:
                    response = d[text.capitalize()]
                    if response:
                        reply(response)
                    else:
                        reply(u'Definition of “%s” cannot be found.' % text)
                except Exception, e:
                    reply('Error.')
                    logging.error('Error: %s' % e)
            else:
                logging.info('Not enabled for chat_id %s' % chat_id)


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)