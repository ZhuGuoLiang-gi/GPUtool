# Project Title

## Description

This project demonstrates how to manage tasks with GPU usage control and memory management.

## Usage

To use this script, you'll need to have the necessary dependencies installed. Ensure that you have the `tool` module available.

### Example Code

Here is an example of how to set up and execute batch tasks with GPU and memory control:

```python
from tool import batch_task, get_gpu_device
import os

def exec_function(param1, param2, **kwargs):
    requery_memory = kwargs.get('requery_memory', None)
    gpu_max_usage = kwargs.get('gpu_max_usage', None)
    max_tasks_num_per_gpu = kwargs.get('max_tasks_num_per_gpu', None)
    gpu_devices = get_gpu_device(requery_memory, max_tasks_num_per_gpu, gpu_max_usage)
    print(param1, param2, f'Using GPU devices: {gpu_devices}')

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
