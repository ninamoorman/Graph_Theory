import numpy as np
from itertools import permutations 

# generate Z_2^n elements
def get_group(n):
    group = set()
    # i = number of 1's in array
    for i in range(n+1):
        arr = []

        j = 0
        while j < n:
            if j < i:
                arr.append(1)
            else: 
                arr.append(0)
            j += 1

        perm = permutations(arr) 

        for permutation in perm:
            group.add(permutation)

    group = list(group)
    return group
        
def P1():
    pass

def P2_prime():
    pass

def addition(g_1, g_2):
    g = []

    for i in range(len(g_1)):
        g.append((g_1[i] + g_2[i]) % 2)

    return g

def apply_T(g_1, g_2):
    # permute g_2 defined by 
    for i in range(len(g_1)):
        j = (i+1) % len(g_1)

        j_copy = g_2[j]
        g_2[j] = g_2[i]
        g_2[i] = j_copy

    return g_2

def get_A_i(A_i, z):
    A_result = []
    for a in A_i:
        for b in A_i:
            A_result.append((a, addition(z, b)))
    return A_result

def subset_check(a, b):
    A = set(a)
    B = set(b)
    return A.issubset(B)

def intersection_check(a, b):
    A = set(a)
    B = set(b)

    intersection = A.intersection(B)
    return 0 == len(intersection)

def checkT(group, x, y, A):
    for z in group:
        LHS = []
        LHS.append(apply_T(x, addition(z, y)))
        LHS.append(apply_T(y, addition(z, x)))

        A_1 = A.copy()
        A_1.remove(x)
        A_1 = get_A_i(A_1, z)

        A_2 = A.copy()
        A_2.remove(y)
        A_2 = get_A_i(A_2, z)

        A_3 = A.copy()
        A_3.remove(x)
        A_3.remove(y)
        A_3 = get_A_i(A_3, z)

        RHS = []
        RHS.append(A_1)
        RHS.append(A_2)

        check_1 = subset_check(LHS, A_1) and subset_check(LHS, A_2)
        check_2 = intersection_check(LHS, A_3)

        if not(check_1 and check_2):
            return False
    return True

def main(n):
    group = get_group(n)
    x = group[1]
    y = group[2]
    A = [x, y]

    P2_prime = checkT(group, x, y, A)

if __name__ == "__main__":
    n = 4
    main(n)