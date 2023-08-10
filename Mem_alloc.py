import copy
import random

global Mem_size
global holes
global segments
global processes

global current_proc
global index
global algo
global seg_num
global memory
global colors
global color_picker
global color_index
global added_process_status

Mem_size = 0
holes = []
segments = []
processes = []

current_proc = []
index = 0
algo = 'f'
seg_num = 0
memory = []
color_picker = []
added_process_status = "fit"
color_index = 0

# #Input memory size
# Mem_size = input("Memory size : ")

# #Input holes
# print("Enter holes, (When done press 'd'):")
# while (1):
#     hole_start = input("Enter hole starting address : ")
#     if hole_start == 'd' : break
#     hole_size = input("Enter hole size : ")
#     holes.append({'name': "", 'start': int(hole_start), 'size': int(hole_size)})

# colors = ["#ffe0e9", "#7fd8be", "#fedc97", "#e8dab2", "#e5e6e4", "#d69f7e", "#abc4ab", "#9999a1", "#c4fff9", "#c5baaf", "#ffec51", "#a68a64", "#c17c74", "#f5ee9e", "#d0b8ac", "#ffcad4"]
colors = ["#ffadad", "#fdffb6", "#caffbf", "#9bf6ff", "#ffd6a5", "#bdb2ff", "#77bfa3", "#ffc6ff", "#a0c4ff", "#b8bedd", "#c89f9c", "#c08497", "#dc93f6", "#9ea93f", "#d69f7e"]
# colors = ["#f3722c", "#f8961e", "#f9c74f", "#90be6d", "#43aa8b", "#577590", "#f07167", "#e9c46a", "#2a9d8f", "#e76f51", "#90be6d", "#9b9b7a", "#02c39a", "#a663cc", "#fcab64"]
def holes_sort_and_combine(holes):
    if holes:
        #sort holes by starting address
        def hole_start(h): return h['start']
        holes.sort(key= hole_start)

        #combine adjacent holes
        while (1):
            # print(holes)
            last_hole = 0
            for i in range(len(holes)):
                if i + 1 < len(holes):
                    if holes[i+1]['start'] <= holes[i]['start'] + holes[i]['size']:
                        holes[i]['size'] += holes[i+1]['size']
                        holes.pop(i+1)
                        break
                else: last_hole = 1
            if last_hole == 1: break

        #removing zero sized holes
        last_hole = 0
        while(holes):
            if len(holes) == 0: break
            if last_hole == 1: break
            for i in range(len(holes)):
                if i + 1 == len(holes): last_hole = 1
                if holes[i]['size'] == 0:
                    holes.pop(i)
                    break

        #naming holes
        if holes:
            for i in range(len(holes)):
                holes[i]['name'] = "Hole" + str(i)


def generate_old_procs():
    holes_sort_and_combine(holes)
    processes.clear()
    segments.clear()
    if holes:
        location = 0
        index = 0
        global colors
        global color_picker
        global color_index
        for h in list(holes):
            if h['start'] > location:
                segments.append({'pid': "Old Process" + str(index), 'name': "", 'start': location, 'size': h['start']-location})
                processes.append({'pid': "Old Process" + str(index), 'seg_num': "", 'seg_info': ""})
                color_picker.append(colors[color_index % 15])
                index += 1
                color_index += 1
            location = h['start'] + h['size']
        #last old process
        if holes[-1]['start'] + holes[-1]['size'] < int(Mem_size):
            segments.append({'pid': "Old Process" + str(index), 'name': "", 'start': location, 'size': int(Mem_size)-location})
            processes.append({'pid': "Old Process" + str(index), 'seg_num': "", 'seg_info': ""})
            color_picker.append(colors[color_index % 15])
            color_index += 1
    else:
        segments.append({'pid': "Old Process0", 'name': "", 'start': 0, 'size': int(Mem_size)})
        processes.append({'pid': "Old Process0", 'seg_num': "", 'seg_info': ""})
        color_picker.append(colors[color_index % 15])
        color_index += 1
    memory_alloc()
    
# generate_old_procs()

def start_(s): return s['start']
def size_(s): return s['size']



