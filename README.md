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




# GPU Status and Task Information

## Execution Details

- <span style="color: green;">2024-08-14 15:28</span>
  - Running time: 0.20 min                         
  - Running tasks: [2] 1, 2                        
  - Waiting tasks: [8] 0, 3, 4, 5, 6, 7, 8, 9                         
  - Completed tasks: [0]                          
  - Error tasks: [0]

- <span style="color: magenta; font-weight: bold;">Remaining tasks: 10  Remaining time: 100,000.00 min</span>

- <span style="color: lightblue;">Found available GPU: GPU 1 - Occupied Total: 0 - Load: 6.7% - Available Memory: 15,600.20 MB - Memory Used: 16,909.80 MB - Memory Total: 32,510.00 MB</span>

- **[Info]** PID: 201214  Task ID: 3  Task Name: `exec_function`  Request Memory: 15,000 MB

- <span style="color: lime; font-weight: bold;">Model using GPU 1 Load: 0 Occupied Num: 0</span>
  - Using GPU devices: 1
  - Starting computation on GPU 1...
  - `exec_function` has started.

- <span style="color: lightblue;">Found available GPU: GPU 1 - Occupied Total: 1 - Load: 6.2% - Available Memory: 27,370.30 MB - Memory Used: 5,139.70 MB - Memory Total: 32,510.00 MB</span>

- **[Info]** PID: 201701  Task ID: 4  Task Name: `exec_function`  Request Memory: 15,000 MB

- <span style="color: lime; font-weight: bold;">Model using GPU 1 Load: 0 Occupied Num: 2</span>
  - Using GPU devices: 1
  - Starting computation on GPU 1...
  - `exec_function` has started.

- <span style="color: red;">Didn't find available GPU, please wait...</span>

- <span style="color: green;">2024-08-14 15:28</span>
  - Running time: 0.40 min                         
  - Running tasks: [4] 1, 2, 3, 4                        
  - Waiting tasks: [6] 0, 5, 6, 7, 8, 9                         
  - Completed tasks: [0]                          
  - Error tasks: [0]

- <span style="color: magenta; font-weight: bold;">Remaining tasks: 10  Remaining time: 100,000.00 min</span>

