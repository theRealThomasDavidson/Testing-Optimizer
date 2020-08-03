import re
import Objects
import pickle
from datetime import datetime
import os
warranty = """
    \tThis is the Batch Testing Organizer. it hopes to remove some of the logistical headaches of batch virus testing
    Copyright (C) 2020  Thomas Davidson (davidson.thomasj@gmail.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

copyr = """Testing Organizer Copyright (C) 2020  Thomas Davidson (davidson.thomasj@gmail.com)
    This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details."""


def batchSizeOptimizer(prop):
    """
    this function will return the most optimal batch size for covid tests given a particular proportion of the tests
    that come up as positives currently this only accounts for true positives.

    :param prop: this is a float that is the proportion of the population

    :return: a tuple of the form (int, float) where the int in the first position is the optimal number of tests for a
    batched testing scenario and the float in the second position is the proportion of tests needed given an optimized
    batch secario.
    """
    if not isinstance(prop, float):
        raise TypeError
    if 0 >= prop or prop >= 1:      #domain check: to be fair these should probably be
        raise ValueError("Math Domain Error: input should be between 0 and 1 used value was {}".format(prop))

    batchtests = lambda P, N: (1/N) + (1 - (1 - P)**N)
    low, mid, high = 1, 1, 2
    bt = lambda x: batchtests(prop, x)

    while bt(mid) > bt(high) and bt(high) < 1:

        low = mid
        mid = high
        high *= 2
    if bt(mid) == 1.:
        return 1, 1.

    l, m1, m2, h = low, int(low + ((high - low ) / 3)), int(low + (2*((high-low)/3))), high

    while l + 5 < h:
        if bt(m1) > bt(m2):
            l = m1
            m1, m2 = int(l + ((h-l)/3)), int(l + (2*((h-l)/3)))
            continue
        h = m2
        m1, m2 = int(l + ((h-l)/3)), int(l + (2*((h-l)/3)))
    a = sorted(list(range(l,h+1)), key=bt)[0]
    print("best batch size is: {}, you need {} as much as without batches".format(a, bt(a)))
    if bt(a) >= 1.:
        return 1, 1.
    return a, bt(a)



def main():
    """

    :return:
    """
    running = True
    print(copyr)
    pickles = []
    for root, dirs, files in os.walk("."):
        path = root.split(os.sep)
        for file in files:
            if file.endswith(".pkl"):
                temp = os.path.join(root, file)
                pickles.append(temp)
    pickPattern = re.compile(r"(\d+|none)(?=\s*)")
    print("#########################################")
    for ndx in range(len(pickles)):
        # if runningTests[key]._status not in (1, 3):
        # continue
        print("#############Use {} to link to###########\n{}\n#########################################".format(ndx, pickles[ndx]))
    runningTests = {}
    runningTestNum = 0
    while True:
        temp = pickPattern.search(input("Use the link number to load that file. Use 'None' to start from scratch: "))
        while not temp:
            temp = pickPattern.search(
                input("Use the link number to report result for that. Use 'None' to start from scratch: "))

        if temp.group(0) == "none":
            print("Loading...")
            organ = Objects.BatchTestingOrganizer()
            break

        elif int(temp.group(0)) >= len(pickles):
            print("{} did not appear to be in the the active tests.".format(int(temp.group(0))))
            continue
        else:
            print("Loading...")
            filename = pickles[int(temp.group(0))]
            data = open(filename, 'rb')
            restore = pickle.load(data)
            data.close()
            organ = Objects.BatchTestingOrganizer(restore=restore)
            for item in organ.individualStore._testing:
                runningTests[runningTestNum] = organ.individualStore._testing[item]
                runningTestNum +=1
            for item in organ.batchStore._testing:
                runningTests[runningTestNum] = organ.batchStore._testing[item]
                runningTestNum += 1
            break


    Objects.cases = [1, 2]                                              #cases with positives first then totoal pop our null is 50/50
                                                                        #and becomes negligable after we have a lot of samples
    copyrightPattern = re.compile(r"(show c)\s*")
    warrantyPattern = re.compile(r"(show w)\s*")
    exitPattern = re.compile(r"(exit|quit)\s*")                         #exit command
    propPattern = re.compile(r"(?<=prop:)\s*\d*\.\d+\s*")               #find batch size based on proportion
    addPattern = re.compile(r"(?<=add pop:)\s*\d+\s+\d+\s*")            #add cases to population with positives first then negatives
    newCasePattern = re.compile(r"(?<=add patient)\s*")                 #add cases to population with positives first then negatives
    popPattern = re.compile(r"population\s*")
    batchPattern = re.compile(r"batch size\s*")
    resultsPattern = re.compile(r"(?<=test results)\s*")
    nextTestPattern = re.compile(r"get next(?=\s*)")
    posNegPattern = re.compile(r"(\+|-)(?=\s*)")
    digitPattern = re.compile(r"(\d+|oops)(?=\s*)")
    savePattern = re.compile(r"(save)(?=\s*)")
    print("Loading Done")
    while running:
        try:
            action = input("what action should we take? ")
            #print(action)
            if exitPattern.search(action.lower()):
                print("Shutting down program...")
                # create a pickle file
                filename = ".\SavedStates\BatchOrganizer_Date_{}.pkl".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                picklefile = open(filename, 'wb+')
                saved = organ.shutdown()
                pickle.dump(saved, picklefile)
                picklefile.close()
                print("Save successful in {}".format(filename))
                running = False
                break

            if propPattern.search(action.lower()):
                number = propPattern.search(action.lower()).group(0)
                number = float(number)
                batchSizeOptimizer(number)      #just run for the print probably will fix this later
                continue

            if addPattern.search(action.lower()):
                #print(addPattern.search(action.lower()))
                numbers = addPattern.search(action.lower()).group(0)
                pos, neg = [int(x) for x in numbers.split()]
                Objects.cases[0] += pos
                Objects.cases[1] += neg + pos
                batchSizeOptimizer((Objects.cases[0]/Objects.cases[1]))
                continue

            if popPattern.search(action.lower()):
                print("Positive cases: \t{}\nTotal tests:\t\t{}\nPositive percentage: \t{:.4f}%".format(
                    Objects.cases[0], Objects.cases[1], 100. * Objects.cases[0]/Objects.cases[1]))
                continue

            if batchPattern.search(action.lower()):
                batchSizeOptimizer((Objects.cases[0] / Objects.cases[1]))
                continue

            if newCasePattern.search(action.lower()):
                organ.newID(input("Enter new Accession Number: "))

            if resultsPattern.search(action.lower()):
                print("#########################################")
                for key in runningTests:
                    #if runningTests[key]._status not in (1, 3):
                        #continue
                    print("Use {} to link to\n{}\n#########################################".format(key, runningTests[key]))
                temp = digitPattern.search(input("Use the link number to report result for that. Use 'oops' to go back: "))
                while not temp:
                    temp = digitPattern.search(
                        input("Use the link number to report result for that. Use 'oops' to go back: "))
                if temp.group(0) == "oops":
                    continue
                if int(temp.group(0)) not in runningTests:
                    print("{} did not appear to be in the the active tests.".format(int(temp.group(0))))
                tested = runningTests.pop(int(temp.group(0)))
                result = ""
                while not result:
                    a = input("result (+ or -): ")
                    if posNegPattern.search(a):
                        result = posNegPattern.search(a).group(0)
                result = (result == "+")
                organ.results(tested, result)

            if nextTestPattern.search(action.lower()):
                next = organ.getNextTest()
                if next:
                    runningTests[runningTestNum] = next
                    runningTestNum += 1
            if warrantyPattern.search(action.lower()):
                print(warranty)
            if copyrightPattern.search(action.lower()):
                print("Tell 'em Thomas sent ya' and that he expect that ya'll won't keep him waitin' next time.\n"
                      "also any redistribution must contain the all copyright information.")
            if savePattern.search(action.lower()):
                print("Shutting down program...")
                # create a pickle file
                filename = ".\SavedStates\BatchOrganizer_Date_{}.pkl".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                picklefile = open(filename, 'wb+')
                saved = organ.saveAndRun()
                pickle.dump(saved, picklefile)
                picklefile.close()
                print("Save successful in {}".format(filename))
        except Exception as e:
            print("Unexpected error:", repr(e))
            continue

    print("Thank you, good bye.")

if __name__ == "__main__":
    main()
