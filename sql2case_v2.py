# -*- coding:utf-8 -*-
import re
import sys
from argparse import ArgumentParser

r_table = re.compile("CREATE TABLE `?([\w_]+)`? \((.*)\)(.*?);$")
caseSuffix = "Dto"

class Table:
    def __init__(self, query):
        self.separater(query)

    def separater(self,query):
        q = query.strip()
        m = r_table.match(q)
        self.tableName = m.group(1)
        self.columnSeq = m.group(2).split(",")
        self.camelTable = classCamel(self.tableName)

    def caseClass(self):
        print "case class " + self.camelTable + caseSuffix + "("
        valList = []
        for i,elem in enumerate(self.columnSeq):
            columnName, dataType = columnData(elem)
            if dataType != "":
                valList.append("  " + snake2camel(columnName) + ": " + dataType)
        for i,val in enumerate(valList):
            print val,
            if (i < len(valList) - 1):
                print","
            else:
                print
        print ")"

    def tableTag(self):
        print "class " + self.camelTable + "Table(tag: Tag) extends Table[" + self.camelTable + caseSuffix +"](tag, \"" + self.tableName + "\") {"

        for i,elem in enumerate(self.columnSeq):
            columnName, dataType = columnData(elem)
            if dataType != "":
                print "  def " + snake2camel(columnName) + ": Column[" + dataType + "] = column[" + dataType + "](\"" + columnName + "\")"

        columns = [snake2camel(columnData(x)[0]) for x in self.columnSeq if columnData(x)[1] != ""]
        print "def * = (" + ",".join(columns) + ")<>(" + self.camelTable + caseSuffix + ".tupled, " + self.camelTable + caseSuffix + ".unapply)"
        print "}"

    def getTableName(self):
        print self.tableName
        return self.tableName
    def getColumnSeq(self):
        print self.columnSeq
        return self.columnSeq

def snake2camel(string):
    return re.sub("_(.)",lambda x:x.group(1).upper(),string)

def classCamel(string):
    string = string[0].upper() + string [1:]
    return snake2camel(string)

def columnData(elem):
    columnItems = elem.split()
    columnName = re.sub("`" ,"" , columnItems[0])
    dataType = datatype(columnItems[1])
    return (columnName, dataType)

def datatype(typeName):
    t = re.sub("\(.*\)","",typeName.lower())
    if t in {"bigint", "int", "tinyint"}:
        return "Int"
    elif t in {"timestamp", "datetime"}:
        return "DateTime"
    elif t in {"varchar","text"}:
        return "String"
    else:
        return ""

def parserAdder():
    parser = ArgumentParser(description = "SQL to scala case class for slick ORM")
    parser.add_argument(
        "filename",
        type=str,
        help="sql file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parserAdder()
    with open(args.filename) as f:
        sql = "".join([x.strip() for x in f.readlines()]);
        print sql
        t = Table(sql)
        t.caseClass()
        t.tableTag()
