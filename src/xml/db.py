import xml.etree.ElementTree as ET
from src.board.Board import Board
from src.board.Task import Task
from src.board.Column import Column


def buildXML(project: Board, projectName="template"):
    root = ET.Element("Project")
    _board = ET.SubElement(root, "Board", title=project.title)

    for x in range(len(project.columnList)):
        pj_column: Column = project.columnList[x]
        _column = ET.SubElement(_board, "Column", title=pj_column.title, WIPLimit=str(pj_column.WIPLimit))
        for y in range(len(pj_column.taskList)):
            pj_task: Task = pj_column.taskList[y]
            task = ET.SubElement(_column, "Task", title=pj_task.title, id=str(pj_task.id))

            description = ET.SubElement(task, 'description')
            description.text = pj_task.describe

            priority = ET.SubElement(task, 'priority')
            priority.text = str(pj_task.priority)

            createTime = ET.SubElement(task, 'createTime')
            createTime.text = pj_task.StartDate

            leadTime = ET.SubElement(task, 'leadTime')
            leadTime.text = str(pj_task.EndDate)

            his = ET.SubElement(task, "historyList")
            if range(len(pj_task.history)) != 0:
                for z in range(len(pj_task.history)):
                    history = ET.SubElement(his, "history")
                    history.text = str(pj_task.history[z])

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(projectName + ".xml", encoding='utf-8', xml_declaration=True)


def parserXML(fileAddress="test_file.xml"):
    tree = ET.parse(fileAddress)
    root = tree.getroot()
    _board = Board(root.find("Board").attrib.get("title"))
    for n in root.iter("Column"):
        column_WIP = n.attrib.get("WIPLimit")
        column_title = n.attrib.get("title")
        _column = Column(column_title, column_WIP)
        _board.columnList.append(_column)

        for m in n.iter("Task"):
            task_id = m.attrib.get("id")
            task_title = m.attrib.get("title")
            task_describe = m.find("description").text
            task_priority = m.find("priority").text
            task_createTime = m.find("createTime").text
            task_leadTime = m.find("leadTime").text
            _task = Task(task_title, task_describe, task_priority, task_createTime, task_leadTime)
            _column.taskList.append(_task)

            task_hisList = m.find("historyList")
            if len(task_hisList.findall("history")):
                for v in task_hisList.iter("history"):
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

    # buildXML(board)
    _board = parserXML()
    buildXML(_board)

# TODO Task的Date进行过修改, 解析要重新改动
