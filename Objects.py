import hashlib
from time import time
from queue import Queue

idNum = 0


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

    methods
    def __init__(self, name=None, status=0)
    def __ str__ ()
    def updateStatus(self, newStatus)
    ##TODO: add method to report results once the patient has received a result
    """
    i = 1
    _statusRead = {0: "Awaiting Batch Testing",
                   1: "Awating Batch Results",
                   2: "Awaiting Individual Testing",
                   3: "Awaiting Individual Results",
                   4: "Negative Result",
                   5: "Positive Result"
                   }
    _statusProgress = {0: (1, 2),
                       1: (2, 4),
                       2: (3,),
                       3: (4, 5)
                       }

    def __init__(self, name=None, status=0):
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
        idNum += 1
        self.num = hashlib.sha256((str(time()) + str(idNum)).encode() ).hexdigest()
        self.name = name
        self._status = status

    def __str__(self):
        return "Start of ID #: \t\t{}\nName: \t\t\t{}\nTesting status: \t{}".format(str(self.num)[:8], str(self.name),
                                                                                    PatientID._statusRead[self._status])

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
            raise ValueError("This patient has Already received an outcome. This was: {}".format(
                PatientID._statusRead[self._status]))
        if newStatus not in PatientID._statusProgress[self._status]:
            raise ValueError("This Patient is at the stage: {} and cannot move directly to {}".format(
                PatientID._statusRead[self._status], PatientID._statusRead[newStatus]))
        self._status = newStatus
        if self._status == 4 or self._status == 5:
            print("Ready to send back {}".format(PatientID._statusRead[self._status]))

class Hopper:
    """
    this object will hold individual Patient ID # before they are assigned a batch to be in
    we want to use a buffer queue style for prioritizing First In First Out
    """
    def __init__(self):
        self._Q = Queue()

    def add(self, item):
        return

    def makeBatch(self):
        pass

class Batch:
    """
    this object will hold sets of Patient IDs from when they are assigned a Batch from the hopper until they have
    received a batch testing result
    """
    _statusProgress = {0: (1, 2),
                       1: (2, 4),
                       2: (3,),
                       3: (4, 5)
                       }
    _statusRead = {0: "Awaiting Batch Testing",
                   1: "Awating Batch Results",
                   2: "Awaiting Individual Testing",
                   3: "Awaiting Individual Results",
                   4: "Negative Result",
                   5: "Positive Result"
                   }

    def __init__(self, items):
        """
        this initializes the batch and inputs all the items.
        :param items: a tuple with all elements of class PatientID these are the elements that are to be used together.
        """

        self.items = items
        self._status = None
        for item in range(0,len(items)):
            if item._status == 4 or item._status == 5:
                raise ValueError("Resolved case was passed to Batch")
            if self._status == None:
                self._status = item._status
            else:
                if item._status != self._status:
                    raise ValueError("Batch was made with IDs not at the same stage")

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
        ##TODO:this will have to decide if this is going to resolve the Batch and then decide if it is going to send
        # negative results or if it passes on to the Individual Queue


class BatchStore:
    """
    This object will hold batches while from when they are formed until they have outcomes.
    """

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

    def __init__(self):
        self._Q = Queue()
        self._minorQ = Queue()
        self._testing = {}

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
        if res == "Y" or res == "y":
            a.updateStatus(3)
            self._testing[a.num] = a
        return

    def put(self, items):
        """
        this method adds items to the scheduler to be handled in order
        :param items: is a PatientID type object or a tuple or list of PatientID objects
        :return: None
        """
        if isinstance(items, PatientID):
            if items._status not in (0, 1, 2):
                ValueError("Patient cannot be put into individual testing schedule with status:\n {}".format(
                    IndividualStore._statusRead(items._status)))
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
        patient = self._testing[id]
        self._testing[id] = None

        patient.updateStatus(4+result)
        #TODO: issue resolve command to patient



def testing():
    a, b, c, d, e = PatientID(), PatientID(), PatientID(), PatientID(), PatientID()
    print(b)
    store = IndividualStore()
    aNum = a.num
    dNum = d.num
    store.put([a, b, c, d, e])
    store.getNextTest()
    store.getNextTest()
    store.getNextTest()
    store.getNextTest()
    print(store._testing)
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



if  __name__ == "__main__":
    testing()