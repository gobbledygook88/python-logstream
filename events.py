class ServerSentEvent(object):
    def __init__(self, data, event=None, id=None):
        self.data = data
        self.event = event
        self.id = id
        self.desc_map = {
            self.data: 'data',
            self.event: 'event',
            self.id: 'id'
        }

    def encode(self):
        if not self.data:
            return '' 

        lines = ['{}: {}'.format(v, k) 
                 for k, v in self.desc_map.iteritems() if k]

        return '{}\n\n'.format('\n'.join(lines))
