def login_check(func):
    def wrapper(*args, **kwargs):
        print("进入函数")
        func(*args, **kwargs)
        print("退出函数")
    return wrapper

@login_check
def do():
    print("函数执行。。。")

do()