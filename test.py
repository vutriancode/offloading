from threading import Timer
#
#
# def print_result(x):
#     print(x)
#
# def count(x):
#     while True:
#         x += 1
#
# if __name__ == '__main__':
#     t = Timer(3, print_result)
#     t.start()
#
#     count()

def print_result(x):
    print(x)
    Timer(3, print_result, args={x}).start()


def search():
    x = 0
    Timer(3, print_result, args={x}).start()
    while True:
        # search
        print()
        x += 1


search()