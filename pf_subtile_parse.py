# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 14:14:44 2018

@author: jnguyen3
"""

import os
import csv
from numpy import std
from collections import OrderedDict

class Boxes():
    '''
    Sets the pattern used to group the matrices\n
    Set the .table attribute to a 2d array of size 12x14\n
    Use intergers to separate groups out\n
    By default, it's using a given layout by request\n
    With titles implemented, but this table will work with strings and chars as well
    '''
    def __init__(self, table = None, default = True):
        self.default = default
        default_ref = {0:"NotValid",
                       1:"TopLeft",
                       2:"TopRight",
                       3:"BottomLeft",
                       4:"BottomRight",
                       5:"Center"}
        if table == None:
            self.table = [[0,0,1,1,1,1,1,2,2,2,2,2,0,0],
                          [0,1,1,1,1,1,1,2,2,2,2,2,2,0],
                          [1,1,1,1,1,1,1,2,2,2,2,2,2,2],
                          [1,1,1,5,5,5,5,5,5,5,5,2,2,2],
                          [1,1,1,5,5,5,5,5,5,5,5,2,2,2],
                          [1,1,1,5,5,5,5,5,5,5,5,2,2,2],
                          [3,3,3,5,5,5,5,5,5,5,5,4,4,4],
                          [3,3,3,5,5,5,5,5,5,5,5,4,4,4],
                          [3,3,3,5,5,5,5,5,5,5,5,4,4,4],
                          [3,3,3,3,3,3,3,4,4,4,4,4,4,4],
                          [0,3,3,3,3,3,3,4,4,4,4,4,4,0],
                          [0,0,3,3,3,3,3,4,4,4,4,4,0,0]]
            self.default_table = [[""]*14 for x in range(12)]
            if default:
                for col in range(len(self.table)):
                    for row in range(len(self.table[col])):
                        self.default_table[col][row] = default_ref[self.table[col][row]]
        else:
            self.table = table
        

class Matrix():
    '''
    Matrix object\n
    Contains information on each matrix generated\n
    It also collect averages for each zone/section\n
    And provides statistics\n
    '''
    def __init__(self, tile, matrix, pattern = Boxes(), combined = [], run = ""):
        '''
        tile = the tile number this matrix represents\n
        matrix = a 2d list of int\n
        pattern = the pattern used for parsing out the sub groups\n
        combined = a list of tuples of size two to combine groups\n
        run = the run name\n
        '''
        self.matrix = matrix
        self.tile_38 = tile
        self.surface = "Top" if tile < 20 else "Bottom"
        self.tile = tile if tile < 20 else tile - 19
        self.pattern = pattern
        self.combined = combined
        self.run = run
        self.zones = self.get_zones(self.combined)
        self.averages = self.get_averages()
        self.stdv = self.get_stdv()
        self.data, self.values, self.titles = self.data_collect()
        
    def get_zones(self, combined):
        '''
        Separates out the 2d matrix by zones\n
        To use for statistics\n
        Combined is a list of tuples of size 2\n
        '''
        if self.pattern.default:
            pat = self.pattern.default_table
        else:
            pat = self.pattern.table
        holder = OrderedDict()
        item_set = set()
        for i in pat:
            for j in i:
                if j not in item_set:
                    item_set.add(j)
        for i in item_set:
            holder[i] = []
            for x in range(12):
                for y in range(14):
                    if pat[x][y] == i:
                        holder[i].append(self.matrix[x][y])
        if len(combined)>0:
            for i in combined:
                holder[i] = holder[i[0]] + holder[i[1]]
        return holder
        
    def get_averages(self):
        '''
        Builds a dict, where the key is the zone, and the value is the average\n
        '''
        averages = {}       
        for i in self.zones:
            averages[i] = sum(self.zones[i])/len(self.zones[i])
        return averages
        
    def get_stdv(self):
        '''
        Builds a dict, where the key is the zone, and the value is the stdv\n
        '''
        stdv = {}
        for i in self.zones:
            stdv[i] = std(self.zones[i])
        return stdv
        
    def data_collect(self):
        '''
        organizes the data into a format for easier parsing\n
        '''
        title = []
        title = ["Run","Surface","Tile","Tile_38"]
        for i in self.averages:
            title.append("Average_"+str(i))
            title.append("Stdv_"+str(i))
        
        holder = []
        holder = [self.run, self.surface, self.tile, self.tile_38]
        for i in self.averages:
            holder.append(self.averages[i])
            holder.append(self.stdv[i])
        
        d = OrderedDict(zip(title,holder))
        
        return d, holder, title
        
class Run_file():
    '''
    Takes a run file, which is a csv with multiple matrices\n
    Separated by new line characters\n
    '''
    def __init__(self, fpath):
        '''
        fpath = file path to a csv
        '''
        self.fpath = fpath
        self.matrix_list = {}
        self.tile_counter = 1
        
    def file_read(self, combined = []):
        '''
        reads in a csv, and creates matrix objects, to feed into dict matrix_list
        combined is a list of tuples
        '''
        matrix = []
        with open(self.fpath,"r") as fhand:
            run = os.path.split(self.fpath)[1]
            for line in fhand:
                line = line.strip("\n")
                if line == "":
                    if len(matrix) > 0:
                        self.matrix_list[self.tile_counter] = Matrix(self.tile_counter, matrix, combined = combined, run = run)
                        self.tile_counter += 1
                        matrix = []
                else:
                    matrix.append(map(int,line.split(",")))
        if len(matrix) > 0:
            self.matrix_list[self.tile_counter] = Matrix(self.tile_counter, matrix, combined = combined, run = run)
        

    
def main():
    folder = r"C:\Users\jnguyen3\Desktop\Production FIT Run Outputs from Thara"
    combined = [("TopLeft","BottomLeft"),("TopRight","BottomRight"),("TopLeft","TopRight"),("BottomLeft","BottomRight")]
    titles = []
    with open("subtile_pf_output.csv","wb") as csvfile:
        writer = csv.writer(csvfile)
        for i in os.listdir(folder):
            fpath = os.path.join(folder,i)
            f = Run_file(fpath)
            print f.fpath
            f.file_read(combined)
            matrices = f.matrix_list        
            if len(titles) < 1:
                titles = matrices[1].titles
                writer.writerow(titles)
            row = []
            for i in matrices:
                for title in titles:
                    row.append(matrices[i].data[title])
                writer.writerow(row)
                row = []
if __name__ == "__main__":
    main()