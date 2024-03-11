
import tkinter
import time
from queue import Empty
from multiprocessing import Process, Queue

def win_run (q):
    root = tkinter.Tk()
    w = tkinter.Text(root, height=30)
    w.grid()
    w.after(1, win_get_data, w, q)
    w.update_idletasks()
    w.mainloop()

def win_get_data (w, q):
    try:
        s = q.get(False)
        w.insert(tkinter.END, s + "\n")
        w.update_idletasks()
    except Empty:
        pass
    w.after(1, win_get_data, w, q)

if __name__ == '__main__':
    q = Queue()
    p = Process(target=win_run, args=[q])
    p.start()
    print(f"main: foo [{time.asctime()}]")
    time.sleep(1)
    q.put(f"send from main proc (1) [{time.asctime()}]")
    time.sleep(1)
    print(f"main: bar [{time.asctime()}]")
    time.sleep(1)
    q.put(f"send from main proc (2) [{time.asctime()}]")
    time.sleep(1)
    print(f"main: baz [{time.asctime()}]")
    # and, for example...
    # the tkinter window will not be destroyed even with a buggy parent
    #raise ImportError("not really")
    for i in range(10):
        q.put(f'{i}')
    print(f"main: END [{time.asctime()}]")

