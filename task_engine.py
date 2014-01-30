from tornado import gen
import tornadoredis

CONNECTION_POOL = tornadoredis.ConnectionPool(host='C7N6YX1') 


""" Return the description of a task.

The structure include the task, the micro-tasks, the available methods for 
given micro-task, and operators for the given micro-task and method. If method
is not given, use the default method for the micro-task.

"""
@gen.coroutine
def get_desc(task, microidx=0, methodidx=0): 
    c = tornadoredis.Client(connection_pool=CONNECTION_POOL)

    print("task=", task)
    micros = yield gen.Task(c.lrange, task + ':micros', 0, -1)
    micro = micros[microidx]
    print("micro=", micro)
    methods = yield gen.Task(c.lrange, micro + ':methods', 0, -1)
    method  = methods[methodidx]
    print("method=", method)
    ops = yield gen.Task(c.lrange, method + ':ops', 0, -1)
    yield gen.Task(c.disconnect)

    desc = {'task': task, 'micros': micros, 'methods': methods, 'ops': ops}

    print(desc)
    return desc



    
    # if there's no micro, then we assume it's a general task quest
    


