#! /usr/bin/python 

import sys
import math

class IcfUtil(object):
    """ This class maintains the global state 
    information and provides some helpful 
    functions
    """
    def __init__(self, no_procs):
        self.no_procs = no_procs
        self.header_row = []

    def local_to_global_index(self, proc_id, local_index):
        return proc_id + local_index*self.no_procs

    def compute_global_to_local(self, proc_id, global_index):
        if (global_index - proc_id) % self.no_procs != 0:
            return -1
        else:
            return (global_index - proc_id) / self.no_procs
        

class Processor(object):
    """ Simulates multiprocessor environment.
    """
    def __init__(self, id, n):
        self.id = id
        self.rows = []
        self.n = n
        self.v = []
        # Initialize to n x p
        self.H = []
        self.max = None
        self.max_index = None
        
        # Add pivot values list 
        

    def add_row(self, row):
        self.rows.append(row)
        temp = []
        for i in range(len(row)):
            temp.append(0.0)

        self.H.append(temp)


    def calculate_partial_diagnol(self, total):
        for i in range(len(self.rows)):
            index = self.id + i*total
            self.v.append(self.rows[i][index])
        print self.v

    def calculate_max(self, total):
        self.max = max(self.v)
        self.max_index = self.v.index(self.max)

    def get_max(self):
        return self.max

    def get_max_index(self):
        return self.max_index

    def update_icf_matrix(self, column, header_row,master=False, local_index=-1):

        for k in range(column):
            for i in range(len(self.rows)):
                if master and local_index == i:
                    continue
                else:
                    self.H[i][column] = self.H[i][column] - self.H[i][k] * header_row[k]

        for i in range(len(self.rows)):
            if master and local_index == i:
                continue
            else:
                self.H[i][column] = self.rows[i][column] - self.H[i][column]
        
        for i in range(len(self.rows)):
            if master and local_index == i:
                continue
            else:
                print i, column
                print header_row
                self.H[i][column] = float(self.H[i][column]) / header_row[column]


    def update_diagnol(self, column):
        for i in range(len(self.rows)):
            self.v[i] = self.H[i][column] ** 2
        

if __name__ == '__main__':
    mat = [[24, 0, 6, 0, 0], [0, 8, 2, 0, 0], [6, 2, 8, -6, 2], [0, 0, -6, 24, 0], [0, 0, 2, 0, 8]]
    
    processors = []

    for i in range(2):
        processor = Processor(i, 4)
        processors.append(processor)

    for i in range(len(mat)):
        processors[(i + 2) % 2].add_row(mat[i])


    util = IcfUtil(2)
    
    k = int(math.sqrt(5))

    for i in range(2):
        processors[i].calculate_partial_diagnol(util.no_procs)

    for column in range(k):
        global_max = -sys.maxint 
        global_max_index = None
        global_max_proc = None
        

        for i in range(2):
            processors[i].calculate_max(util.no_procs)
            if processors[i].get_max() > global_max:
                global_max = processors[i].get_max
                global_max_index = util.local_to_global_index(i, processors[i].get_max_index())
            
    
    

        util.header_row = []
        for i in range(2):
            proc = processors[i]
            local_index = util.compute_global_to_local(i, global_max_index)
            if local_index != -1:
                proc.H[local_index][column] = math.sqrt(proc.rows[local_index][column])
                map(util.header_row.append, proc.H[local_index][:column +1])

        print util.header_row

        for i in range(2):
            proc = processors[i]
            local_index = util.compute_global_to_local(i, global_max_index)
            if local_index != -1:
                proc.update_icf_matrix(column, util.header_row, True, local_index)
            else:
                proc.update_icf_matrix(column, util.header_row)

        for i in range(2):
            proc = processors[i]
            proc.update_diagnol(column)

        print util.header_row
            

