# GPU Task Management Project

## Description

This project demonstrates how to optimize task execution with GPU usage control and memory management. The provided script efficiently schedules and manages tasks across multiple GPUs while considering GPU memory availability and load.

## Requirements

- Python 3.x
- PyTorch
- `tool` module (for batch task management and GPU querying)

Ensure you have these dependencies installed before running the script.

## Usage

1. **Install Dependencies**: Ensure that you have all necessary modules installed. You can use `pip` or `conda` to install the required packages.

2. **Script Overview**:
   - The script demonstrates GPU task management by scheduling and executing tasks with controlled GPU usage and memory management.
   - The `exec_function` simulates GPU workloads and manages memory.

3. **Example Code**:

   ```python
   from tool import batch_task, get_gpu_device
   import torch
   import time

   def exec_function(param1, param2, **kwargs):
       requery_memory = kwargs.get('requery_memory', None)
       gpu_max_usage = kwargs.get('gpu_max_usage', None)
       max_tasks_num_per_gpu = kwargs.get('max_tasks_num_per_gpu', None)
       
       # Get the available GPU devices
       gpu_devices = get_gpu_device(requery_memory, max_tasks_num_per_gpu, gpu_max_usage)
       print(param1, param2, f'Using GPU devices: {gpu_devices}')
       
       # Simulate GPU workload for 30 seconds
       with torch.cuda.device(gpu_devices):
           print(f'Starting computation on GPU {gpu_devices}...')
           # Create a large tensor to occupy GPU memory
           x = torch.rand((10000, 10000)).cuda(gpu_devices)
           # Perform a matrix multiplication to simulate computation
           y = x @ x
           torch.cuda.synchronize()  # Ensure computation is complete
           time.sleep(30)  # Wait for 30 seconds
           print(f'Finished computation on GPU {gpu_devices}')
       
       return

   task_control = {
       'max_try': 0,
       'max_task_num_per_gpu': 3,
       'interval_output_tasks_info': 60 * 0.2,  # seconds
       'gpu_max_load': 70,  # percentage
       'requery_memory': 15000,  # MB
       'error_loop': True
   }

   tasks = []

   for i in range(10):
       task = {
           'task_name': f'task_{i}',
           'func': exec_function,
           'args': (i, i),
           'kwargs': {
               'requery_memory': task_control['requery_memory'],
               'gpu_max_usage': task_control['gpu_max_load'],
               'max_tasks_num_per_gpu': task_control['max_task_num_per_gpu'],
           }
       }
       tasks.append(task)

   batch_task(tasks, **task_control)




output result:

if you running batch_task,you will see these information below:

found avail gpu : GPU 1 - occupied_total:2 - Load: 0.5% - avail_Memory:32412.67MB Memory Used: 97.33MB - Memory Total: 32510.00MB
found avail gpu : GPU 3 - occupied_total:1 - Load: 0.7% - avail_Memory:32416.83MB Memory Used: 93.17MB - Memory Total: 32510.00MB
found avail gpu : GPU 4 - occupied_total:1 - Load: 45.7% - avail_Memory:29828.33MB Memory Used: 2681.67MB - Memory Total: 32510.00MB
[info] pid:116765  task_id: 2 task_name: exec_function  request_memory:15000
model using gpu 2 load:0 occupied_num:1
2 2 Using GPU devices: 2
Starting computation on GPU 2...
exec_function has started.

2024-08-14 15:05
     running time: 0.20 min                         
     running tasks: [2] 1, 2                        
     waiting tasks: [8] 0, 3, 4, 5, 6, 7, 8, 9                         
     completed tasks: [0]                          
     error_tasks: [0]


