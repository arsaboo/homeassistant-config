
import time
import threading

class ArloBackgroundWorker(threading.Thread):

    def __init__( self ):
        super().__init__()
        self._id    = 0
        self._lock  = threading.Condition()
        self._queue = {}

    def _next_id( self ):
        self._id += 1
        return str(self._id) + ':' + str(time.monotonic()) 

    def _run_next( self ):

        # timout in the future
        timeout = int(time.monotonic() + 60)

        # go by priority...
        for prio in sorted( self._queue.keys() ):

            # jobs in particular priority
            for run_at,job_id in sorted( self._queue[prio].keys() ):
                if run_at <= int(time.monotonic()):
                    job = self._queue[prio].pop( (run_at,job_id) )
                    self._lock.release()

                    # run it
                    #print( 'run:' + str(int(time.monotonic())) + ' run_at=' + str(run_at) )
                    job['callback']( **job['args'] )

                    # reschedule?
                    self._lock.acquire()
                    run_every = job.get('run_every',None)
                    if run_every:
                        run_at += run_every
                        self._queue[prio][ (run_at,job_id) ] = job

                    # start going through list again
                    return None
                else:
                    if run_at < timeout:
                        timeout = run_at

        return timeout

    def run( self ):

        with self._lock:
            while True:

                # loop till done
                timeout = None
                while timeout is None:
                    timeout = self._run_next()

                # wait or get going?
                now = time.monotonic()
                if ( now < timeout ):
                    self._lock.wait( timeout - now )

    def queue_job( self,run_at,prio,job ):
        run_at = int(run_at)
        with self._lock:
            job_id = self._next_id()
            if prio not in self._queue:
                self._queue[prio] = {}
            self._queue[prio][ (run_at,job_id) ] = job
            self._lock.notify()
        return job_id

    def stop_job( self,to_delete ):
        with self._lock:
            for prio in self._queue.keys():
                for run_at,job_id in self._queue[prio].keys():
                    if job_id == to_delete:
                        #print( 'cancelling ' + str(job_id) )
                        del self._queue[prio][ (run_at,job_id) ]
                        return True
        return False


class ArloBackground(threading.Thread):
 
    def __init__( self,arlo ):
        self._worker = ArloBackgroundWorker()
        self._worker.name = 'ArloBackgroundWorker'
        self._worker.daemon = True
        self._worker.start()
        arlo.debug( 'starting' )

    def _run( self,bg_cb,prio,**kwargs):
        job = { 'callback':bg_cb, 'args':kwargs }
        return self._worker.queue_job( time.monotonic(),prio,job )

    def run_high( self,bg_cb,**kwargs):
        return self._run( bg_cb,10,**kwargs)
    def run( self,bg_cb,**kwargs):
        return self._run( bg_cb,40,**kwargs)
    def run_low( self,bg_cb,**kwargs):
        return self._run( bg_cb,99,**kwargs)

    def _run_in( self,bg_cb,prio,seconds,**kwargs):
        job = { 'callback':bg_cb, 'args':kwargs }
        return self._worker.queue_job( time.monotonic() + seconds,prio,job )

    def run_high_in( self,bg_cb,seconds,**kwargs):
        return self._run_in( bg_cb,10,seconds,**kwargs)
    def run_in( self,bg_cb,seconds,**kwargs):
        return self._run_in( bg_cb,40,seconds,**kwargs)
    def run_low_in( self,bg_cb,seconds,**kwargs):
        return self._run_in( bg_cb,99,seconds,**kwargs)

    def _run_every( self,bg_cb,prio,seconds,**kwargs):
        job = { 'run_every':seconds, 'callback':bg_cb, 'args':kwargs }
        return self._worker.queue_job( time.monotonic() + seconds,prio,job )

    def run_high_every( self,bg_cb,seconds,**kwargs):
        return self._run_every( bg_cb,10,seconds,**kwargs)
    def run_every( self,bg_cb,seconds,**kwargs):
        return self._run_every( bg_cb,40,seconds,**kwargs)
    def run_low_every( self,bg_cb,seconds,**kwargs):
        return self._run_every( bg_cb,99,seconds,**kwargs)

    def cancel( self,to_delete ):
        if to_delete is not None:
            self._worker.stop_job( to_delete )

