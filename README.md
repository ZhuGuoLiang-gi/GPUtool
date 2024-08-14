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

       if param1 == 1:
           raise ValueError(f'param1 isn\' equal to 1')
    
       
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




## running output results

### Execution Details
<span style="color: #92c493;">2024-08-14 15:29</span>
- Running time: 0.80 min                         
- Running tasks: [5] 2, 3, 4, 8, 9                        
- Waiting tasks: [4] 0, 5, 6, 7                         
- Completed tasks: [1] 1                         
- Error tasks: [0]

<span style="color: #9b59b6; font-weight: bold;">Remaining tasks: 9  Remaining time: 7.21 min</span>

<span style="color: #1f77b4; font-weight: bold;">`exec_function has started.`</span>

<span style="color: #1f77b4; font-weight: bold;">`TASK 2 HAS COMPLETED`</span>
<span style="color: #1f77b4; font-weight: bold;">`TASK 3 HAS COMPLETED`</span>

<span style="color: #96c5e0;">Found available GPU: GPU 1 - Occupied Total: 1 - Load: 0.7% - Available Memory: 27,905.00 MB - Memory Used: 4,605.00 MB - Memory Total: 32,510.00 MB</span>
<span style="color: #96c5e0;">Found available GPU: GPU 3 - Occupied Total: 2 - Load: 4.5% - Available Memory: 31,415.10 MB - Memory Used: 1,094.90 MB - Memory Total: 32,510.00 MB</span>

**[Info]** PID: 204630  Task ID: 6  Task Name: `exec_function`  Request Memory: 15,000 MB

<span style="color: #2ecc71; font-weight: bold;">Model using GPU 1 Load: 0 Occupied Num: 1</span>


## complete results

---

### Process Summary

**All 10 processes have completed:**
- **Normal task number:** 9
- **Error task number:** 1
- **Running time:** 1.26 min

---

### Error Tasks Information

| Task ID | Task Name | Task Function   |
|:-------:|:---------:|:---------------:|
|    1    |  task_1   | exec_function   |

---


