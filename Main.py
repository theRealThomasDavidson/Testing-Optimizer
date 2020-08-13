import re
import Objects
import pickle
from datetime import datetime
import os
import json
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


def clearScreen():
    # for windows
    if os.name == 'nt':
        os.system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        os.system('clear')


def main():
    """

    :return:
    """
    running = True
    print(copyr)
    jasons = []
    for root, dirs, files in os.walk("."):
        path = root.split(os.sep)
        for file in files:
            if file.endswith(".json"):
                temp = os.path.join(root, file)
                jasons.append(temp)
    pickPattern = re.compile(r"(\d+|none)(?=\s*)")
    print("#########################################")
    for ndx in range(len(jasons)):
        # if runningTests[key]._status not in (1, 3):
        # continue
        print("#############Use {} to link to###########\n{}\n#########################################".format(ndx, jasons[ndx]))
    runningTests = {}
    runningTestNum = 0
    while True:
        temp = pickPattern.search(input("Use the link number to load that file. Use 'None' to start from scratch: "))
        while not temp:
            temp = pickPattern.search(
                input("Use the link number to report result for that. Use 'None' to start from scratch: "))

        if temp.group(0) == "none":
            print("Loading...")
            Objects.cases = [1, 2]
            organ = Objects.BatchTestingOrganizer()
            break

        elif int(temp.group(0)) >= len(jasons):
            print("{} did not appear to be in the the active tests.".format(int(temp.group(0))))
            continue
        else:
            print("Loading...")
            filename = jasons[int(temp.group(0))]
            data = open(filename, 'rb')
            restore = json.load(data)
            data.close()
            organ = Objects.BatchTestingOrganizer(restore=restore)
            for item in organ.individualStore._testing:
                runningTests[runningTestNum] = organ.individualStore._testing[item]
                runningTestNum +=1
            for item in organ.batchStore._testing:
                runningTests[runningTestNum] = organ.batchStore._testing[item]
                runningTestNum += 1
            break


                                                #cases with positives first then totoal pop our null is 50/50
                                                                #and becomes negligable after we have a lot of samples
    copyright_pattern = re.compile(r"(show c)\s*")
    warranty_pattern = re.compile(r"(show w)\s*")
    exit_pattern = re.compile(r"(exit|quit)\s*")                        # exit command
    prop_pattern = re.compile(r"(?<=prop:)\s*\d*\.\d+\s*")              # find batch size based on proportion
    add_pattern = re.compile(r"(?<=add pop:)\s*\d+\s+\d+\s*")           # add cases to population with positives first
                                                                        # then negatives
    new_case_pattern = re.compile(r"(?<=add patient)\s*")
    pop_pattern = re.compile(r"population\s*")
    batch_pattern = re.compile(r"batch size\s*")
    results_pattern = re.compile(r"(?<=test results)\s*")
    next_test_pattern = re.compile(r"get next(?=\s*)")
    pos_neg_pattern = re.compile(r"([+-])(?=\s*)")
    digit_pattern = re.compile(r"(\d+|oops)(?=\s*)")
    save_pattern = re.compile(r"(save)(?=\s*)")
    clear_pattern = re.compile(r"(clear)(?=\s*)")
    recall_pattern = re.compile(r"(oh no)(?=\s*)")
    comment_pattern = re.compile(r"#")
    print("Loading Done")
    while running:
        try:
            action = input("what action should we take? ")
            if comment_pattern.search(action.lower()):
                continue
            if exit_pattern.search(action.lower()):
                filename = ".\SavedStates\BatchOrganizer_Date_{}.json".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                saved = organ.shutdown()
                with open(filename, 'w+') as f:
                    json.dump(saved, f, indent=4)
                print("Save successful in {}".format(filename))
                running = False
                break

            if prop_pattern.search(action.lower()):
                number = prop_pattern.search(action.lower()).group(0)
                number = float(number)
                batchSizeOptimizer(number)      #just run for the print probably will fix this later
                continue

            if add_pattern.search(action.lower()):
                #print(add_pattern.search(action.lower()))
                numbers = add_pattern.search(action.lower()).group(0)
                pos, neg = [int(x) for x in numbers.split()]
                Objects.cases[0] += pos
                Objects.cases[1] += neg + pos
                batchSizeOptimizer((Objects.cases[0]/Objects.cases[1]))
                continue

            if pop_pattern.search(action.lower()):
                print("Positive cases: \t{}\nTotal tests:\t\t{}\nPositive percentage: \t{:.4f}%".format(
                    Objects.cases[0], Objects.cases[1], 100. * Objects.cases[0]/Objects.cases[1]))
                continue

            if batch_pattern.search(action.lower()):
                batchSizeOptimizer((Objects.cases[0] / Objects.cases[1]))
                continue

            if new_case_pattern.search(action.lower()):
                organ.new_id(input("Enter new Accession Number: "))
                continue

            if results_pattern.search(action.lower()):
                print("#########################################")
                for key in runningTests:
                    if runningTests[key]._status not in (1, 3):
                        continue
                    print("Use {} to link to\n{}\n#########################################".format(key, runningTests[key]))
                temp = digit_pattern.search(input("Use the link number to report result for that. Use 'oops' to go back: "))
                while not temp:
                    temp = digit_pattern.search(
                        input("Use the link number to report result for that. Use 'oops' to go back: "))
                if temp.group(0) == "oops":
                    continue
                if int(temp.group(0)) not in runningTests:
                    print("{} did not appear to be in the the active tests.".format(int(temp.group(0))))
                tested = runningTests.pop(int(temp.group(0)))
                result = ""
                while not result:
                    a = input("result (+ or -): ")
                    if pos_neg_pattern.search(a):
                        result = pos_neg_pattern.search(a).group(0)
                result = (result == "+")
                organ.results(tested, result)
                continue

            if next_test_pattern.search(action.lower()):
                next = organ.getNextTest()
                if next:
                    runningTests[runningTestNum] = next
                    runningTestNum += 1
                continue

            if warranty_pattern.search(action.lower()):
                print(warranty)
                continue

            if copyright_pattern.search(action.lower()):
                print("Tell 'em Thomas sent ya' and that he expect that ya'll won't keep him waitin' next time.\n"
                      "also any redistribution must contain the all copyright information.")
                continue

            if save_pattern.search(action.lower()):
                #print("Saving program state...")
                filename = ".\SavedStates\BatchOrganizer_Date_{}.json".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                saved = organ.saveAndRun()
                with open(filename, 'w+') as f:
                    json.dump(saved, f, indent=4)
                print("Save successful in {}".format(filename))
                continue

            if clear_pattern.search(action.lower()):
                clearScreen()
                continue

            if recall_pattern.search(action.lower()):
                oopsie = organ.recallRecent("local")

                print("#########################################")
                for ndx in range(len(oopsie)):
                    print("Use {} to link to\n{}\n#########################################".format(ndx, oopsie[ndx]))
                temp = None
                while not temp:
                    temp = digit_pattern.search(input("Use the link number to modify item. Use 'oops' to go back: "))
                if temp.group(0) == "oops":
                    continue
                if int(temp.group(0)) >= len(oopsie):
                    print("{} did not appear to be in the the modified bits.".format(int(temp.group(0))))
                tocorrect = oopsie[int(temp.group(0))]
                print("#######ITEM TO CHANGE########\n{}\n###############################".format(tocorrect))
                assay = None
                if isinstance(tocorrect, Objects.PatientID):
                    assay = input("enter correct Assention Number (or just press enter if correct): ")
                status = None
                while not status:
                    status = digit_pattern.search(input("""From this set\n\t{0: "Awaiting Batch Testing",
        1: "Awating Batch Results",
        2: "Awaiting Individual Testing",
        3: "Awaiting Individual Results",
        4: "Negative Result",
        5: "Positive Result"}\nEnter number for correct status or oops to go back or enter to skip:"""))
                    if assay:
                        break
                if status:
                    status = status.group(0)
                    if status == "oops":
                        continue
                    status = int(status)
                else:
                    status = None
                if status not in {0, 1, 2, 3, 4, 5, None}:
                    print("This status doesn't work for me dawg.")
                    continue
                if not assay:
                    assay = None

                organ.modifyItem(tocorrect, correctStatus=status, correnctNumber=assay)

                continue


        except Exception as e:
            print("Unexpected error:", repr(e))
            continue

    print("Thank you, good bye.")

if __name__ == "__main__":
    main()
