import heapq
import itertools

heap = []
array = {"ovocie":"mandarinka", "zelenina":"mrkva", "sladkosti":"cukriky", "auto":"ferrari"}
array2 = ["ovocie","mandarinka", "zelenina","mrkva", "sladkosti","cukriky", "auto","ferrari"]
array3 = [10,8,4,6,8,3,4,8,9,7,987,98,6,1,96,7,3]
heap2 = heapq.heapify(array2)
print("heap2 {}".format(heap2))
heap3 = heapq.heapify(array3)
print("heap3 {}".format(heap3))
heapq.heappush(heap, "xxx")
print(heap)
heapq.heappush(heap, "auto")
print(heap)
heapq.heappush(heap, "fly")
print(heap)
heapq.heappush(heap, "aaa")
print(heap)
heapq.heappush(heap, "abaa")
print(heap)

pq = []
entry_finder = {}
REMOVED = "<removed-task>"
counter = itertools.count()

def add_task(task, priority = 0):
	"add a new task or update the priority of an existing task"
	if task in entry_finder:
		remove_task(task)
	count = next(counter)
	entry = [priority, count, task]
	entry_finder[task] = entry
	heapq.heappush(pq, entry)

def remove_task(task):
	"mark an existing task as REMOVED. Raise keyError if not found"
	entry = entry_finder.pop(task)
	entry[-1] = REMOVED

def pop_task():
	"Remove and return the lowest priority task. Raise keyError if empty"
	while pq:
		priority, count, task = heapq.heappop(pq)
		if task is not REMOVED:
			del entry_finder[task]
			return (task, priority)
	return []

add_task("goHome", 1)
print("priority queue pq: {0}".format(pq))
add_task("tidy Up", 0)
print("priority queue pq: {0}".format(pq))
add_task("relax", 3)
print("priority queue pq: {0}".format(pq))
add_task("mishmash", 4)
print("priority queue pq: {0}".format(pq))
add_task("surfing", 0)
print("priority queue pq: {0}".format(pq))

print("priority queue pq: {0}".format(pq))
poped = pop_task()
print("{1} was removed by pop_task_1 with priority {2}, queue pq: {0}".format(pq, poped[0], poped[1]))
poped = pop_task()
print("{1} was removed by pop_task_1 with priority {2}, queue pq: {0}".format(pq, poped[0], poped[1]))
poped = pop_task()
print("{1} was removed by pop_task_1 with priority {2}, queue pq: {0}".format(pq, poped[0], poped[1]))
poped = pop_task()
print("{1} was removed by pop_task_1 with priority {2}, queue pq: {0}".format(pq, poped[0], poped[1]))
poped = pop_task()
print("{1} was removed by pop_task_1 with priority {2}, queue pq: {0}".format(pq, poped[0], poped[1]))
poped = pop_task()
print("{1} was removed by pop_task_1 with priority {2}, queue pq: {0}".format(pq, poped[0], poped[1]))