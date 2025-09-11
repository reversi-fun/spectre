#!/usr/bin/python3
import sys
from spectre import SPECTRE_POINTS, Mystic_SPECTRE_POINTS, buildSpectreTiles, trot_inv, TILE_NAMES

INFO = {'total':0, 'positive_x':0, 'positive_y':0, 'negative_x':0, 'negative_y':0, 'x_zeros':0, 'y_zeros':0, 'mystic':0}
def reset_info():
    for k in INFO: INFO[k]=0
    INFO['others'] = {}
    INFO['others']["Gamma1"] = 0
    INFO['others']["Gamma2"] = 0
    for label in TILE_NAMES:
        if label != 'Gamma':
            INFO['others'][label] = 0

def plotVertices(tile_transformation, label, scale=1.0):
    vertices = (SPECTRE_POINTS if label != "Gamma2" else Mystic_SPECTRE_POINTS).dot(tile_transformation[:,:2].T) + tile_transformation[:,2]
    ax = ay = 0.0
    verts = []
    for v in vertices:
        x,y = v
        x *= scale
        y *= scale
        verts.append((x,y))
        ax += x
        ay += y
    ax /= len(vertices)
    ay /= len(vertices)
    rot,scl = trot_inv(tile_transformation)
    if '--verbose' in sys.argv:
        print('pos:', ax, ay)
        print('rot:', rot)
        print('scl:', scl)
    INFO['total'] += 1
    if label == "Gamma2":
        INFO['mystic'] += 1
    if label not in INFO['others']: INFO['others'][label] = 0
    INFO['others'][label] += 1

    if ax < 0:
        INFO['negative_x'] += 1
    elif ax > 0:
        INFO['positive_x'] += 1
    else:
        INFO['x_zeros'] += 1
    if ay < 0:
        INFO['negative_y'] += 1
    elif ay > 0:
        INFO['positive_y'] += 1
    else:
        INFO['y_zeros'] += 1

def print_info():
    print(INFO)
    assert INFO['positive_x'] > INFO['negative_x']
    assert INFO['negative_y'] > INFO['positive_y']
    print('there are more right tiles than left tiles by:', INFO['positive_x']-INFO['negative_x'])
    print('x left right ratio:', INFO['negative_x'] / INFO['positive_x'] )
    print('x right left ratio:', INFO['positive_x'] / INFO['negative_x'] )

    print('there are more bottom tiles than top tiles by:', INFO['negative_y']-INFO['positive_y'])
    print('y bottom top ratio:', INFO['negative_y'] / INFO['positive_y'] )
    print('y top bottom ratio:', INFO['positive_y'] / INFO['negative_y'] )

    ## for INFO['others'].values() in print(INFO)
    ## Gamma1,Gamma2,Delta, Sigma counts[1, 8, 63, 496, 3905, 30744] is  https://oeis.org/A001090   === a(n) = 8*a(n-1) - a(n-2); a(0) = 0, a(1) = 1.
    ## Theta,Lambda counts[0, 1, 8, 63, 496, 3905] is https://oeis.org/A001090  == a(n) = 8*a(n-1) - a(n-2); a(0) = 0, a(1) = 1.

    ## Phi counts[2, 14, 110, 866, 6818,53678...] not in https://oeis.org !
    # But, [2,14,110,866,6818,53678..] == a(n) = 8*a(n-1) - a(n-2); a(0) = 2, a(1) = 14.

    ## Pi counts[1, 7, 47, 371, 2913, 22935...] not in  https://oeis.org !
    ## xi counts[2, 6, 48, 370, 2914, 22934...] not in  https://oeis.org !
    # But, {pi & xi} mixed sequence is https://oeis.org/A341927 : Bisection of the numerators of the convergents of cf(1,4,1,6,1,6,...,6,1).
    #           [1, 6, 47, 370, 2913, 22934, 180559, 1421538, 11191745, 88112422, 693707631, 5461548626,... ]
    #  a(n) = 8*a(n-1) - a(n-2); a(0) = 1; a(1) = 6; 
    ## and {xi & pi} mixed sequence is a(n)+1

    ## Psi counts[0, 10, 86, 684, 5392, 42458...] not in https://oeis.org !
    
    for label in INFO['others']:
        v = INFO['others'][label]
        if is_odd(v):
            print('X',end='')
        else:
            print('O',end='')
    print()
    # 値を降順でソートし、重複を排除
    unique_sorted_values = sorted(set(INFO['others'].values()), reverse=True)
    # 各値に詰めた順位番号を割り当て（1位が最大）
    value_to_rank = {v: i + 1 for i, v in enumerate(unique_sorted_values)}
    # 元の順番に対応する順位リストを生成
    rank_list = [value_to_rank[v] for v in INFO['others'].values()]
    print("rabk list:", rank_list)

    counts_min = min([v for v in INFO['others'].values() if v > 0] )
    print('normalized counts:', end=' ')
    for label in INFO['others']:
        print('{}: {}'.format(label, INFO['others'][label]/counts_min) , end=' ')
    print()

def is_odd(v):
    return v % 2

def test(a=10.0, b=10.0, rotation=30, steps=(1,2,3,4,5,6,7,8)):
    for iterations in steps:
        x = buildSpectreTiles(iterations,a,b, rotation_b=rotation)
        reset_info()
        x["Delta"].forEachTile( plotVertices )
        print('ITERATIONS:', iterations)
        print_info()
        # if is_odd(iterations):
            ## we assume this is always true, yet the other labels have dynamics
        assert is_odd(INFO['mystic']) == is_odd(iterations)
        ## the comment below is the output from 6 iterations of the others labels parity
        #1 #OXOXXX     (iteration 1 is unique, not all labels are used)
        #2 #OOXOOOOXX
        #3 #OXOXXOXOO  (same as 5)
        #4 #OOOOOOXXX  (same as 6)
        #5 #OXOXXOXOO  (same as 3)
        #6 #OOOOOOXXX  (same as 4)
        ## because iteration 3 has the same pattern as iteration 5,
        ## and iteration 4 has the same pattern as iteration 6,
        ## we assume that this alternating will continue forever
        ## this should be confirmed by a faster computer than can do more iterations.

if __name__=='__main__':
    if '--quick' in sys.argv:
        test(steps=(1,2,3))
    else:
        test()