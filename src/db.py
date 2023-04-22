import xml.etree.ElementTree as ET

from src.Board import Board
from src.Task import Task
from src.Column import Column


def buildXML(project: Board, projectName="project"):
    root = ET.Element("Project")
    _board = ET.SubElement(root, "Board", title=project.title)

    for x in range(len(project.columnList)):
        pjColumn: Column = project.columnList[x]
        _column = ET.SubElement(_board, "Column", title=pjColumn.title, WIPLimit=str(pjColumn.WIPLimit))
        for y in range(len(pjColumn.taskList)):
            pj_task: Task = pjColumn.taskList[y]
            task = ET.SubElement(_column, "Task", title=pj_task.title)

            description = ET.SubElement(task, 'description')
            description.text = pj_task.describe

            # priority = ET.SubElement(task, 'priority')
            # priority.text = str(pj_task.priority)

            date = ET.SubElement(task, 'date')
            StartDate = ET.SubElement(date, 'StartDate')
            StartDate.text = pj_task.date[0]
            EndDate = ET.SubElement(date, "EndDate")
            EndDate.text = pj_task.date[1]

            his = ET.SubElement(task, "historyList")
            if range(len(pj_task.history)) != 0:
                for z in range(len(pj_task.history)):
                    history = ET.SubElement(his, "history")
                    history.text = str(pj_task.history[z])

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(projectName + ".xml", encoding='utf-8', xml_declaration=True)


def parserXML(fileAddress="template.xml"):
    tree = ET.parse(fileAddress)
    root = tree.getroot()
    _board = Board(root.find("Board").attrib.get("title"))
    for n in root.iter("Column"):
        columnWIP = n.attrib.get("WIPLimit")
        columnTitle = n.attrib.get("title")
        _column = Column(columnTitle, columnWIP)
        _board.columnList.append(_column)

        for m in n.iter("Task"):
            # task_id = m.attrib.get("id")
            taskTitle = m.attrib.get("title")
            taskDescribe = m.find("description").text
            # taskPriority = m.find("priority").text
            taskStartDate = m.find("date").find("StartDate").text
            taskEndDate = m.find("date").find("EndDate").text
            _task = Task(taskTitle, taskDescribe, taskStartDate, taskEndDate)
            _column.taskList.append(_task)

            taskHisList = m.find("historyList")
            if len(taskHisList.findall("history")):
                for v in taskHisList.iter("history"):
                    _task.history.append(v.text)

    return _board


if __name__ == "__main__":
    board = Board("template board")
    column_list = []
    for i in range(2):
        column = Column("Column " + str(i))
        for j in range(2):
            column.taskList.append(Task("Task " + str(j), "description for task " + str(j), ))
        board.columnList.append(column)

    buildXML(board)
    _board = parserXML()
    buildXML(_board)

