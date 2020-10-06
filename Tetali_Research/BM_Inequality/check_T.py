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
        
# always breaks when mod 2
def P1(group, x, y):

    for z in group:

        LHS = addition(x, z)
        RHS = addition(y, z)

        T_LHS = apply_T(LHS, RHS)
        # print("T_LHS: ", T_LHS)

        T_RHS = apply_T(x, y)
        # print("T RHS: ", T_RHS)
        T_RHS = addition(T_RHS, z)
        # print(T_RHS)

        z_check = T_LHS == T_RHS

        if not z_check:
            print("\nT({0} + {1}, {2} + {1}) != T({0}, {2}) + {1}".format(x,z, y))
            return False

    return True

def addition(g_1, g_2):
    g = []

    for i in range(len(g_1)):
        element = (g_1[i] + g_2[i]) % 2
        g.append(element)

    
    return g

# multiplication (and operator)
def apply_T(g_1, g_2):
    g = []
    for i in range(len(g_1)):
        element = g_1[i] * g_2[i]
        g.append(element)
    return g

def get_A_i(A_i, z):
    A_result = []
    for a in A_i:
        for b in A_i:
            A_result.append((a, addition(z, b)))
    return A_result

def subset_check(a, b):
    # exist element in LHS not in RHS
    for element in a:
        if element not in b:
            return True
    return False
    
def intersection_check(a, b):
    intersection = []
    for element in a:
        if element in b:
            intersection.append(element)

    return 0 == len(intersection)

def P2_prime(group, x, y, A): # check T
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

# permutations grom g_1 applied to g_2
def permutations_apply_T(g_1, g_2):
    g_1 = [*g_1]
    g_2 = [*g_2]
    
    # permute g_2 defined by 
    for i in range(len(g_1)):
        j = (i+1) % len(g_1)

        j_copy = g_2[j]
        g_2[j] = g_2[i]
        g_2[i] = j_copy

    return g_2

# multiplication (and operator)
def multiplications_apply_T(g_1, g_2):
    g = []
    for i in range(len(g_1)):
        element = g_1[i] * g_2[i]
        g.append(element)
    return g

# or (max operator)
def or_apply_T(g_1, g_2):
    g = []
    for i in range(len(g_1)):
        element = max(g_1[i], g_2[i])
        g.append(element)
    return g

def main(n):
    group = get_group(n)
    x = group[1]
    y = group[2]
    A = [x, y]

    P2_prime_check = P2_prime(group, x, y, A)
    print("P2': ", P2_prime_check)

    P1_check = P1(group, x, y)
    print("P1: ", P1_check)

if __name__ == "__main__":
    n = 3
    main(n)