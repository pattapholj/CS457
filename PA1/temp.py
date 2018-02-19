# -*- coding: utf-8 -*-

import cmd, sys
import os
import xml.etree.cElementTree as ET

runProgram = True;



class Interface(cmd.Cmd):
    intro = 'PA1 Assignment by Pattaphol Jirasessakul.\n'
    prompt = '(>) '
    file = None  
    command_list = list()
    DBInUse = "None"
    directory = "C:/PA1/"
########################################## 
    def do_exit(self, arg):
        'Stop recording, close the turtle window, and exit:  BYE'
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

    #command_list = list commands user enter before entering "go"
    #command = one particular command from command_list
 
            
    def do_create(self,arg):
        
        command  = arg.split(" ")
        command.insert(0,"create")
        self.command_list.append(command)
         
        print(self.command_list)
      #  print(self.command_list[0][3])
    
    
    def do_alter(self,arg):
        command = arg.split(" ")  
        command.insert(0,"alter")
        self.command_list.append(command)
        print(self.command_list)
    
    
      
    def do_go(self,arg):
        
        for command in self.command_list:
            if command[0] == "create":
                if (self.create(command) == False):
                    self.command_list.clear()
                    break
                    
        
#            if command[0] == "use":
#                print("call use")
                
            if command[0] == "drop":
                print("call drop")
        
            if command[0] == "select":
                print("call select")
                
            if command[0] == "alter":
                print("call alter")
        
        print(self.command_list)
    
        self.command_list.clear()
        print(self.command_list)
   
    def do_use(self,arg):
        
        self.DBInUse = arg
    
 #########################################   
    def create(self,command):
        
        if(command[1].lower() == "database"):
            print("call create database")
            return self.createDB(command[2]); #command[2] represents name of of db or table
        
        
        
        elif(command[1].lower() == "table"):
            if (len(command) == 2):
                print("Can't create table without table name")
                return False
            else:
                
                return self.createTable(command[2],self.DBInUse)
        
        
        else:
            print("Syntax error with create")
            return False
    
 
    def createDB(self,DBName):
        
        directory = self.directory + DBName
        if not os.path.exists(directory):
            os.makedirs(directory)
            self.initializeMeta(DBName,directory)
            return True;
        else:
            print("Database " +DBName + ", already exists")
            return False;


    def createTable(self,tableName,DBInUse):
        
         
        tableName = tableName
        tableLocation = os.path.join(self.directory,DBInUse,tableName) 
        
        if(self.DBInUse == "None"):
            print("No Database in use, can't create a table")
            return False
        
        
        os.chdir(os.path.join(self.directory,DBInUse))
        tree= ET.parse(DBInUse+".xhtml")
        root = tree.getroot()
         
         
        if (root.find(tableName) == None):
               # open(tableLocation, "a")
                #print(os.path.join(self.directory,DBInUse))
            
            c= ET.SubElement(root,tableName)
            c.text = 'test'
           # print (ET.tostring(root))
                 
            tree.write(DBInUse+".xhtml")
#                DB = root.find(root.tag)
                #print(DB.tag)
                 
                
            return True
        else:
            print("Table already exists in current database")
            return False    

 #########################################      

    def initializeMeta(self,DBName,directory):
        root = ET.Element(DBName)
            
        # wrap it in an ElementTree instance, and save as XML
        tree = ET.ElementTree(root)
        os.chdir(directory)
        tree.write(DBName+".xhtml")

#
#
#
#
#
#

          
  
    
            
    
Interface().cmdloop()

