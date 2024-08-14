from tool import batch_task



def exec_function(param1,param2,**kwargs)
requery_memory = kwargs.get(f'requery_memory',None)
gpu_max_usage  = kwargs.get(f'gpu_max_usage',None)
max_tasks_num_per_gpu = kwargs.get(f'max_tasks_num_per_gpu ',None)
print(param1,param2)

return 





task_control = {
        'max_try' : 0,
        'max_task_num_per_gpu' : 3, 
        'interval_output_tasks_info' : 60 * 0.2, # second
        'gpu_max_load' : 70,   # percentage
        'requery_memory' : 15000 , #MB
        'error_loop': True
    }


    
  for i in range(10)
        if not os.path.exists(child_out_file):
            task = {
                'task_name':f'task_{i}',
                'func':exec_function,
                'args':(i,i),
                'kwargs':{'requery_memory' : task_control['requery_memory'],
                        'gpu_max_usage':task_control['gpu_max_load'],
                        'max_tasks_num_per_gpu':task_control['max_task_num_per_gpu'],
                }
            }
            tasks.append(task)
    
    batch_task(tasks,**task_control)
    
