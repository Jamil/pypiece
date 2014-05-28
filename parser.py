import sys
import os
import re
import pyparsing
import pydot

class PythonProject(object):
    def __init__(self):
        self.all_classes = {}
        # Any class with a superclass not defined in the project is a 'root class'
        self.root_classes = []

class PythonClass(object):
    def __init__(self, name, parent_class):
        self.name = name
        self.parent = parent_class
        self.parent_obj = None
        self.ivars = set()
        self.funcs = set()
        self.is_root = False
    def __repr__(self):
        str = self.name + '\n'
        str += '\tInherits from ' + self.parent + '\n'
        str += '\tInstance variables: \n'
        for ivar in self.ivars:
            str += '\t\t' + ivar + '\n'
        str += '\tFunctions: \n'
        for func in self.funcs:
            str += '\t\t' + func + '\n'
        return str

def main():
    if len(sys.argv) <= 1:
        print "Please enter the directory as an argument"
        return
    
    directory = sys.argv[1]
    python_files = retrieveFilesWithExtension(directory, ".py")
    
    if not directory.endswith('/'):
        directory += "/"

    python_files = [directory + str(x) for x in python_files]
    
    contents = retrieveFileContents(python_files)

    classes = []
    for file_contents in contents:
        classes += findClasses(contents[file_contents])

    project = PythonProject()

    for pyclass in classes:
        project.all_classes[pyclass.name] = pyclass
    
    for pyclass in classes:
        if pyclass.parent in project.all_classes:        
            pyclass.parent_obj = project.all_classes[pyclass.parent]
        else:
            project.root_classes.append(pyclass)
            pyclass.is_root = True
    drawProject(project)
    prompt(project)


def prompt(project):
    while True:
        cmd = raw_input('>> ')
        args = cmd.split()
        if len(args) > 1 and args[0] == 'class':
           if not args[1] in project.all_classes:
               print 'Not Found.'
           else:
               c = project.all_classes[args[1]]
               print '\n'
               print c
        elif len(args) > 1 and args[0] == 'graph':
            graph = pydot.Dot(graph_type='graph')
            args = args[1:]
            classes = set()
            
            for arg in args:
                classes.add(arg)

            for pyclass in project.all_classes:
                class_obj = project.all_classes[pyclass]
                if class_obj.name in classes or class_obj.parent in classes:
                    edge = pydot.Edge(' ' + class_obj.parent + ' ', ' ' + class_obj.name + ' ')
                    graph.add_edge(edge)
            
            graph.write_png(args[0] + '.png')
        
        elif len(args) > 0 and args[0] == 'quit':
            break

        else:
            print 'Invalid command'

def drawProject(project):
    graph = pydot.Dot(graph_type='graph')

    for pyclass in project.all_classes:
        class_obj = project.all_classes[pyclass]
        edge = pydot.Edge(' ' + class_obj.parent + ' ', ' ' + class_obj.name + ' ')
        graph.add_edge(edge)

    graph.write_png('class_hierarchy.png')

def retrieveFilesWithExtension(dir, ext):
    files = []
    for file in os.listdir(dir):
        if file.endswith(ext):
            files.append(file)
    return files

def retrieveFileContents(files):
    fileContents = {}
    for file in files:
        with open(file) as f:
            fileContents[file] = f.readlines()
    return fileContents

def parseClassDeclaration(line):
    line = line.strip("class ")
    open_paren_index = line.find("("); 
    close_paren_index = line.find(")");
    dot_index = line.find(".");
    
    classname = None
    parent = None
    if dot_index == -1:
        classname = line[:open_paren_index]
        parent = line[open_paren_index + 1 : close_paren_index]
    else:
        classname = line[:open_paren_index]
        parent = line[dot_index + 1: close_paren_index];

    if not classname.isalpha() or not parent.isalpha():
        return None
    
    newclass = PythonClass(classname, parent)
    return newclass

def parseIVarAssignment(line):
    dot_index = line.find(".")
    space_index = line.find(" ")
    ivar = line[dot_index + 1 : space_index] 
    return ivar

def parseFunctionDeclaration(line):
    return line.strip("def ")

def findClasses(lines):
    all_classes = []

    classre = re.compile('class .*\(.*\):')
    ivar_re = re.compile('self\..* = ');
    f_re = re.compile('def .*\(.*\):')
    current_class = None
    for line in lines:
        arr = ivar_re.findall(line)
        f_arr = f_re.findall(line)
        if classre.match(line):
            newclass = parseClassDeclaration(line)
            if newclass:
                all_classes.append(newclass)
                current_class = newclass
        elif arr:
            ivar_name = parseIVarAssignment(arr[0])
            if ivar_name.isalpha() and current_class:
                current_class.ivars.add(ivar_name)
        elif f_arr:
            func_name = parseFunctionDeclaration(f_arr[0])
            if current_class:
                current_class.funcs.add(func_name)
    return all_classes
        
main()
