import threading
import queue
import contextlib


class MyThreadPool:
    def __init__(self, maxsize=None):
        """
        初始化环境变量
        :param maxsize: 最大线程数
        """
        if maxsize:
            self.queue_size = queue.Queue(maxsize)
        else:
            self.queue_size = queue.Queue()
        self.maxsize = maxsize
        self.free_thread = []
        self.work_thread = []
        self.terminal = False

    def run(self, func, args):
        """
        设置创建线程的规则，完事把任务添加到队列中
        :param func: 要执行的函数名
        :param args: 函数接收的参数
        :return:
        """
        if len(self.free_thread) == 0 and len(self.work_thread) < self.maxsize:
            self.create_thread()
        event = (func, args)
        self.queue_size.put(event)

    def create_thread(self):
        """
        创建线程
        :return:
        """
        t = threading.Thread(target=self.call)
        t.start()

    def call(self):
        """
        执行函数，同时检查还有没有任务，有就重用当前线程继续执行任务
        :return:
        """
        current_thread = threading.currentThread()
        self.work_thread.append(current_thread)
        event = self.queue_size.get()
        while event:
            func, args = event
            func(*args)
            # 调整线程当前的状态，先添加到空闲列表中，检查队列中还有没有任务，
            # 如果有，获取任务，然后从空闲列表中移除当前线程，然后执行
            # 如果没有，则主线程往队列中添加空对象，使线程自己退出
            with self.check_status(current_thread, self.free_thread):
                if self.terminal:
                    event = None
                else:
                    event = self.queue_size.get()
        else:
            self.work_thread.remove(current_thread)

    @contextlib.contextmanager
    def check_status(self, current_thread, free_list):
        """
        设置线程的状态
        :param current_thread: 当前执行的线程
        :param free_list:  空闲线程列表
        :return:
        """
        free_list.append(current_thread)
        try:
            yield
        finally:
            free_list.remove(current_thread)

    def close(self):
        """
        主动关闭线程池
        :return:
        """
        none_num = len(self.work_thread)
        while none_num:
            self.queue_size.put(None)
            none_num -= 1

    def terminate(self):
        """
        无论是否还有任务，终止线程
        """
        self.terminal = True
        while self.work_thread:
            self.queue_size.put(None)
        self.queue_size.queue.clear()
