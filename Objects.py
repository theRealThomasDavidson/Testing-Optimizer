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
    if bt(a) >= 1.:
        return 1, 1.
    return a, bt(a)


class PatientID:
    """
    this object is designed to be the way we interact with an individual's data and store it's current status of testing

    self params
    :param num: a str this is a hashed identifier and is the most common ID to be used in methods display this as it's first
    8 characters for human readability
    :param name: a str or default None this is a string that I may use to store the name of the patient with any information needed to give \
    resutls to them
    :param status: an int default 0 will refer to the status according to this dictionary
    {0: "Awaiting Batch Testing",
    1: "Awating Batch Results",
    2: "Awaiting Individual Testing",
    3: "Awaiting Individual Results",
    4: "Negative Result",
    5: "Positive Result"}
    :param cases: this is a pointer to the list that records resolved cases it is used to increment when results are
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
        :param name: expects a string and will only use None if no name is specified,
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
        return "Start of ID #: \t\t{}\nAccession Number: \t{}\nTesting status: \t{}".format(str(self.num)[:8], str(self.name),
                                                                                    PatientID._statusRead[self._status])

    def save(self):
        return {
            "num": self.num,
            "name":self.name,
            "status": self._status
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
    :param running: a bool that acts as a flag to turn off the makeBatch threads when they are running
    :param cases: a list of 2 ints where the first is the number of positive samples you have received in the past and
        the second number is the total population of testing results
    :param feed: this is a semaphore to indicate when we sould check to see if batch testing is appropriate
    :param batchTest: this is the BatchStore object that we will pass our batches to
    :param retest: this is the IndividualStore object that we will be using for retesting PatientIDs that get
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
        :param cases: a list of 2 ints where the first is the number of positive samples you have received in the past and
            the second number is the total population of testing results
        :param feed: this is a semaphore to indicate when we should check to see if batch testing is appropriate
        :param ready: this is a semaphore to indicate when we should save the objects.
        :param batchTest: this is the BatchStore object that we will pass our batches to
        :param retest: this is the IndividualStore object that we will be using for retesting PatientIDs that get
            positive batch results
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
        self.running = True
        self.saveReady.release()

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
        raise TypeError("Only put individual PatientIDs into this Hopper object. The object added was of type: {}"\
                        .format(type(items)))

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
        temp = Batch(items, self.retest)
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
            raise TypeError("please use a object of type IndividualStore as retestQueue. used object is of type {}"\
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
            if self._status == None:
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
    :param _Q: this is a queue.Queue object that holds the main testing schedule
    :param _minorQ: this is a queue.Queue objec that holds the testing schedule accidents so they are still at the
            start of the schedule
    :param _testing: this is a dictionary with str as keys that associate with the hex based ID numbers of
            Batch objects. the values are the associated Batch objects or None. this is used to hold information
            about batches that are awaiting results.

    methods
    __init__(self): this is the initalizer and takes no arguments
    getNextTest(self): this is the method for getting the next Batch for individual testing
    put(self, items): this is a method for adding Batches to the batch testing queue either as Batch objects or
            as a list or tuple of Batch objects
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
        if restore:
            if not isinstance(retest, IndividualStore):
                raise TypeError("Cannot restore Batch store without a Restesting queue")
            for item in restore["items"]:
                self._Q.put(Batch(retest, restore=item))
            for item in restore["testing"]:
                self._testing[item] = Batch(retest, restore=restore["testing"][item])

    def save(self):
        items = []
        for _ in range(self._minorQ.qsize()):
            items.append(self._minorQ.get().save())
        for _ in range(self._Q.qsize()):
            items.append(self._Q.get().save())
        testingStorage = {}
        for item in self._testing:
            testingStorage[item] = self._testing[item].save()
        return {"items": items, "testing": testingStorage}

    def put(self, items):
        """
        this method adds items to the scheduler to be handled in order
        :param items: is a Batch type object or a tuple or list of Batch objects
        :return: None
        """
        if isinstance(items, Batch):
            if items._status not in (0,):
                ValueError("Patient cannot be put into individual testing schedule with status:\n{}".format(
                    IndividualStore._statusRead[items._status]))
            self._Q.put(items)
            return
        if isinstance(items, (tuple, list)):
            for item in items:
                self.put(item)
            return
        raise TypeError("Only put Batch objects into this BatchStore object. Added object was of type:\n{}"
                        .format(type(items)))

    def getNextTest(self):
        """
        this gets the next scheduled item from the queue
        :return: the next item from the scheduler, this item should be a Batch type object
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
            a.updateStatus(1)
            self._testing[a.num] = a
            return a

    def results(self, id, result):
        """
        This item handles when individuals receive test results. pushes further methods to handle the next steps in
        testing.
        :param item: a str that holds the Batch number or it is a Batch object that results have been found for.
        :param result: this is a bool that will be True when the results are positive and False when the results are
        negative.
        :return:
        """
        if isinstance(id, Batch):
            id = id.num
        if not isinstance(id, str):
            raise TypeError("The Identification used for results was not a recognized type.")
        if id not in self._testing:
            raise ValueError("The Identification used for results was not found in Batches waiting for results")
        if not self._testing[id]:
            raise ValueError("This Batch seems to already have results.")
        batch = self._testing.pop(id)
        batch.updateStatus(4 - 2 * result)


