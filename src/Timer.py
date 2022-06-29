from datetime import datetime, timedelta

TIME_OFFSET = 4 # 5 during the winter, 4 during the summer
class Timer:
    def __init__(self, total, every=10, first_event=False):
        self.event_times, self.event_counts = [], []
        if first_event: self.event(0)
        self.total, self.every = total, every
        
    def event(self, count):
        self.event_times.append(datetime.utcnow()-timedelta(hours=TIME_OFFSET))
        self.event_counts.append(count)
        
    def get_eta(self, count, minus_one=True, return_str=False):
        self.event(count)
        if len(self.event_times) == 1: s='ETA: ???, Now: ' + self._time_to_str(); return s if return_str else print(s, flush=True); return
        if count % self.every != 0: return
        
        def rate(i): return (self.event_counts[i+1]-self.event_counts[i])/(self.event_times[i+1]-self.event_times[i]).total_seconds()
        avg_rate = sum([rate(i) for i in range(len(self.event_times)-1)]) / (len(self.event_times)-1)
        
        
        seconds_remaining = (self.total-count)/avg_rate
        eta = self.event_times[-1]+timedelta(seconds=seconds_remaining)
        s = 'Doing number ' + str(count) + ' / ' + str(self.total) + '  |  '
        s += 'ETA: %s, Now: %s' %(self._time_to_str(eta), self._time_to_str())
        s += self._format_time_remaining(seconds_remaining)
        return s if return_str else print(s, flush=True)
    
    def _time_to_str(self, t=None):
        if t is None: t = datetime.utcnow()-timedelta(hours=TIME_OFFSET)
        return str(t.hour - (12 if t.hour > 12 else 0)) + ':' + str(t.minute).zfill(2) + ':' + str(t.second).zfill(2) + ' ' + ('AM' if t.hour < 12 else 'PM')
    
    def _format_time_remaining(self, seconds=None):
        if seconds is None: return '' # happens if first event
        
        opt1 = """
        if seconds < 24*3600:
            return ' (%s:%s:%s remaining)' %(str(seconds//3600).zfill(2), str((seconds%3600)//60).zfill(2), str(seconds%60).zfill(2))
        else:
            return ' (%id, %s:%s:%s remaining)' %(seconds//(24*3600), str((seconds%(24*3600))//3600).zfill(2),
                                                  str((seconds%3600)//60).zfill(2), str(seconds%60).zfill(2))
        """
        
        if seconds < 60:
            return ' (%is remaining)' % seconds
        elif seconds < 3600:
            return ' (%i:%s remaining)' %(seconds//60, str(int(seconds%60)).zfill(2))
        elif seconds < 24*3600:
            return ' (%i:%s:%s remaining)' %(seconds//3600, str(int((seconds%3600)//60)).zfill(2), str(int(seconds%60)).zfill(2))
        else:
            return ' (%id, %s:%s:%s remaining)' %(seconds//(24*3600), str(int((seconds%(24*3600))//3600)).zfill(2),
                                                  str(int((seconds%3600)//60)).zfill(2), str(int(seconds%60)).zfill(2))