# Testing-Optimizer

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
    
Just thinking about covid testing and proper use of resources. 


So, I (Thomas Davidson) was doing a little math in my free time to see
how much batch testing covid tests would reduce cost, time, and materials.
I was surprised when I figured about optimized performance and found that
there was a lot more savings than I expected. 

So, initially on July 24 to 31 I would like to have memory reserved to 
detect based on current samples how many samples should be an a batch test.
(DONE)

Moving forward I would love to be able to give running totals and to move 
items from memory to storage and load that back to memory August 1 - 4 (DONE)

Lastly I would like to rework my initial math accounting for false 
positives and false negatives. (THIS DOESN'T LOOK LIKE IT WILL BE NEEDED)

Next goal, review and revise where necessary all documentation. August 3-5


I will reassess goals for this sprint or the next sprint. 
    If you have any suggestions please feel free to contact me to allow me to work on those.

MANUAL:

To use this project I reccomend running the Main.py program with your python interpreter.

Once, the program starts it will initalize and imagine that the entire tested population is one positive case out of two
 total cases. 

Commands 
    
    show w                      this shows warranty information and is required for the GNU license
    show c                      this shows copy information and is required for the GNU license
    exit                        this exits the program, shutsdown all threads, and saves the current state
    population                  this command will give information about the positivity rate and a 
                                    count of all resolved samples
    add pop: (int) (int)	    this will add members to the population the first number here is positive cases and the
                                    second number is negative cases this only supports whole numbers                                  
    prop: (float)               this will give information about optimal batch sizes when for a particular proportion 
                                    of the population.  this proportion will be a decimal number between 0 and 1. 
    batch size                  this is a request for information about optimal batch sizes given the current 
                                    result population
    add patient                 this is the method for adding a patient, 
        Enter new Accession Number:     this is a name to be assigned to the sample
    test results                this is a command to assign test results to a sample that you have tested.
                                    next you will be asked for the key from the above list this key is an int
                                    after theis you will be asked if the test was positive or negative with + or - 
    get next                    this will print the next test in the queue it pioritises whichever has more tests of 
                                    batch or individual tests followed by batch tests over individual tests.
    save                        this feature will save all of the objects in the file and resuming running all threads 
                                    after the save is finished.
    clear                       this action will clear any information displayed on the console at this time and 
                                    readys for next action.
These commands will be updated later to align more with APIs that are in use already. 
 