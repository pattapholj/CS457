# -*- coding: utf-8 -*-
#PA1 by Pattaphol Jirasessakul
#CS 457



import shutil # for removing folders and files
import cmd, sys
import os
import xml.etree.cElementTree as ET #for creating and working  with XML files
from pathlib import Path
 



#Inherit from the cmd framework for creating command line interpreters 
#https://docs.python.org/2/library/cmd.html
class Interface(cmd.Cmd):
    intro = 'PA1 (new) Assignment by Pattaphol Jirasessakul.\n'
    prompt = '(>) '
    file = None  
    command_list = list()
    DBInUse = "None"
    directory = os.getcwd()
########################################## 
    def do_exit(self, arg):
        'Stop recording, close the window, and exit:  BYE'
        print('Closing PA1')
        self.close()
        return True

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
            
    def precmd(self,  line ):
        line = line.lower()
        return line
 
            
    def do_create(self,arg):
        
        command  = arg.split(" ")
        command.insert(0,"create")
        self.command_list.append(command)
        if command[0] == "create":
            if (self.create(command) == False): #if create_table or create_db doesn't work
                self.command_list.clear() #clear list of quer
                command.clear()
        self.command_list.clear()
        print(self.command_list)
      
    
    
    def do_alter(self,arg):
        command = arg.split(" ")  
        command.insert(0,"alter")
        self.command_list.append(command)
        
        
     
    def do_drop(self,arg):
        command  = arg.split(" ")
        command.insert(0,"drop")
        self.drop(command) 
        command.clear()
    
    def do_select(self,arg):   
        command  = arg.split(" ")
        command.insert(0,"select")
        #self.select(command)
        
        tableName = "product"+".xhtml"
        os.chdir(os.path.join(self.directory,"db2")) 
      # tableLocation =( os.path.join(self.directory,self.DBInUse,tableName) )
        metaTree =ET.parse("productMeta.xhtml")        
        metaRoot = metaTree.getroot()
        print(command[3])
        print("Showing data of table: "+  command[3])
        colNames = ''
        
        #print meta data of rows
        for child in metaRoot:
            colNames += child.attrib["ColumnName"] + " "+ child.attrib["DataType"] + "|"
        print(colNames)
#       
                
        
        tree = ET.parse(tableName)
        root = tree.getroot()
        colData = ''        
#       
#        #Get the entire table with select
        if(command[1] == '*'):
            for row in root:
                for col in row:
                    colData += (col.text + "|")
                print (colData)
                colData = ''
            return True

        
        #Else user wants specific rows            
        #check if rows to be projected is actually in the metadata file of that table
        colNames = command[1:command.index("from")]
        colNames="".join(colNames).split(",")
        
        columnCount = 0
        for child in metaRoot:
           if (child.attrib["ColumnName"] in colNames):
              columnCount += 1;
              
        if columnCount == len(colNames):
           print("it works")
            for row, data in zip(root, colNames):
               colData = row.find(data)
               
        else:
            print("Columns to be projected is not in the table")
            return False
        #colCheck(colNames)
            
    
    
    def colCheck(self,arg):
        metaTree =ET.parse("productMeta.xhtml")        
        metaRoot = metaTree.getroot()
        
        print(metaRoot.find("name"))
            
        
    
                  
    #Set the current database that the user wants to use
    def do_use(self,arg):
        self.DBInUse = arg
        directory = self.directory +"/"+ self.DBInUse
        if not os.path.exists(directory):
            print(self.DBInUse + " doesn't exist.")
             
        else:
            print("Using " + self.DBInUse + " as current database.")
            
    def do_insert(self,arg):
        command = arg.split(" ")
        command.insert(0,"insert")
        self.insert(command)
        command.clear()
        
    def do_update(self,arg):
        command = arg.split(" ")
        command.insert(0,"update")
        self.update(command)
    
    def do_delete(self,arg):
        command = arg.split(" ")
        command.insert(0,"update")
        self.delete(command)
            
            
    
 #########################################   
    def create(self,command):
        
        if(command[1].lower() == "database"):
            print("call create database")
            return self.createDB(command[2]); #command[2] represents name of of db or table
        
        
        
        elif(command[1].lower() == "table"):
            if (len(command) <=2):
                print("Can't create table without table name")
                return False
            else:
                return self.createTable(command[2],self.DBInUse,command)
        else:
            print("Syntax error with create")
            return False
    
 
    def createDB(self,DBName):
        
        directory = self.directory +"/"+ DBName
        if not os.path.exists(directory):
            os.makedirs(directory)
            self.initializeMeta(DBName,directory)
            return True;
        else:
            print("Database " +DBName + ", already exists")
            return False;


    def createTable(self,tableName,DBInUse,command):
        
        if(self.DBInUse == "None"):
            print("No Database in use, can't create a table")
            return False
        
        tableLocation = (os.path.join(self.directory,DBInUse,tableName+"Meta.xhtml"))
        dataChunk = self.parseTableCreate(command)
         
        os.chdir(os.path.join(self.directory,DBInUse)) # change directory to current DB in use

        if os.path.exists(tableLocation): #if table exists in current directory
           print ("Table with this name already exists")
           return False  
            
        else:#else create metadata of the table
            root = ET.Element(tableName)
            tree = ET.ElementTree(root)
            
            for chunk in dataChunk:
                column=ET.SubElement(root,"col") #create column
                column.set('ColumnName', chunk[0].split()[0])
                column.set('DataType', chunk[0].split()[1]) # set data type of column
 
            tree.write(tableName+"Meta"+".xhtml") # write to xml file           
            
            #creating the actual table
            root = ET.Element(tableName)
            tree = ET.ElementTree(root)
            tree.write(tableName+".xhtml")
        
        return True

 #########################################      

