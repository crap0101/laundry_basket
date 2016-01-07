
import sys
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

TclError = tk._tkinter.TclError
_DELAY = 100

class AnimatedGif (object):
    def __init__ (self, filename, container, delay=_DELAY):
        self._delay = delay
        self._container = container
        self._after_id = None
        self._filename = filename
        self._format = 'gif -index %d'
        self._frame = 0
        self._frames = self._total_frames()
        self._image = None
        self._update()

    def next (self):
        if self._frame >= self._frames:
            self._frame = 0
        else:
            self._frame += 1
        self._update()

    def prev (self):
        if self._frame > 0:
            self._frame -= 1
        else:
            self._frame = self._frames
        self._update()

    def play (self):
        if self._after_id is not None:
            self.stop()
        self.next()
        self._after_id = self._container.after(self._delay, self.play)

    def stop (self):
        if self._after_id is not None:
            self._container.after_cancel(self._after_id)
            self._after_id = None

    def _total_frames (self):
        idx = 0
        while True:
            try:
                _ = tk.PhotoImage(file=self._filename, format=self._format % idx)
                idx += 1
            except TclError:
                idx -= 1
                break
        return idx

    def _update (self):
        try:
            self._image = tk.PhotoImage(file=self._filename, format=self._format % self._frame)
        except TclError as e:
            print (e, self._frame, self._frames)
        self._container.config(image=self._image)
        self._container._image = self._image
        self._container.update_idletasks()

def example (filename, delay):
    root = tk.Tk()
    label = tk.Label(master=root, bg='white')
    gif = AnimatedGif(filename, label, delay=delay)
    play_b = tk.Button(text='play', command=gif.play)
    stop_b = tk.Button(text='stop', command=gif.stop)
    label.pack()
    play_b.pack()
    stop_b.pack()
    root.mainloop()

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.stderr.write("USAGE: %%prog GIF_FILE MS_DELAY\n")
    elif args[1:]:
        example(args[0], args[1])
    else:
        example(args[0], _DELAY)
