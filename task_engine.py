from tornado import gen
import tornadoredis

CONNECTION_POOL = tornadoredis.ConnectionPool(host='C7N6YX1') 


""" Return the description of a task.

The structure include the task, the micro-tasks, the available methods for 
given micro-task, and operators for the given micro-task and method. If method
is not given, use the default method for the micro-task.

"""
@gen.coroutine
def get_desc(task, micro=None, method=None): 
    c = tornadoredis.Client(connection_pool=CONNECTION_POOL)

    print("task=", task)
    micros = yield gen.Task(c.lrange, task + ':micros', 0, -1)
    if not micro:
        micro = micros[0]
    print("micro=", micro)
    methods = yield gen.Task(c.smembers, micro + ':methods')
    if not method:
        method = yield gen.Task(c.get, micro + ':default_method')
    print("method=", method)
    methods.remove(method)
    ops = yield gen.Task(c.lrange, method + ':ops', 0, -1)
    yield gen.Task(c.disconnect)

    desc = {}
    desc['task'] = task
    desc['micros'] = micros
    desc['methods'] = [method]
    desc['methods'].extend(methods)
    desc['ops'] = ops

    print(desc)
    return desc



    
    # if there's no micro, then we assume it's a general task quest
    


