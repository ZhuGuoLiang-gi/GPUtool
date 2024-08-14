import subprocess
import re
import os
import pty
import multiprocessing
from typing import List, Tuple, Callable, Any
import paramiko
import pynvml
import time
import traceback
import threading
import GPUtil
import numpy as np

def get_gpu_info():
    # 运行 nvidia-smi 命令并捕获输出
    result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,memory.free', '--format=csv,nounits,noheader'],
                            stdout=subprocess.PIPE, encoding='utf-8')

    # 解析输出
    gpu_info = result.stdout.strip().split('\n')
    gpus = []
    for info in gpu_info:
        index, name, memory_total, memory_used, memory_free = info.split(',')
        gpus.append({
            'id': int(index),
            'name': name.strip(),
            'memory_total': int(memory_total),
            'memory_used': int(memory_used),
            'memory_free': int(memory_free)
        })

    # 按空闲显存排序
    gpus = sorted(gpus, key=lambda x: x['memory_free'], reverse=True)


    free_gpus = gpus

    if free_gpus:
        for gpu in free_gpus:
            print(f"GPU ID: {gpu['id']}, 名称: {gpu['name']}")
            print(f"  总显存: {gpu['memory_total']} MB")
            print(f"  已使用显存: {gpu['memory_used']} MB")
            print(f"  空闲显存: {gpu['memory_free']} MB")
            print("")
    else:
        print("没有找到空闲的 GPU")

    return gpus

def get_free_gpus(min_memory_mb):
    result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,memory.free', '--format=csv,nounits,noheader'],
                            stdout=subprocess.PIPE, encoding='utf-8')

    gpu_info = result.stdout.strip().split('\n')
    available_gpus = []
    for info in gpu_info:
        index, name, memory_total, memory_used, memory_free = info.split(',')
        memory_free = int(memory_free)
        if memory_free >= min_memory_mb:
            available_gpus.append(int(index))
    return available_gpus



def execute_remote_command(command,server_ip,username):

    server_ip = '172.16.20.151'
    username = 'zhengliangzhen'
    
    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 连接到服务器
        ssh.connect(server_ip, username=username)
        
        current_directory = os.getcwd()
        command = f'cd {current_directory} &&' + command 
        # 执行远程命令
        stdin, stdout, stderr = ssh.exec_command(command,get_pty=True)
        
        # 设置非阻塞模式
        stdout.channel.setblocking(0)
        stderr.channel.setblocking(0)
        
        # 创建一个文件描述符列表
        channels = [stdout.channel, stderr.channel]
        data = {stdout.channel: b'', stderr.channel: b''}
        
        # 循环读取输出
        while True:
            # 使用select选择可读通道
            readable, _, _ = select.select(channels, [], [])
            for chan in readable:
                try:
                    data[chan] += chan.recv(4096*2)
                except Exception as e:
                    pass


                # 检查是否还有数据可读
                if chan.recv_ready():
                    continue
                # 打印输出结果
                if chan is stdout.channel:
                    if data[stdout.channel]:
                        print(data[stdout.channel].decode('utf-8'), end='')
                        data[stdout.channel] = b''  # 清空缓冲区
                else:
                    if data[stderr.channel]:
                        print(data[stderr.channel].decode('utf-8'), end='')
                        data[stderr.channel] = b''  # 清空缓冲区

            # 检查命令是否已经执行完成
            if stdout.channel.exit_status_ready() and not stderr.channel.recv_ready():
                break
        
    finally:
        # 关闭SSH连接
        ssh.close()




def run_command(command):
    import pty
    import subprocess
    import os
    import sys
    import select
    import errno

    master, slave = pty.openpty()
    process = subprocess.Popen(command, shell=True, stdout=slave, stderr=slave, stdin=slave, universal_newlines=True)
    os.close(slave)  # Close slave descriptor in parent process

    output = []

    try:
        while process.poll() is None:
            if master < 0:
                break  # Check if master descriptor is valid

            rlist, _, _ = select.select([master], [], [], 0.1)
            if rlist:
                try:
                    data = os.read(master, 1024).decode('utf-8', errors='ignore')
                    if data:
                        output.append(data)
                        sys.stdout.write(data)
                        sys.stdout.flush()
                except OSError as e:
                    if e.errno == errno.EIO:  # Handle IOError
                        break
    finally:
        if master >= 0:
            os.close(master)

    return ''.join(output)

def check_gpu_memory(min_memory,gpu_id):

    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)  # 假设使用第一个GPU
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    free_memory = info.free / 1024 / 1024  # 转换为MB
    pynvml.nvmlShutdown()
    
    return free_memory >= min_memory

