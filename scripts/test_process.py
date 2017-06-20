from multiprocessing import Pool
import time
import os


def f1(arg):
    print("func f1", arg, os.getpid())
    time.sleep(1)


def bar(i):
    print("===============func bar", os.getpid())


if __name__ == "__main__":
    pool = Pool(5)

    for i in range(10):
        # p = pool.apply(func=f1, args=(i, ))
        p = pool.apply_async(func=f1, args=(i, ), callback=bar)
    print("main", os.getpid())
    pool.close()
    # pool.terminate()
    pool.join()