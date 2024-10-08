from tool import batch_task
import torch
import time

def exec_function(gpu_device,param1, param2, **kwargs):
    requery_memory = kwargs.get('requery_memory', None)
    gpu_max_usage = kwargs.get('gpu_max_usage', None)
    max_tasks_num_per_gpu = kwargs.get('max_tasks_num_per_gpu', None)
    
    # Get the available GPU devices
    gpu_device = gpu_device
    print(param1, param2, f'Using GPU devices: {gpu_device}')

    if param1 == 1:
        raise ValueError(f'param1 isn\'t equal to 1')
 
    # Simulate GPU workload for 30 seconds
    with torch.cuda.device(gpu_device):
        print(f'Starting computation on GPU {gpu_device}...')
        # Create a large tensor to occupy GPU memory
        x = torch.rand((10000, 10000)).cuda(gpu_device)
        # Perform a matrix multiplication to simulate computation
        y = x @ x
        torch.cuda.synchronize()  # Ensure computation is complete
        time.sleep(30)  # Wait for 30 seconds
        print(f'Finished computation on GPU {gpu_device}')
    
    return

if __name__ == '__main__':

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
