import hashlib
from time import time
from queue import Queue
import threading
import json
warranty = """
    This is the Batch Testing Organizer. it hopes to remove some of the logistical headaches of batch virus testing
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

copyr = """Testing Optimizer  Copyright (C) 2020  Thomas Davidson (davidson.thomasj@gmail.com)
    This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details."""

idNum = 0
cases = [1, 2]


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
    if 0 >= prop or prop >= 1:      # domain check: to be fair these should probably be
        raise ValueError("Math Domain Error: input should be between 0 and 1 used value was {}".format(prop))

    def batchtests(p, n): return (1/n) + (1 - (1 - p)**n)
    low, mid, high = 1, 1, 2

    def bt(x): return  batchtests(prop, x)

    while bt(mid) > bt(high) and bt(high) < 1:

        low = mid
        mid = high
        high *= 2
    if bt(mid) == 1.:
        return 1, 1.

    l, m1, m2, h = low, int(low + ((high - low) / 3)), int(low + (2*((high-low)/3))), high

    while l + 5 < h:
        if bt(m1) > bt(m2):
            l = m1
            m1, m2 = int(l + ((h-l)/3)), int(l + (2*((h-l)/3)))
            continue
        h = m2
        m1, m2 = int(l + ((h-l)/3)), int(l + (2*((h-l)/3)))
    a = sorted(list(range(l, h+1)), key=bt)[0]
    if bt(a) >= 1.:
        return 1, 1.
    return a, bt(a)


class PatientID:
    """
    this object is designed to be the way we interact with an individual's data and store it's current status of testing

    self params
    :param self.num: a str this is a hashed identifier and is the most common ID to be used in methods display this as it's first
    8 characters for human readability
    :param self.name: a str or default None this is a string that I may use to store the assension number
        of the patient
    :param self.status: an int default 0 will refer to the status according to this dictionary
    {0: "Awaiting Batch Testing",
    1: "Awating Batch Results",
    2: "Awaiting Individual Testing",
    3: "Awaiting Individual Results",
    4: "Negative Result",
    5: "Positive Result"}
    :param self.cases: this is a pointer to the list that records resolved cases it is used to increment when results are
    found

    methods
    def __init__(self, name=None, status=0)
    def __ str__ ()
    def updateStatus(self, newStatus)
    ##TODO: add method in updateStatus to report results once the patient has received a result (4 or 5)
    """
    i = 1
    _statusRead = {0: "Awaiting Batch Testing",
                   1: "Awating Batch Results",
                   2: "Awaiting Individual Testing",
                   3: "Awaiting Individual Results",
                   4: "Negative Result",
                   5: "Positive Result"
                   }
    _statusProgress = {0: (0, 1, 2),
                       1: (1, 2, 4),
                       2: (2, 3),
                       3: (3, 4, 5)
                       }

    def __init__(self, accession_number=None, status=0, restore=None):
        """
        this method initializes the PatientID Object
        :param accession_number: expects a string and will only use None if no name is specified,
        :param status: an int default 0 will refer to the status according to this dictionary
        {0: "Awaiting Batch Testing",
        1: "Awating Batch Results",
        2: "Awaiting Individual Testing",
        3: "Awaiting Individual Results",
        4: "Negative Result",
        5: "Positive Result"}
        """
        global idNum
        if not isinstance(idNum, int):
            idNum = -342
        idNum += 1
        if restore:
            self.restore(restore)
            return
        self.num = hashlib.sha256( (str(time()) + str(idNum)).encode() ).hexdigest()
        self.name = accession_number
        self._status = status

    def __str__(self):
        return "Start of ID #: \t\t{}\nAccession Number: \t{}\nTesting status: \t{}".format(
            str(self.num)[:8], str(self.name), PatientID._statusRead[self._status])

    def save(self):
        return {
            "num":      self.num,
            "name":     self.name,
            "status":   self._status
        }

    def restore(self, info):
        self.num = info["num"]
        self.name = info["name"]
        self._status = info["status"]

    def updateStatus(self, newStatus):
        """
        this method modifies the internal status of a PatientID to the new Status
        :param newStatus: an int that will refer to the status according to this dictionary
        {0: "Awaiting Batch Testing",
        1: "Awating Batch Results",
        2: "Awaiting Individual Testing",
        3: "Awaiting Individual Results",
        4: "Negative Result",
        5: "Positive Result"}
        :return:
        """
        if self._status not in PatientID._statusProgress:
            if self._status == newStatus:
                return
            raise ValueError("This patient has already received an outcome. This was: {}".format(
                PatientID._statusRead[self._status]))
        if newStatus not in PatientID._statusProgress[self._status]:
            raise ValueError("This patient is at the stage: {} and cannot move directly to {}".format(
                PatientID._statusRead[self._status], PatientID._statusRead[newStatus]))
        self._status = newStatus
        if self._status == 4 or self._status == 5:
            global cases
            cases[1] += 1
            cases[0] += (self._status == 5)
            print("##########PATIENT RESULTS##########")
            print("Ready to send back {} for :\n{}".format(PatientID._statusRead[self._status], self))
            print("###################################")


class Hopper:
    """
    this object will hold individual Patient ID # before they are assigned a batch to be in
    we want to use a buffer queue style for prioritizing First In First Out

    self params
    :param self._Q: a queue.Queue that holds individuals to be added to a Batch
    :param self.running: a bool that acts as a flag to turn off the makeBatch threads when they are running
    :param self.cases: a list of 2 ints where the first is the number of positive samples you have received in the past
        and the second number is the total population of testing results
    :param self.feed: this is a semaphore to indicate when we sould check to see if batch testing is appropriate
    :param self.batchTest: this is the BatchStore object that we will pass our batches to
    :param self.retest: this is the IndividualStore object that we will be using for retesting PatientIDs that get
        positive batch results

    methods
    def __init__(self, cases):
        this
    def shutdown(self):
    def put(self, items):
    def def makeBatch(self, feed, batchTest, retest):
    """
    _statusRead = {0: "Awaiting Batch Testing",
                   1: "Awating Batch Results",
                   2: "Awaiting Individual Testing",
                   3: "Awaiting Individual Results",
                   4: "Negative Result",
                   5: "Positive Result"
                   }

    def __init__(self, feed, ready, batchTest, retest, restore=None):
        """
        this method initializes the class and identifies the objects it will send item to.
        :param feed: this is a semaphore that will direct the hopper to check to see if it can push out a new batch
        :param ready: this is a semaphore to indicate when we should save the objects.
        :param batchTest: this is the BatchStore object that we will pass our batches to
        :param retest: this is the IndividualStore object that we will be using for retesting PatientIDs that get
            positive batch results
        :param restore: this is a dictionary that allows us to unserialize data for the hopper object
        """
        self.feed = feed
        self.saveReady = ready
        self.batchTest = batchTest
        self.retest = retest
        self._Q = Queue()
        self.running = True
        if restore:
            for item in restore["items"]:
                self.put(PatientID(restore=item), fromSave=True)

    def shutdown(self):
        """
        this shuts down the makeBatch command
        :return:
        """
        self.running = False
        self.feed.release()

    def restart(self):
        """
        this is used by the handler of this object to spin while the object itself is saving. used when you want to
        restart this object after you have called shutdown.
        :return:
        """
        self.running = True
        self.saveReady.release()
        threading.Thread(target=self.makeBatch).start()

    def save(self):
        items = []
        for _ in range(self._Q.qsize()):
            items.append(self._Q.get().save())
        return {"items": items}

    def put(self, items, fromSave=False):
        """
        this method adds items to the scheduler to be handled in order
        :param items: is a PatientID type object or a tuple or list of PatientID objects
        :param fromSave: this is a bool that will describe if this put is loading from a save state. and will not print
            to console as if it was new.
        :return: None
        """
        if isinstance(items, PatientID):
            if items._status not in (0,):
                ValueError("Patient cannot be put into batch testing schedule with status:\n {}".format(
                    Hopper._statusRead[items._status]))
            self._Q.put(items)
            if not fromSave:
                print("############NEW PATIENT############")
                print(items)
                print("###################################")
            return
        if isinstance(items, (tuple, list)):
            for item in items:
                self.put(item, fromSave=fromSave)
            return
        raise TypeError("Only put individual PatientIDs into this Hopper object. The object added was of type: {}"
                        .format(type(items)))

    def remove(self, item):
        """
        this is a method for removing items in the hopper it identifies if an item is removed so we know if it passed to
        the batch store
        :param item: this is a PatientID that is the item that should be removed.
        :return: a bool that returns true if the item was removed and false if it was not.
        """
        tempQ = Queue()
        found = False
        while not self._Q.empty():
            temp = self._Q.get()
            if temp is not item:
                tempQ.put(temp)
            else:
                found = True
                break
        while not tempQ.empty():
            self.put(tempQ.get(), fromSave=True)
        return found

    def lastBatch(self):
        """
        this will be a method run when all batches and individual tests are done so that we can clear any remaining
        patients
        :return:
        """
        size = self._Q.qsize()
        global cases
        bsize = batchSizeOptimizer(cases[0]/cases[1])[0]
        for _ in range(size//bsize):
            items = []
            for __ in range(bsize):
                items.append(self._Q.get())
            temp = Batch(items, self.retest)
            self.batchTest.put(temp)
        if self._Q.empty():
            return
        size = self._Q.qsize()
        if size == 1:
            item = self._Q.get()
            item.updateStatus(2)
            self.retest.put(item)
        items = []
        for _ in range(size):
            items.append(self._Q.get())
        temp = Batch(self.retest, items=items)
        self.batchTest.put(temp)



    def makeBatch(self):
        """
        this will be a method run with it's own thread that will automatically add items to the
        :return:
        """
        while self.running:
            size = self._Q.qsize()
            global cases
            bsize = batchSizeOptimizer(cases[0]/cases[1])[0]
            for _ in range(size//bsize):
                items = []
                for __ in range(bsize):
                    items.append(self._Q.get())
                if len(items) > 1:
                    temp = Batch(self.retest, items=items)
                    self.batchTest.put(temp)
                elif len(items) == 1:
                    self.retest.put(items[0])
            self.feed.acquire()
        self.saveReady.release()


class Batch:
    """
    this object will hold sets of Patient IDs from when they are assigned a Batch from the hopper until they have
    received a batch testing result.

    self params:
    :param  self.items: a tuple with all elements of class PatientID these are the elements that are to be used together.
    :param self._status: this is a int that describes the status of all of the patients in the batch it is associated with
    the dict
    {   0: "Awaiting Batch Testing",
        1: "Awating Batch Results",
        2: "Awaiting Individual Testing",
        3: "Awaiting Individual Results",
        4: "Negative Result",
        5: "Positive Result"
        }
    :param self._retest: object of type IndividualStore that we pass our items for resting to.

    methods
    __init__(self, items, retestQueue): this is the initializer and takes a tuple of PatientIDs as the items argument
    and makes a batch with these IDs and an IndividualStore as the RetestQueue.
    updateStatus(self, newStatus): this is the recommended method for changing status of the batch and the
        Patient IDs in the batch newStatus is an int associated with the new status.

    """
    _statusProgress = {0: (0, 1, 2),
                       1: (1, 2, 4),
                       2: (2, 3),
                       3: (3, 4, 5)
                       }
    _statusRead = {0: "Awaiting Batch Testing",
                   1: "Awating Batch Results",
                   2: "Awaiting Individual Testing",
                   3: "Awaiting Individual Results",
                   4: "Negative Result",
                   5: "Positive Result"
                   }

    def __init__(self, retestQueue, items=None, restore=None):
        """
        this initializes the batch and inputs all the items.
        :param items: a tuple with all elements of class PatientID these are the elements that are to be used together.
        """
        if not isinstance(retestQueue, IndividualStore):
            raise TypeError("please use a object of type IndividualStore as retestQueue. used object is of type {}"
                            .format(type(retestQueue)))
        self._retest = retestQueue
        if restore:
            self.num = restore["num"]
            self._status = restore["status"]
            self.items = []
            for item in restore["items"]:
                self.items.append(PatientID(restore=item))
            return

        global idNum
        if not isinstance(idNum, int):
            idNum = -342
        idNum += 1
        if not items:
            raise ValueError("No items were added to a new batch")
        self.num = hashlib.sha256((str(time()) + str(idNum)).encode() ).hexdigest()
        self.items = items
        self._status = None

        if not isinstance(items, (tuple, list)):
            raise TypeError("Batch tried to initialize with a non iterable type. Instead useing type:{}".format(
                type(items)))
        for item in items:
            if not isinstance(item, PatientID):
                raise TypeError("Items in list passed to Batch not PatientID. Instead used type: {}".format(
                    type(item)))
            if item._status == 4 or item._status == 5:
                raise ValueError("Resolved case was passed to Batch")
            if self._status is None:
                self._status = item._status
            else:
                if item._status != self._status:
                    raise ValueError("Batch was made with IDs not at the same stage")

    def __str__(self):
        members = ""
        for item in self.items:
            members += "\t\t{}\n".format(item.name)
        members = "Members: " + members[1:-1]
        return "Start of Batch ID #: \t{}\nSize: \t\t\t{}\nTesting status: \t{}\n"\
            .format(str(self.num)[:8], str(len(self.items)), PatientID._statusRead[self._status]) + members

    def save(self):
        items = []
        for item in self.items:
            items.append(item.save())
        return {
            "num": self.num,
            "status": self._status,
            "items": items
        }

    def updateStatus(self, newStatus):
        """
        this method modifies the internal status of a PatientID to the new Status
        :param newStatus: an int that will refer to the status according to this dictionary
        {0: "Awaiting Batch Testing",
        1: "Awating Batch Results",
        2: "Awaiting Individual Testing",
        3: "Awaiting Individual Results",
        4: "Negative Result",
        5: "Positive Result"}
        :return:
        """
        if self._status not in Batch._statusProgress:
            raise ValueError("This patient has Already received an outcome. This was: {}".format(
                Batch._statusRead[self._status]))
        if newStatus not in Batch._statusProgress[self._status]:
            raise ValueError("This Patient is at the stage: {} and cannot move directly to {}".format(
                Batch._statusRead[self._status], Batch._statusRead[newStatus]))
        self._status = newStatus
        for item in self.items:
            item.updateStatus(newStatus)
        if newStatus == 2:              #moving on to individual testing
            self._retest.put(self.items)


class BatchStore:
    """
    This object will hold batches while from when they are formed until they have outcomes.

    self params:
    :param self._Q: this is a queue.Queue object that holds the main testing schedule
    :param self._minorQ: this is a queue.Queue objec that holds the testing schedule accidents so they are still at the
            start of the schedule
    :param self,_testing: this is a dictionary with str as keys that associate with the hex based ID numbers of
            Batch objects. the values are the associated Batch objects or None. this is used to hold information
            about batches that are awaiting results.
    :param self._qlock: this is a blocking object to keep us from inputing objects into the queue when internal work is
        being done on the queue
    methods
    results(self, id, result): this is a method for reporting results to a Batch that have been tested and allows the
            Batch to forward itself as is appropriate.
    """
    _statusRead = {0: "Awaiting Batch Testing",
                   1: "Awating Batch Results",
                   2: "Awaiting Individual Testing",
                   3: "Awaiting Individual Results",
                   4: "Negative Result",
                   5: "Positive Result"
                   }

    def __init__(self, restore=None,retest=None):
        self._Q = Queue()
        self._minorQ = Queue()
        self._testing = {}
        self._qlock = threading.Lock()
        if restore:
            if not isinstance(retest, IndividualStore):
                raise TypeError("Cannot restore Batch store without a Restesting queue")
            for item in restore["items"]:
                self._qlock.acquire()
                self._Q.put(Batch(retest, restore=item))
                self._qlock.release()
            for item in restore["testing"]:
                self._testing[item] = Batch(retest, restore=restore["testing"][item])

    def save(self):
        items = []
        for _ in range(self._minorQ.qsize()):
            items.append(self._minorQ.get().save())
        for _ in range(self._Q.qsize()):
            items.append(self._Q.get().save())
        testing_storage = {}
        for item in self._testing:
            testing_storage[item] = self._testing[item].save()
        return {"items": items, "testing": testing_storage}

    def put(self, items):
        """
        this method adds items to the scheduler to be handled in order
        :param items: is a Batch type object or a tuple or list of Batch objects
        :return: None
        """

        if isinstance(items, Batch):
            if items._status not in {0, }:
                ValueError("Patient cannot be put into individual testing schedule with status:\n{}".format(
                    IndividualStore._statusRead[items._status]))
            self._qlock.acquire()
            self._Q.put(items)
            self._qlock.release()
            return

        if isinstance(items, (tuple, list)):
            for item in items:
                self.put(item)
            return
        raise TypeError("Only put Batch objects into this BatchStore object. Added object was of type:\n{}"
                        .format(type(items)))

    def put_on_top(self, item):
        """
        this is for emergency use to put an item back into the queue when it was mistakenly pull early
        :param item: this is the item to be put back into the queue
        :return: None
        """
        if isinstance(item, Batch):
            if item._status not in {0, }:
                item._status = 0
            self._qlock.acquire()
            self._minorQ.put(item)
            self._qlock.release()
            return
        raise TypeError("Only put Batch objects into this BatchStore object. Added object was of type: {}"
                        .format(type(item)))

    def getNextTest(self):
        """
        this gets the next scheduled item from the queue
        :return: the next item from the scheduler, this item should be a Batch type object
        """
        self._qlock.acquire()
        if self._minorQ.empty():
            a = self._Q.get()
        else:
            a = self._minorQ.get()
        res = ""
        while not (res == "Y" or res == "y" or res == "N" or res == "n"):
            res = input("Sample is:\n{}\nIs this sample ready to test(y/n): ".format(a))
        if res == "N" or res == "n":
            print("Sample:\n{}\nIs being added back into testing queue. ".format(a))
            self._minorQ.put(a)
            self._qlock.release()
            return
        if res == "Y" or res == "y":
            a.updateStatus(1)
            self._testing[a.num] = a
            self._qlock.release()
            return a
        self._qlock.release()

    def results(self, bat, result):
        """
        This item handles when individuals receive test results. pushes further methods to handle the next steps in
        testing.
        :param bat: a str that holds the Batch number or it is a Batch object that results have been found for.
        :param result: this is a bool that will be True when the results are positive and False when the results are
        negative.
        :return:
        """
        if isinstance(bat, Batch):
            bat = bat.num
        if not isinstance(bat, str):
            raise TypeError("The Identification used for results was not a recognized type.")
        if bat not in self._testing:
            raise ValueError("The Identification used for results was not found in Batches waiting for results")
        if not self._testing[bat]:
            raise ValueError("This Batch seems to already have results.")
        batch = self._testing.pop(bat)
        batch.updateStatus(4 - 2 * result)
        return batch

    def remove_q_items(self, items, hopper=None):
        """
        this method is intended to allow for an item to be pulled from the self._Q if it was put in accidentally
        :param items: this is the items to be removed it should be either a PatientID object to be removed and if
            possible replaced in it's batch or it is a Batch in which case it is simply removed fro the queue.
        :param hopper: this is a Hopper object that can offer replacement PatientIDs in case one is removed from a batch.
        :return: None
        """
        self._qlock.acquire()
        if isinstance(items, Batch):
            while not self._Q.empty():
                temp = self._Q.get()
                if temp is items:
                    self._minorQ.put(temp)
            while not self._minorQ.empty():
                self._Q.put(self._minorQ.get())
        if isinstance(items, PatientID):
            tempQ = Queue()
            while not self._Q.empty() or not self._minorQ.empty():
                if not self._minorQ.empty():
                    temp = self._minorQ.get()
                else:
                    temp = self._Q.get()
                for ndx in range(len(temp.items)):
                    if items is temp.items[ndx]:
                        replace = False
                        if hopper:
                            if not hopper._Q.empty():
                                temp.items[ndx] = hopper._Q.get()
                                replace = True
                        if not replace:
                            temp.items = temp.items[:ndx] + temp.items[ndx + 1:]
                tempQ.put(temp)
            while not tempQ.empty():
                self._Q.put(tempQ.get())

        self._qlock.release()

        return


class IndividualStore:
    """
    this object will hold Patient ID#s from when they are assigned to be individually tested until they receive outcomes

    self params:
    :param self._Q: this is a queue.Queue object that holds the main testing schedule
    :param self._minorQ: this is a queue.Queue objec that holds the testing schedule accidents so they are still at the
            start of the schedule
    :param self._testing: this is a dictionary with str as keys that associate with the hex based ID numbers of
            PatientID objects. the values are the associated PatientID objects or None. this is used to hold information
            about patients that are awaiting results.
    :param self._qlock: this is a blocking object to keep us from inputing objects into the queue when internal work is
        being done on the queue
    methods
    __init__(self): this is the initalizer and takes no arguments
    getNextTest(self): this is the method for getting the next patientID for individual testing
    put(self, items): this is a method for adding patients to the individual testing queue either as patient objects or
            as a list or tuple of patient objects
    results(self, id, result): this is a method for reporting results to individuals that have been individually tested.
    """
    _statusRead = {0: "Awaiting Batch Testing",
                   1: "Awating Batch Results",
                   2: "Awaiting Individual Testing",
                   3: "Awaiting Individual Results",
                   4: "Negative Result",
                   5: "Positive Result"
                   }

    def __init__(self, restore=None):
        self._Q = Queue()
        self._minorQ = Queue()
        self._testing = {}
        self._qlock = threading.Lock()
        if restore:
            for item in restore["items"]:
                self._Q.put(PatientID(restore=item))
            for item in restore["testing"]:
                self._testing[item] = PatientID(restore=restore["testing"][item])

    def save(self):
        items = []
        for _ in range(self._minorQ.qsize()):
            items.append(self._minorQ.get().save())
        for _ in range(self._Q.qsize()):
            items.append(self._Q.get().save())
        testing_storage = {}
        for item in self._testing:
            testing_storage[item] = self._testing[item].save()
        return {"items": items, "testing": testing_storage}

    def getNextTest(self):
        """
        this gets the next scheduled item from the queue
        :return: the next item from the scheduler, this item should be a PatientID type object
        """
        if self._minorQ.empty():
            a = self._Q.get()
        else:
            a = self._minorQ.get()
        res = ""
        while not (res == "Y" or res == "y" or res == "N" or res == "n"):
            res = input("Sample is:\n{}\nIs this sample ready to test(y/n): ".format(a))
        if res == "N" or res == "n":
            print("Sample:\n{}\nIs being added back into testing queue. ".format(a))
            self._minorQ.put(a)
            return
        if res == "Y" or res == "y":
            a.updateStatus(3)
            self._testing[a.num] = a
            return a

    def put(self, items):
        """
        this method adds items to the scheduler to be handled in order
        :param items: is a PatientID type object or a tuple or list of PatientID objects
        :return: None
        """
        if isinstance(items, PatientID):
            if items._status not in (0, 1, 2):
                ValueError("Patient cannot be put into individual testing schedule with status:\n {}".format(
                    IndividualStore._statusRead[items._status]))
            items.updateStatus(2)
            self._Q.put(items)
            return
        if isinstance(items, (tuple, list)):
            for item in items:
                self.put(item)
            return
        raise TypeError("only put individual PatientIDs into this IndividualStore object")

    def put_on_top(self, item):
        """
        this is for emergency use to put an item back into the queue when it was mistakenly pull early
        :param item: this is a PatientID object the item to be put back into the queue
        :return: None
        """
        if isinstance(item, PatientID):
            if item._status is not 2:
                item._status = 2
            self._qlock.acquire()
            self._minorQ.put(item)
            self._qlock.release()
            return
        raise TypeError("Only put PatientID objects into this IndividualStore object. Added object was of type: {}"
                        .format(type(item)))

    def results(self, pat, result):
        """
        This item handles when individuals receive test results. pushes further methods to handle the next steps in
        testing.
        :param pat: a str that holds the PatientID number or it is a PatientID object that results have been found for.
        :param result: this is a bool that will be True when the results are positive and False when the results are
        negative.
        :return:
        """
        if isinstance(pat, PatientID):
            pat = pat.num
        if not isinstance(pat, str):
            raise TypeError("The Identification used for results was not a recognized type.")
        if pat not in self._testing:
            raise ValueError("The Identification used for results was not found in patients waiting for results")
        if not self._testing[pat]:
            raise ValueError("This Patient seems to already have results.")
        patient = self._testing.pop(pat)
        patient.updateStatus(4 + result)
        return patient

    def remove_q_item(self, items):
        """
        this method is intended to allow for an item to be pulled from the self._Q if it was put in accidentally
        :param items: this is the items to be removed it should be either a PatientID object or an iterable of PatientID
                    objects, preferably sets. if this item does not match any items in the queue it will not remove
                    any items.
        :return: None
        """
        self._qlock.acquire()
        temp = {True: lambda a, b: a is b,
                False: lambda a, b: a in b}
        cond = temp[isinstance(items, PatientID)]
        while not self._Q.empty():
            temp = self._Q.get()
            if cond(temp, items):
                self._minorQ.put(temp)
        while not self._minorQ.empty():
            self._Q.put(self._minorQ.get())

        self._qlock.release()

        return


class BatchTestingOrganizer:
    def __init__(self, restore=None):
        """
        this method will initialize all the objects we use to hold data in during the batch testing protocols it also
        starts any needed asynchronous threads.
        """
        self.running = True
        self.hopperFeed = threading.Semaphore()
        self.saveReady = threading.Semaphore()
        self._recent = {}
        if not restore:
            self.individualStore = IndividualStore()
            self.batchStore = BatchStore()
            self.hopper = Hopper(self.hopperFeed, self.saveReady, self.batchStore, self.individualStore)
        else:
            self.individualStore = IndividualStore(restore=restore["Istore"])
            self.batchStore = BatchStore(restore=restore["Bstore"], retest=self.individualStore)
            self.hopper = Hopper(self.hopperFeed, self.saveReady, self.batchStore, self.individualStore, restore=restore["hopper"])
            global cases
            cases = restore["cases"]
        threading.Thread(target=self.hopper.makeBatch).start()

    def new_id(self, name, client="local"):
        """
        this method adds a new PatientID to
        :param name: the name associated with the new Patient ID
        :param client: a str that represents the name of the requesting party this should usually be a unique hash
            generated by username or by time with hash
        :return:
        """
        patient = PatientID(name)
        self.hopper.put(patient)
        self.hopperFeed.release()
        self.putRecent(patient, client=client)

    def save(self):
        return{
            "cases" : cases,
            "hopper": self.hopper.save(),
            "Istore": self.individualStore.save(),
            "Bstore": self.batchStore.save()
        }

    def saveAndRun(self):
        """
        this funtion should save the project while keeping the objects running.
        :return: a save object
        """
        print("Saving...")
        self.hopper.shutdown()      #shutd downt he makeBatch thread
        self.saveReady.acquire()
        state = self.save()
        self.hopper.restart()
        self.saveReady.acquire()
        for item in state["Istore"]["items"]:
            self.individualStore.put(PatientID(restore=item))
        for item in state["Bstore"]["items"]:
            self.batchStore.put(Batch(self.individualStore, restore=item))
        for item in state["hopper"]["items"]:
            self.hopper.put(PatientID(restore=item), fromSave=True)
        return state

    def shutdown(self):
        """
        this should safely shut down all threads starting with new information threads then processing
        threads in other objects and lastly processing threads in this object when all is done we will
        save objects as pickles
        :return:
        """
        print("Saving and Shutting down...")
        self.hopper.shutdown()      #shutd downt he makeBatch thread
        self.running = False
        self.saveReady.acquire()
        return self.save()

    def getNextTest(self, client="local"):
        """
        this method will return the next test to be put forward
        :param client: a str that represents the name of the requesting party this should usually be a unique hash
            generated by username or by time with hash
        :return: a Batch or PatientID associated with the next Test to be preformed
        """
        iSize = self.individualStore._Q.qsize() + self.individualStore._minorQ.qsize()
        bSize = self.batchStore._Q.qsize() + self.batchStore._minorQ.qsize()
        if iSize + bSize == 0:
            self.hopper.lastBatch()
            iSize = self.individualStore._Q.qsize() + self.individualStore._minorQ.qsize()
            bSize = self.batchStore._Q.qsize() + self.batchStore._minorQ.qsize()
            if iSize + bSize == 0:
                print("All samples are being tested.")
                return None

        if bSize >= iSize:
            item = self.batchStore.getNextTest()

        else:
            item = self.individualStore.getNextTest()
        self.putRecent(item, client)
        return item

    def results(self, item, result, client="local"):
        """
        This item handles when individuals receive test results. pushes further methods to handle the next steps in
        testing.
        :param item: a str that holds the (PatientID/Batch) number or it is a (PatientID/Batch) object that results
                have been found for.or a
        :param result: this is a bool that will be True when the results are positive and False when the results are
                negative.
        :param client: this is a string of the hash of the client that is accessing this command
        :return: None
        """
        if isinstance(item, PatientID):
            self.putRecent(item, client)
            self.individualStore.results(id, result)
            return
        if isinstance(item, Batch):
            self.putRecent(item, client)
            self.batchStore.results(id, result)
            return
        if not isinstance(item, str):
            raise TypeError("The Identification used for results was not a recognized type.")
        else:
            try:
                temp = self.batchStore.results(item, result)
                self.putRecent(temp, client)
            except ValueError:
                temp = self.individualStore.results(item, result)
                self.putRecent(temp, client)
            return

    def putRecent(self, item, client):
        if client not in self._recent:
            self._recent[client] = []
        self._recent[client].append(item)
        self._recent[client][-5:]

    def recallRecent(self, client):
        return self._recent[client][:]

    def modifyItem(self, item, correctStatus=None, correnctNumber=None):
        """
        this method will take an item from one part of the program and correct it's classification and move it to the
        object that should have proper control of it.
        :param item: this is an item  of type Batch or PatientID that is to be reclassified
        :param correctStatus: this is and int corresponding to the status that that item should take according to the
            below dictionary.
           {0: "Awaiting Batch Testing",
            1: "Awaiting Batch Results",
            2: "Awaiting Individual Testing",
            3: "Awaiting Individual Results",
            4: "Negative Result",
            5: "Positive Result"}
        :param correctNumber: this is a string corresponding to a correction of the Assention number if it was entered
            incorrectly
        :return: this will return the modified item
        """

        # comments are pretty liberal here to allow for more readability,
        if item._status is correctStatus:
            return
        if isinstance(item, Batch):
            if correctStatus in {3, 5}:
                raise ValueError("Batches cannot be modified to the value {}".format(
                    IndividualStore._statusRead[correctStatus]))
            oldStatus = item._status
            item._status = correctStatus

            for pat in item.items:
                pat._status = correctStatus

            if oldStatus is 0:
                # each item is in the batchStore Queue Idk how this would be called
                self.batchStore.remove_q_item(item)

            if oldStatus is 1:
                # batch is in batch store waiting area
                self.batchStore._testing.pop(item.num)

            if oldStatus is 2:
                # each item is in the queue for individual store
                self.individualStore.remove_q_items(set(item.items))

            if oldStatus is 4:
                # each item is popped off in negative result bit so we need to amend that area instead of
                #  changing any internal data
                pass

            if correctStatus is 0:
                self.batchStore.put_on_top(item)

            if correctStatus is 1:
                self.batchStore._testing[item.num] = item

            if correctStatus in {2, 4}:
                item._status = 1
                for pat in item.items:
                    pat._status = 1
                self.batchStore._testing[item.num] = item
                self.batchStore.results(item.num, (correctStatus == 2))
            return item

        if isinstance(item, PatientID):
            if correctStatus in {1, }:
                raise ValueError("Batches cannot be modified to the value {}".format(
                    IndividualStore._statusRead[correctStatus]))

            if correnctNumber:
                item.name = correnctNumber

            if correctStatus is not None:
                oldStatus = item._status
                item._status = correctStatus
                if oldStatus is 0:
                    #could be in hopper or in batch
                    if not self.hopper.remove(item):
                        self.batchStore.remove_q_items(item, hopper=self.hopper)
                if oldStatus is 1:

                    # HACK
                    # DO NOT USE THIS CODE AS A REFERENCE TO HOW THIS PROJECT IS TO BE WRITTEN THIS CODE SHOULD BE UNDER REVIEW UPON
                    # FIRST REFACTOR
                    #awating batch test results
                    for key in self.batchStore._testing:
                        for ndx in range(len(self.batchStore._testing[key].items)):
                            if self.batchStore._testing[key].items[ndx] is item:
                                self.batchStore._testing[key].items = self.batchStore._testing[key].items[:ndx] + \
                                                        self.batchStore._testing[key].items[ndx + 1:]
                                break

                if oldStatus is 2:
                    # one item in individual test queue
                    self.individualStore.remove_q_item(item)

                if oldStatus is 3:
                    #in the testing dictionary in individualstore
                    self.individualStore._testing.pop(item.num)

                if oldStatus in {4, 5}:
                    # each item is popped off in negative or positive result bit so we need to amend that area
                    #       instead of changing any internal data
                    pass

                if correctStatus is 0:
                    self.hopper.put(item, fromSave=True)

                if correctStatus is 2:
                    self.individualStore._minorQ.put(item)

                if correctStatus is 3:
                    self.individualStore._testing[item.num] = item

                if correctStatus in {4, 5}:
                    item._status = 3
                    self.individualStore._testing[item.num] = item
                    self.individualStore.results(item.num, (correctStatus is 5))

            return item


def testing():
    print(copyr)
    print("this environment is meant for testing and is not expected to have compatibility with the"
          " show c and show w commands. running main will allow for these functions.")
    global cases
    organ = BatchTestingOrganizer()
    cases = [40, 390]
    names = [
        "alice",
        "bob",
        "carol",
        "dennis",
        "eloise",
        "franklin",
        "greg",
        "hannah",
        "irene",
        "james",
        "kim",
        "louis",
        "mary",
        "nicole",
        "ogden",
        "pearl",
        "quinton",
        "rachael",
        "steven",
        "tanya",
        "urkel",
        "vince",
        "will",
        "xander",
        "yolanda",
        "zander"
    ]
    for name in names:
        print("add patient\n{}".format(name))
    organ.shutdown()
    return
    print("size of the queue is :", organ.batchStore._Q.qsize())
    ID1 = organ.getNextTest()
    ID1 = ID1.num
    ID2 = organ.getNextTest()
    ID2 = ID2.num
    ID3 = organ.getNextTest()

    print("cases before any results:", cases)
    organ.batchStore.results(ID1, False)
    print("cases after negative batch:", cases)
    organ.batchStore.results(ID2, True)
    print("cases after positive batch:", cases)
    print("Individual queue after positive:", organ.individualStore._Q.qsize())

    ID4 = organ.getNextTest()
    ID5 = organ.getNextTest()
    ID6 = organ.getNextTest()

    print(ID1)
    print(ID2)
    print(ID3)
    print(ID4)
    print(ID5)
    print(ID6)

    print("size of individual queue after 1 pop is :", organ.batchStore._Q.qsize())


    organ.shutdown()


    """
    a, b, c, d, e = PatientID(), PatientID(), PatientID(), PatientID(), PatientID()
    store = IndividualStore()
    print(a)
    bat = Batch((a, b, c, d, e), store)
    print(bat)
    bat.updateStatus(1)
    print(bat)
    print(a)
    bat.updateStatus(2)

    aNum = a.num
    dNum = d.num
    print("######################################\n")

    store.getNextTest()
    store.getNextTest()
    store.getNextTest()
    store.getNextTest()
    store.getNextTest()
    print(store._testing)
    print("######################################\n")
    print(a, "\n")
    print(b, "\n")
    print(c, "\n")
    print(d, "\n")
    print(e, "\n")
    print("######################################\n")
    store.results(aNum, False)
    print("results for negative: \n", a)
    store.results(b, True)
    print("results for positive: \n", b)
    print("\n######################################\n")
    print(store._testing)
    store.results(d, False)
    print(d)

    print(store._testing)"""





if  __name__ == "__main__":
    testing()