# XML file management functions

    #Use database name and current directory to generate metadata file of a database
    def initializeMeta(self,DBName,directory):
        root = ET.Element(DBName)
        tree = ET.ElementTree(root)
        os.chdir(directory)
        
        tree.write(DBName+".xhtml")

    #Parse a create table query and return a list containing the columns and their data type
    def parseTableCreate(self,command):
        
        #commands to create table will be something like "create table tablename  (x y)" 
       testData = command[3:] #remove 'create' and 'table' from list to get parameters
        
       testData2 = " ".join(testData)[1:-1].split(" ")  #remove parentheses
       testData2 =" ".join(testData2).split(",")  # remove commas
       chunks = [testData2[x:x+1] for x in range(0, len(testData2), 1)] # make all name and data types into pairs
       return (chunks)

#########################################  

    def drop(self,command):
        if(command[1].lower() == "database"):
            os.chdir(self.directory)
            dbToDelete = (os.path.join(self.directory,command[2]) )
            
            
            shutil.rmtree(dbToDelete, ignore_errors=True)
            print("delete database " + dbToDelete)
            return True; #command[2] represents name of of db or table
        
        
        
        elif(command[1].lower() == "table"):
            if(self.DBInUse == "None"):
                print("No Database in use, can't delete table")
                return False
        
            tableName = command[2]+".xhtml"
            os.chdir(os.path.join(self.directory,self.DBInUse)) 
            tableLocation = Path(os.path.join(self.directory,self.DBInUse,tableName))
              
            
            if (len(command) <= 2):
                print("Can't delete table without table name")
                return False
            
            if  not os.path.exists(tableLocation): #if table exists in current directory
                print ("Table " +command[2] + " doesn't exists in " +self.DBInUse )
                print(tableLocation )
                
                return False  
        
            else:
                os.remove(tableLocation)
               
                
                
        else:
            print("Syntax error with Drop")
            return False

#########################################

    def insert(self,command):
        if len(command) <=3:
            print("Syntax error with insert")
            return False
        
        if self.DBInUse == "None":
            print("No Database in use to get table from")
            return False
            
        else:
          #  print(self.DBInUse)
            tableName = command[2]+".xhtml"
            os.chdir(os.path.join(self.directory,self.DBInUse)) 
            tableLocation =( os.path.join(self.directory,self.DBInUse,tableName) )
            
            if  not os.path.exists(tableLocation): #if table exists in current directory
                print ("Table " +command[2] + " doesn't exists in " +self.DBInUse )
                return False
                
            else:             
                tree = ET.parse(command[2]+".xhtml")
                root = tree.getroot()
                
                testData = command[3:]
                testData2 = " ".join(testData)[7:-2].split(' ') 
                testData2 = "".join(testData2)
                testData2 = testData2.split()
                testData2 =" ".join(testData2).split(",")  # remove commas
                 
                os.chdir(os.path.join(self.directory,self.DBInUse)) 
                
                #Get XML tree of the table's metadata
                tree2 = ET.parse(command[2]+ "Meta"+".xhtml")  
                root2 = tree2.getroot()
                 #Create a subtree to represent the row of the table being inserted
                tblObject = ET.SubElement(root,"Row")  
                
                #For column we're inserting, pair it to the correct attribute and then insert
                for child, data in zip(root2, testData2):
                    column=ET.SubElement(tblObject,child.attrib["ColumnName"]) #create column
                    #column.set(child.attrib["ColumnName"], data) #put data into column
                    column.text = data
                tree.write(command[2]+".xhtml") # write to xml file          
                print("Record inserted")
                return True
        

 
    def select(self,command):
        
        if len(command) <=3:
            print("Syntax error with select")
            return False
        
        if self.DBInUse == "Null":
            print("No Database in use to get table from")
            return False
        
        else:
            tableName = command[3]+".xhtml"
            os.chdir(os.path.join(self.directory,self.DBInUse)) 
            tableLocation =( os.path.join(self.directory,self.DBInUse,tableName) )
            
            if  not os.path.exists(tableLocation): #if table exists in current directory
                print ("Table " +command[3] + " doesn't exists in " +self.DBInUse )
                return False
            
            else:     #go to XML file and print out all of its children which are the columns         
                tree = ET.parse(tableName)
                root = tree.getroot()
                print("Showing name of columns and their data types")
                for child in root:
                   print(child.tag, child.attrib)
                   