def insert_process():
    global holes
    global segments
    global processes
    global index
    global colors
    global color_picker
    global color_index

    global current_proc
    global added_process_status
    global algo
    global seg_num
    global memory
    holes_copy = copy.deepcopy(holes)
    segments_copy = copy.deepcopy(segments)
    processes_copy = copy.deepcopy(processes)
    color_picker_copy = copy.deepcopy(color_picker)
    processes_copy.append({'pid': "P" + str(index), 'seg_num': seg_num, 'seg_info': ""})
    color_picker_copy.append(colors[color_index % 15])
    color_index += 1
    process_fit = 1
    if len(holes_copy) == 0: process_fit = 0

    for j in range(len(current_proc)):

        if algo == 'f':
            #sort holes by starting address
            holes_copy.sort(key= start_)
        elif algo == 'b':
            #sort holes by size
            holes_copy.sort(key= size_)
        elif algo == 'w':
            #sort holes by largest size
            holes_copy.sort(key= size_, reverse= True)

        if len(holes_copy) == 0: process_fit = 0
        if current_proc[j]['size'] == 0: 
            added_process_status = "not fit 0"
            break
        for i in range(len(holes_copy)):
            if current_proc[j]['size'] <= holes_copy[i]['size']:
                current_proc[j]['start'] = holes_copy[i]['start']
                holes_copy[i]['size'] -= current_proc[j]['size']
                holes_copy[i]['start'] += current_proc[j]['size']
                segments_copy.append(current_proc[j])
                processes_copy[-1]['seg_info'] += current_proc[j]['name'] + ": " + str(current_proc[j]['size'])
                if j < int(seg_num) - 1: processes_copy[-1]['seg_info'] += ", "
                holes_sort_and_combine(holes_copy)
                break
            if i + 1 == len(holes_copy): process_fit = 0
        if process_fit == 0:
            index -= 1
            added_process_status = "not fit"

            break
    if process_fit == 1 and added_process_status != "not fit 0":
        color_picker_copy.append(colors[color_index % 15])
        color_index += 1
        holes = copy.deepcopy(holes_copy)
        segments = copy.deepcopy(segments_copy)
        processes = copy.deepcopy(processes_copy)
        color_picker = copy.deepcopy(color_picker_copy)
    del holes_copy
    del segments_copy
    del processes_copy
    del color_picker_copy
        
    index += 1
    memory_alloc()
            


def memory_alloc():
    global holes
    global segments
    global processes
    global memory
    # print(processes)
    # print(color_picker)
    # print(segments)
    if holes or segments:
        memory.clear()
        memory.extend(copy.deepcopy(holes))
        memory.extend(copy.deepcopy(segments))
        memory.sort(key= start_)
    # print(memory)


# memory_alloc()        

# print(holes)
# print(processes)
# print(segments) 
# print(memory)


#deallocate
def de_allocate(proc):
    global holes
    # print(holes)
    # #de-allocate from processes list
    # print(segments)
    for i in range(len(processes)):
        if processes[i]['pid'] == proc:
            processes.pop(i)
            color_picker.pop(i)
            break
    # print(segments)
    #de-allocate from segments list and put holes instead
    indexes = []
    for i in range(len(segments)):
        if segments[i]['pid'] == proc:
            indexes.append(i)
    if indexes:
        for i in range(len(indexes)):
            seg = segments[indexes[-(i + 1)]]
            holes.append({'name': "", 'start': seg['start'], 'size': seg['size']})
            segments.pop(indexes[-(i + 1)])
    holes_sort_and_combine(holes)
    memory_alloc()        

    # print(holes)
    # print(processes)
    # print(segments) 
    # print(memory)

# while (1):
#     de_proc = input("Enter process to de-allocate (when done press 'd') : ")
#     if de_proc == 'd': break
#     de_allocate(de_proc)


    
#apply compaction
def apply_compaction():
    location = 0
    segments.sort(key= start_)
    for seg in list(segments):
        seg['start'] = location
        location += seg['size']
    holes.clear()
    holes.append({'name': "Hole0", 'start': location, 'size': int(Mem_size) - location})
    holes_sort_and_combine(holes)
    memory_alloc()

    # print(holes)
    # print(processes)
    # print(segments) 
    # print(memory)

# comp = input("Press 'c' to  apply compaction : ")
# if comp == 'c': 
#     apply_compaction()

    