def get_gpu_usage(gpu_id):
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu", "--format=csv,nounits,noheader", f"--id={gpu_id}"],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        memory_used, memory_total, utilization = map(int, output.split(','))
        return utilization
 
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def get_gpu_task_count(gpu_index):
    try:
        # Get GPU UUIDs and PIDs
        result = subprocess.run(['nvidia-smi', '--query-compute-apps=gpu_uuid,pid', '--format=csv,noheader'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8').strip().split('\n')
        gpu_processes = []
        for line in output:
            line = line.strip()
            if line:
                gpu_uuid, pid = line.split(',')
                gpu_processes.append({
                    'gpu_uuid': gpu_uuid.strip(),
                    'pid': int(pid.strip())
                })
        # Get GPU indices and map GPU UUIDs to indices
        result = subprocess.run(['nvidia-smi', '--query-gpu=index,gpu_uuid', '--format=csv,noheader'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8').strip().split('\n')
        gpu_indices = {}
        for line in output:
            line = line.strip()
            if line:
                index, gpu_uuid = line.split(',')
                gpu_indices[gpu_uuid.strip()] = int(index.strip())
        # Count processes for the specified GPU index
        task_count = 0
        for process in gpu_processes:
            if process['gpu_uuid'] in gpu_indices:
                if gpu_indices[process['gpu_uuid']] == gpu_index:
                    task_count += 1
        return task_count

    except Exception as e:
        print(f"Error: {e}")
        return 999
    

def batch_task(tasks,**kwargs):
    

    max_try = kwargs.get('max_try',5)
    max_task_num_per_gpu = kwargs.get('max_task_num_per_gpu',5)
    interval_output_tasks_info = kwargs.get('interval_output_tasks_info',300)
    gpu_max_load = kwargs.get('gpu_max_load',80)
    requery_memory = kwargs.get('requery_memory',1000)
    error_loop = kwargs.get('error_loop',False)
    
    
    global running_tasks, waiting_tasks, completed_tasks, error_tasks
    
    def print_tasks_info():
        global running_tasks, waiting_tasks, completed_tasks,error_tasks,terminate_event
        start_runings = time.time()
        interval_time_start =  0
        
        while not terminate_event.is_set():
            
            current_time = time.time()
            time_data = time.strftime('%Y-%m-%d %H:%M', time.localtime(current_time))
            running_time = (current_time - start_runings) / 60 
            remaining_task = len(running_tasks) + len(waiting_tasks)
            task_per_time = len(completed_tasks) / (running_time + 0.000001)
            remaining_time = remaining_task / (task_per_time + 0.0001)
            interval_time_end = time.time()
            interval_time = (interval_time_end - interval_time_start)
            if  interval_output_tasks_info - interval_time < 0:
                interval_time_start =  time.time()
                print(
                    f'\n\033[92m\n{time_data}\n\t running time: {running_time:.2f} min \
                        \n\t running tasks: [{len(running_tasks)}] {", ".join(map(str, running_tasks))}\
                        \n\t waiting tasks: [{len(waiting_tasks)}] {", ".join(map(str, waiting_tasks))} \
                        \n\t completed tasks: [{len(completed_tasks)}] {", ".join(map(str, completed_tasks))} \
                        \n\t error_tasks: [{len(error_tasks)}] {", ".join(map(str, error_tasks))}\033[0m\n',flush=True
                )
                    
                print('\033[1;35m' + f'remaining tasks: {remaining_task}  remaining time: {remaining_time:.2f}' + ' min' + '\033[0m',flush=True)
            time.sleep(1)
        return 0
    
    def monitor_gpu(gpu_queue):
        time_log = []
        global terminate_event
        while not terminate_event.is_set():
            for i in range(2):
                gpus = GPUtil.getGPUs()
                gpu_status = [(gpu.id, gpu.load, gpu.memoryUsed, gpu.memoryTotal) for gpu in gpus]
                time_log.append(gpu_status)
                if len(time_log) > 10:
                    time_log = time_log[-10:]
                time.sleep(1)
                
            while not gpu_queue.empty():
                try:
                    gpu_queue.get_nowait()
                except queue.Empty:
                    break
            gpu_queue.put(time_log)
        return False
        
            
            
    def detect_gpu_state(gpu_queue,requery_memory,max_load=80):
        global terminate_event
        avail_gpu = []
        if not gpu_queue.empty():
            gpu_info = {}
            gpu_status = gpu_queue.get()
            for time_log in gpu_status:
                for gpu_id, load, memory_used, memory_total in time_log:
                    if gpu_id not in gpu_info:
                        gpu_info[gpu_id]={}
                        gpu_info[gpu_id]['load'] = []
                        gpu_info[gpu_id]['memory_used'] = []
                        gpu_info[gpu_id]['memory_total'] = []
                    gpu_info[gpu_id]['load'].append(load)
                    gpu_info[gpu_id]['memory_used'].append(memory_used)
                    gpu_info[gpu_id]['memory_total'].append(memory_total)
            avail_gpu_info = ''
            for gpu_id in gpu_info:
                load = np.mean(gpu_info[gpu_id]['load'])
                memory_used = np.mean(gpu_info[gpu_id]['memory_used'])
                memory_total = np.mean(gpu_info[gpu_id]['memory_total'])
                avil_memory = memory_total -memory_used
                task_num = get_gpu_task_count(gpu_id)
                if avil_memory > requery_memory  and load*100 < max_load and task_num < max_task_num_per_gpu:
                    avail_gpu_info += f"\033[96m\nfound avail gpu : GPU {gpu_id} - ocuppied_total:{task_num} - Load: {load*100:.1f}% - avil_Memory:{avil_memory:.2f}MB Memory Used: {memory_used:.2f}MB - Memory Total: {memory_total:.2f}MB\033[0m"
                    avail_gpu.append(gpu_id)
            print(avail_gpu_info,flush=True)
        return avail_gpu
    
            
    def worker(idx, task_func, args, kwargs,error_queue,status_queue):
        try:
            status_queue.put((idx, "started"))
            result = task_func(*args, **kwargs)
            status_queue.put((idx, "completed"))
        except Exception as e:
            error_queue.put((idx, task_func, args, kwargs, str(e), traceback.format_exc()))
            return 0
        return 1
    
    def stop_processes():
        global completed_tasks,running_tasks
        global processes 
        for idx in list(processes.keys())[:]:  # 创建键的副本
            p_idx = processes[idx]
            if not p_idx.is_alive():
                p_idx.join()
                running_tasks.remove(idx)
                completed_tasks.append(idx)
                print(f"\033[1;34m\nTASK {idx} HAS COMPLETED\033[0m")
                del processes[idx]
        return 1

    def all_tasks_complete_justification():
        global error_queue,processes,completed_tasks,copy_task_id
        if not processes and  error_queue.empty() and len(completed_tasks) == len(copy_task_id):
            return True
        else:
            return False
        
    def obtain_error_info(max_try,error_loop):
        
        global running_tasks, waiting_tasks, completed_tasks, error_tasks
        global error_queue,task_id,processes,task_task_times,gpu_queue,task_task_times 
        
        while not error_queue.empty():
            idx, task_func, args, kwargs, error_message, traceback_info = error_queue.get()
            print(f"\033[31mError in task:{task_name} \n\ttask_id:{idx} \n\tfunc_name:{task_func} \n\terror info:{error_message}\033[0m",flush=True)
            print('\n\033[1;35m' + traceback_info + '\033[0m',flush=True)
            
        
            p_idx = processes[idx]
            p_idx.terminate()
            p_idx.join()
           
            error_tasks.append(idx)
            running_tasks.remove(idx)
            completed_tasks.append(idx)
            del processes[idx]
            
            if task_task_times[idx] <  max_try and error_loop:
                bold_black_on_white = "\033[1m\033[30m\033[47m"
                reset = "\033[0m"
                print(f'{bold_black_on_white}re_running task {idx} \n\t running times: {task_task_times[idx]} \n\t max time: {max_try}{reset}', flush=True)
                task_id[idx] = copy_task_id[idx]
                waiting_tasks.append(idx)
                completed_tasks.remove(idx)
                error_tasks.remove(idx)
                task_task_times[idx] += 1
        return 1
        
    
    global error_queue,task_id,processes,task_task_times,gpu_queue, task_task_times,copy_task_id,terminate_event

    error_queue = multiprocessing.Queue()
    task_id = {id: task for id, task in enumerate(tasks)}
    processes = {}
    copy_task_id = task_id.copy()
    status_queue = multiprocessing.Queue()
    running_tasks =[]
    waiting_tasks = [id for id in range(len(tasks))]
    completed_tasks = []    
    error_tasks = []
    task_task_times = {idx:0 for idx,task in enumerate(tasks)}
    all_task_completed = False
    terminate_event = multiprocessing.Event()
    start_running_time = time.time()
    

    gpu_queue = multiprocessing.Queue()
    gpu_thread = threading.Thread(target=monitor_gpu, args=(gpu_queue,))
    gpu_thread.daemon = True
    gpu_thread.start()
    
    print_tasks_info_thread = threading.Thread(target=print_tasks_info)
    print_tasks_info_thread.daemon = True
    print_tasks_info_thread.start()
    

    try:
        multiprocessing.set_start_method('spawn')  
    except:
        pass
    

    while not all_task_completed:
        
        for idx in list(task_id.keys())[:]:
            task = task_id[idx]
            func = task['func']
            args = task['args']
            kwargs = task['kwargs']
            

            avail_gpu = detect_gpu_state(gpu_queue,requery_memory,max_load=gpu_max_load)
            
            if len(avail_gpu) == 0:
                for i in range(3):
                    message = "\033[31mDidn't find available GPU, please wait" + "." * (i + 1) + "\033[0m"
                    print(message, end='\r', flush=True)
                    time.sleep(1)
                print(' ' * len(message), end='\r', flush=True)  # 清空行
                continue
            

            task_name = f"{func.__name__}"
            p = multiprocessing.Process(target=worker, args=(idx, func, args, kwargs, error_queue,status_queue))
            processes[idx] = p
            p.start()
            pid = p.pid
            print(f'[info] pid:{pid}  task_id: {idx} task_name: {task_name}  request_memory:{requery_memory}',flush=True)
            del task_id[idx]

            task_started = False
            while not task_started:
                if not status_queue.empty():
                    task_idx, status = status_queue.get()
                    if status == "started":
                        print(f"{task_name} has started.")
                        running_tasks.append(task_idx)
                        waiting_tasks.remove(task_idx)
                        task_started = True
                time.sleep(1)
            
            stop_processes()
            obtain_error_info(max_try,error_loop)
            all_task_completed=all_tasks_complete_justification()
            time.sleep(1)
        stop_processes()
        obtain_error_info(max_try,error_loop)
        all_task_completed=all_tasks_complete_justification()

    terminate_event.set()
    gpu_thread.join()
    print_tasks_info_thread.join()    
    end_running_time = time.time()
    running_time = (end_running_time - start_running_time) / 60

    gpu_queue.get()
    gpu_queue.close()
    gpu_queue.join_thread()
    
    while not error_queue.empty():
        error_queue.get()
    error_queue.close()
    error_queue.join_thread()
    

    orange_color = "\033[38;5;208m"
    red_color = "\033[1m\033[31m" 
    purple_color ="\033[1m\033[35m" 
    bold_italic = "\033[1m\033[3m"
    reset = "\033[0m"
        
    finished_prompt = f'all {len(copy_task_id)} processes have completed'
    print(f'\n{orange_color}' + '-'*len(finished_prompt) + f'{reset}\n')
    print(f'{orange_color}{bold_italic}{finished_prompt}{reset}')
    print(f'{orange_color}{bold_italic}normal task number: {len(completed_tasks)-len(error_tasks)}{reset}')
    print(f'{orange_color}{bold_italic}error task number: {len(error_tasks)}{reset}')
    print(f'{orange_color}{bold_italic}running time: {running_time:.2f} min {reset}')
    print(f'\n{orange_color}' + '-'*len(finished_prompt) + f'{reset}\n')
    
    

    if len(error_tasks) > 0:
         
        if 'task_name' not in copy_task_id[0]:
            for idx in copy_task_id:
                copy_task_id[idx]['task_name']='None' 
                
        max_lengths = {
        'task_id': len('task_id'),
        'task_name': max(len(copy_task_id[idx]['task_name']) for idx in error_tasks),
        'task_function': max(len(copy_task_id[idx]['func'].__name__) for idx in error_tasks)
        }

        column_widths = {key: value + 5 for key, value in max_lengths.items()}
        total_len = sum(column_widths.values())

        header = (
        f"{purple_color}{bold_italic}"
        f"{'task_id':^{column_widths['task_id']}}"
        f"{'task_name':^{column_widths['task_name']}}"
        f"{'task_function':^{column_widths['task_function']}}"
        f"{reset}"
        )
        print(f'\n{orange_color}' + '-'*total_len + f'{reset}')
        print(f"{red_color}{bold_italic}{'ERROR TASKS INFORMATION':^{total_len}}{reset}")
        print(f'{orange_color}' + '-'*total_len + f'{reset}')
        print(header)
        print(f'{orange_color}' + '-'*total_len + f'{reset}')
        for idx in sorted(error_tasks):
            task_name = copy_task_id[idx]['task_name']
            task_f = copy_task_id[idx]['func'].__name__
            row = (
            f"{orange_color}{bold_italic}"
            f"{str(idx):^{column_widths['task_id']}}"
            f"{task_name:^{column_widths['task_name']}}"
            f"{task_f}{reset}"
        )

            print(row)
        print(f'{orange_color}' + '-'*total_len + f'{reset}\n')


    return 0
    
    
