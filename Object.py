import hashlib
from time import time
idNum = 0
class PatientID:
    """
    this object is designed to be the way we interact with an individual's data and store it's current status of testing

    self params
    :param num: a str this is a hashed identifier and is the most common ID to be used in methods display this as it's first
    8 characters for human readability
    :param name: a str or default None this is a string that I may use to store the name of the patient with any information needed to give \
    resutls to them
    :param status: an int default 0 will refer to the status accoring to this dictionary
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
    """
    i = 1
    _statusRead = {0: "Awaiting Batch Testing",
                  1: "Awating Batch Results",
                  2: "Awaiting Individual Testing",
                  3: "Awaiting Individual Results",
                  4: "Negative Result",
                  5: "Positive Result"
                  }
    _statusProgress = {0:(1,),
                      1:(2,4),
                      2:(3,),
                      3:(4,5)
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
        self.status = status

    def __str__(self):
        return "Start of ID #: \t\t{}\nName: \t\t\t{}\nTesting status: \t{}".format(str(self.num)[:8], str(self.name),
                                                                                    PatientID._statusRead[self.status])

    def updateStatus(self, newStatus):
        if self.status not in PatientID.statusProgress:
            raise ValueError("This patient has Already received an outcome. This was: {}".format(
                PatientID._statusRead[self.status]))
        if newStatus not in PatientID._statusProgress[self.status]:
            raise ValueError("This Patient is at the stage: {} and cannot move directly to {}".format(
                PatientID.statusRead[self.status], PatientID._statusRead[newStatus]))
        self.status = newStatus
        if self.status == 4 or self.status == 5:
            print("Ready to send back {}".format(PatientID._statusRead[self.status]))

class Hopper:
    """
    this object will hold individual Patient ID # before they are assigned a batch to be in
    we want to use a buffer queue style for prioritizing First In First Out
    """

class Batch:
    """
    this object will hold sets of Patient IDs from when they are assigned a Batch from the hopper until they have
    received a batch testing result
    """


class BatchStore:
    """
    This object will hold batches while from when they are formed until they have outcomes.
    """

class IndividualStore:
    """
    this object will hold Patient ID#s from when they are assigned to be individually tested until they receive outcomes.
    """


def testing():
    for _ in range(20):
        print(PatientID())
    a= PatientID()
    print("Start positive:")
    print(a, "\n")
    a.updateStatus(1)
    print(a, "\n")
    a.updateStatus(2)
    print(a, "\n")
    a.updateStatus(3)
    print(a, "\n")
    a.updateStatus(5)
    print(a, "\n")
    print("Start negative with neg batch:")
    b = PatientID()
    print(b, "\n")
    b.updateStatus(1)
    print(b, "\n")
    b.updateStatus(4)
    print(b, "\n")
    print("Start negative with pos batch:")
    c = PatientID()
    print(c, "\n")
    c.updateStatus(1)
    print(c, "\n")
    c.updateStatus(2)
    print(c, "\n")
    c.updateStatus(3)
    print(c, "\n")
    c.updateStatus(4)
    print(c, "\n")

if  __name__ == "__main__":
    testing()