
# c3ba838e19b3e716c2bd793c6809ed02098e7a1983482506da6deb5770546924
# import time

# start = time.time()

# known = {0:0, 1:1}

# def fibonacci_memo(n):
#     if n in known:
#         return known[n]

#     res = fibonacci_memo(n-1) + fibonacci_memo(n-2)
#     known[n] = res
#     return res
# print(fibonacci_memo(40))
# end = time.time()
# print(end - start)

# start = time.time()
# def fibonacci(n):
#     if n == 0:
#         return 0
    
#     if n == 1:
#         return 1

#     return fibonacci(n-1) + fibonacci(n-2)

# print(fibonacci(40))
# end = time.time()
# print(end - start)
 
# letters = 'abcdefghijklmnopqrstuvwxyz'
# numbers = range(len(letters))
