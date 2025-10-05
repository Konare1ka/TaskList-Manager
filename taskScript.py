import json
import os
import argparse
from datetime import datetime

def openJSON():
    directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directory, "taskList.json")
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            #print(data) #debug
            return data, path
    except FileNotFoundError:
        print("task-list script try open JSON file, but did not find the JSON file in the script directory")
    except UnicodeDecodeError:
        print("task-list script cannot decode JSON file using UTF-8 encoding")
    except Exception as exception:
        print(f"task-list script try open JSON file, but got an error: {exception}")

def output(task):
    print(f"\n ID: {task.get("id")}")
    print(f" Title: {task.get("title")}")            
    print(f" Description: {task.get("description")}")
    print(f" State: {task.get("state")}")
    print(f" Notes: {task.get("notes")}")
    print(f" Created: {task.get("created")}")

def tasksOutput(data, state=None, full=False):
    print("\n List of tasks:")
    if not data:
        print("\n No tasks")
    counter = 0
    for task in data:
        if not full and not state:
            if task.get("state") == "Complete" and not full: continue
            counter += 1
            print(f" {task.get("id")}){task.get("title")}")
            if counter > 3: break
        elif full and not state:
            output(task)
        elif state and not full:
            if task["state"] == state:
                output(task)
            
def valueTaskOutput(data, index):
    if index < 1 or index > len(data):
        print(f" This task does not exist, all tasks are: {len(data)}")
        return
    task = data[index-1]
    output(task)

def createTask(data, ID=None):
    if ID != None:
        data.pop(ID-1)
    else: ID = len(data)+1
    print(f"\n ID: {ID}")
    title = str(input(" Title: "))
    desc = str(input(" Description: "))
    state = str(input(" Choose a state(plans, progress, complete): ")).capitalize()
    notes = str(input(" Maybe you want to include notes?: "))
    print(f" Created: {datetime.now().strftime("%Y-%m-%d %H:%M")}")
    newTask = {
        "id":len(data)+1,
        "title":title,
        "description":desc,
        "state": (state if state in ["Plans", "Progress", "Complete"] else "Not specified"),
        "notes":notes,
        "created":datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    data.insert(ID-1, newTask)
    handleTasks(data)

def deleteTask(data, ID, wipe=False):
    if wipe and ID is None:
        data.clear()
        print(f" Tasks list was clear")
        handleTasks(data)
    else:
        data.pop(ID-1)
        print(f" Task number {ID} was successfuly deleted")
        handleTasks(data)
    
def elevateTask(data, ID):
    for task in data:
        if task["id"] == ID and task["state"] == "Complete":
            print(" A completed task cannot be moved to the top of the list")
            return
        if task["id"] == ID:
            data.insert(0, task)
            data.pop(ID) #because json list +1 task
            handleTasks(data)
            
def editTask(data, args):
    for task in data:
        if task["id"] == int(args[0]):
            task[args[1]] = args[2]
    print(f" Task {args[0]} changed {args[1]} to \"{args[2]}\"")
            
def handleTasks(data, fresh=False):
    completedTasks = []
    othersTasks = []
    for task in data:
        if task.get("state") == "Complete":
            completedTasks.append(task)
        else:
            othersTasks.append(task)
    data[:] = othersTasks + completedTasks
    for i, task in enumerate(data, 1):
        task["id"] = i
    updateTask(data)

def updateTask(data):
    try:
        with open(path, "w", encoding="utf-8") as jsonFile:
            json.dump(data, jsonFile, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{e} need to fix")
    else: print("\n Changes saved successfully")

def argsGet():
    parser = argparse.ArgumentParser(prog="taskList",
                                                            description="Task List manager",
                                                            epilog="""
Examples:

python taskScript.py --add (To create task)
python taskScript.py --edit 3(ID) notes(name) "Update system before start"(value)
python taskScript.py --view complete (View all completed tasks)
python taskScript.py --fresh 2 (Rewrite task)
""", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--full", action="store_true", help="Display full list of tasks")
    parser.add_argument("-c", "--check", type=int, help="Display task information")
    parser.add_argument("-v", "--view", choices=["plans", "progress", "complete"], help="View a specific task type")
    parser.add_argument("-a","--add", action="store_true", help="Create a new task")
    parser.add_argument("-d","--delete", type=int, help="Delete a task (Specify ID)")
    parser.add_argument("-e","--elevate", type=int, help="Move task to top by ID (NOT COMPLETED)")
    parser.add_argument("-r","--refresh", action="store_true", help="Forced refresh tasks")
    parser.add_argument("--wipe", action="store_true", help="Delete all tasks")
    parser.add_argument("-t", "--edit", nargs=3, help="Edit task, choose ID, name and value")
    parser.add_argument("--fresh", type=int, help="Overwrite task (specify ID)")
    return parser.parse_args()

def main():
    global path
    data, path = openJSON()
    args = argsGet()
    if args.full: tasksOutput(data, full=True)
    elif args.check: valueTaskOutput(data, args.check)
    elif args.view: tasksOutput(data, args.view.capitalize(), full=False)
    elif args.add: createTask(data)
    elif args.fresh: createTask(data, args.fresh)
    elif args.delete: deleteTask(data, args.delete)
    elif args.elevate: elevateTask(data, args.elevate)
    elif args.refresh: handleTasks(data)
    elif args.edit: editTask(data, args.edit)
    elif args.wipe: deleteTask(data, ID=None, wipe=True)
    else: tasksOutput(data)
    
if __name__ == "__main__":
    main()