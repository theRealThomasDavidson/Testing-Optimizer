import re

def savings(prop):
    """
    this function will return the most optimal batch size for covid tests given a particular proportion of the tests
    that come up as positives currently this only accounts for true positives.

    :param prop: this is a float that is the proportion of the population

    :return: a tuple of the form (int, float) where the int in the first position is the optimal number of tests for a
    batched testing scenario and the float in the second position is the proportion of tests needed given an optimized
    batch secario.
    """
    batchtests = lambda P, N: (1/N) + (1 - (1 - P)**N)
    if 0 >= prop >= 1:
        return 1, 1.
    low,mid,high = 1, 1, 2
    bt = lambda x: batchtests(prop, x)

    while bt(mid) >= bt(high):
        low = mid
        mid = high
        high *= 2

    l, m1, m2, h = low, int(low + ((high - low ) / 3)), int(low + (2*((high-low)/3))), high

    while l + 5 < h:
        if bt(m1) > bt(m2):
            l = m1
            m1, m2 = int(l + ((h-l)/3)), int(l + (2*((h-l)/3)))
            continue
        h = m2
        m1, m2 = int(l + ((h-l)/3)), int(l + (2*((h-l)/3)))
    a = sorted(list(range(l,h+1)), key=bt)[0]
    print("best batch size is: {}, you need {} as much as without batches".format(a,bt(a)))
    return a, bt(a)



def main():
    """

    :return:
    """
    running = True
    print("Loading...")
    exitPattern = re.compile("exit|quit")
    propPattern = re.compile(r"(?<=prop:\s)\d+\.\d*")
    print("Loading Done")
    #print(7, re.search(r"(?<=prop:\s)\d+\.\d*", "prop: 0.00234\n"))
    #return
    while running:
        action = input("what action should we take?")
        print(action)
        #print(str(exitPattern.match(action.lower())))
        if exitPattern.search(action.lower()):
            running = False
            break
        if propPattern.search(action.lower()):
            number = propPattern.search(action.lower()).group(0)
            number = float(number)
            print("hey",savings(number))



    print("Thank you, good bye.")


if __name__ == "__main__":
    main()