#########################################  
    
    def update(self,command):   
        if len(command) <=3:
            print("Syntax error with update")
            return False
        
        if self.DBInUse == "None":
            print("No Database in use to get table from")
            return False
        
        else:
          #  print(self.DBInUse)
            tableName = command[1]+".xhtml"
            os.chdir(os.path.join(self.directory,self.DBInUse)) 
            tableLocation =( os.path.join(self.directory,self.DBInUse,tableName) )
            
            if  not os.path.exists(tableLocation): #if table exists in current directory
                print ("Table " +command[1] + " doesn't exists in " +self.DBInUse )
                return False
                
            tbl = command[:2]      #'Update tblname'
            update = command[2:-4] #'Set attribute1 = x'
            condition= command[-4:] #Where attribute2 = y'
            
            #set variables so function know the conditions and value to update
            conditionCol =  condition[1]#The column fulfilling the conditon 
            updateCol = update[1] #The column that will be updated
            conditionVal = "".join(condition[3]).split(';') #the condition that the column has to be before being updated
            updateVal = update[3] #value to update the column of that row to
            
            #for each row, look at the the column that fulfills the condition
            #once it finds the row with that column value, update the value of 
            #the column that the user wants to be changed
            os.chdir(os.path.join(self.directory,"db2"))
            tree = ET.parse(tbl[1]+".xhtml")
            root = tree.getroot()
            for row  in root: #find column with the correct attribute
                Col = row.find(conditionCol) #Where attribute1 = y'
                if (Col.text == conditionVal[0]):
                    updatedCol = row.find(updateCol)#'Set attribute2 = x'
                    #print(updateVal )
                    updatedCol.text = updateVal
                    
            tree.write(tbl[1]+".xhtml") 
                
            
########################################################################    
    
    def delete(self,command):    
        if len(command) <=3:
            print("Syntax error with select")
            return False
        
        if self.DBInUse == "None":
            print("No Database in use to get table from")
            return False
        
        else:
          #  print(self.DBInUse)
            tableName = command[2]+".xhtml"
            os.chdir(os.path.join(self.directory,self.DBInUse)) 
            tableLocation =( os.path.join(self.directory,self.DBInUse,tableName) )
            
            if  not os.path.exists(tableLocation): #if table exists in current directory
                print ("Table " +command[2] + " doesn't exists in " +self.DBInUse )
                return False
                        
            tbl = command[2]      #'Update tblname'
            condition= command[-4:] #delete if..
            conditionOp = command[-2]   
            #set variables so function know the conditions and value to update
            conditionCol =  condition[1]#The column fulfilling the conditon 
            updateCol = update[1] #The column that will be updated
            conditionVal = "".join(condition[3]).split(';') #the condition that the column has to be before being updated
            updateVal = update[3] #value to update the column of that row to
            
            os.chdir(os.path.join(self.directory,"db2"))
            tree = ET.parse("product"+".xhtml")
            root = tree.getroot()
            for row  in root: #find column with the correct attribute
                Col = row.find(conditionCol) #Where attribute1 = y' , gets that specific column
                
                #check what math operation user wants done
                if(conditionOp == '='):            
                    if (Col.text == conditionVal[0]):
                        #updateCol = row.find(updateCol)#'Set attribute2 = x'
                        root.remove(row)
                        print("Record removed")
                        
                elif(conditionOp == '>'): 
                    #if the value in the user's where condition is a number,
                    #change from string to int, along with the value in the column
                    if(conditionVal[0].replace('.','',1).isdigit()):
                        conditionValInt =  float(conditionVal[0])
                        colValInt = float(Col.text)
                    
                    if (colValInt > conditionValInt):
                        root.remove(row)
                        print("Record removed")
                        
                elif(conditionOp == '<'):            
                    if(conditionVal[0].replace('.','',1).isdigit()):
                        conditionValInt =  float(conditionVal[0])
                        colValInt = float(Col.text)
                    
                    if (colValInt < conditionValInt):
                        root.remove(row)
                        print("Record removed")
                    
                tree.write("product"+".xhtml") 
        
        
    def alter(self,command):
        print("Table "+command[2] + " modified")
        
    
        

    
Interface().cmdloop()