class IndividualStore:
    """
    this object will hold Patient ID#s from when they are assigned to be individually tested until they receive outcomes.

    self params:
    :param _Q: this is a queue.Queue object that holds the main testing schedule
    :param _minorQ: this is a queue.Queue objec that holds the testing schedule accidents so they are still at the
            start of the schedule
    :param _testing: this is a dictionary with str as keys that associate with the hex based ID numbers of
            PatientID objects. the values are the associated PatientID objects or None. this is used to hold information
            about patients that are awaiting results.

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
        testingStorage = {}
        for item in self._testing:
            testingStorage[item] = self._testing[item].save()
        return {"items": items, "testing": testingStorage}

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

    def results(self, id, result):
        """
        This item handles when individuals receive test results. pushes further methods to handle the next steps in
        testing.
        :param item: a str that holds the PatientID number or it is a PatientID object that results have been found for.
        :param result: this is a bool that will be True when the results are positive and False when the results are
        negative.
        :return:
        """
        if isinstance(id, PatientID):
            id = id.num
        if not isinstance(id, str):
            raise TypeError("The Identification used for results was not a recognized type.")
        if id not in self._testing:
            raise ValueError("The Identification used for results was not found in patients waiting for results")
        if not self._testing[id]:
            raise ValueError("This Patient seems to already have results.")
        patient = self._testing.pop(id)
        patient.updateStatus(4 + result)


class BatchTestingOrganizer:
    def __init__(self, restore=None):
        """
        this method will initialize all the objects we use to hold data in during the batch testing protocols it also
        starts any needed asynchronous threads.
        """
        self.running = True
        self.hopperFeed = threading.Semaphore()
        self.saveReady = threading.Semaphore()
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

    def newID(self, name):
        """
        this method adds a new PatientID to
        :param name: the name associated with the new Patient ID
        :return:
        """
        self.hopper.put(PatientID(name))
        self.hopperFeed.release()

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
            self.hopper.put(PatientID(restore=item))
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

    def getNextTest(self):
        """
        this method will return the next test to be put forward
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
            return self.batchStore.getNextTest()
        else:
            return self.individualStore.getNextTest()

    def results(self, id, result):
        """
        This item handles when individuals receive test results. pushes further methods to handle the next steps in
        testing.
        :param item: a str that holds the PatientID number or it is a PatientID object that results have been found for.
        :param result: this is a bool that will be True when the results are positive and False when the results are
        negative.
        :return:
        """
        if isinstance(id, PatientID):
            self.individualStore.results(id,result)
            return
        if isinstance(id, Batch):
            self.batchStore.results(id, result)
            return
        if not isinstance(id, str):
            raise TypeError("The Identification used for results was not a recognized type.")
        else:
            try:
                self.batchStore.results(id, result)
            except ValueError:
                self.individualStore.results(id, result)
            return



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