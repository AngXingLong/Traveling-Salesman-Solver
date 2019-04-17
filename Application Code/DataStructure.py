import collections
import copy
class SinglyListNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def getNodeFromIndex(self, index):
        temp = self.head
        prev = None
        counter = 0
        while temp is not None and counter < index:
            prev = temp
            temp = temp.next
            counter += 1

        if temp is None:
            return
        else:
            return temp

    def search(self, index):
        node = self.getNodeFromIndex(index)

        if node == None:
            return
        else:
            return node.data


    def insertAtHead(self, value):

        node = SinglyListNode(value)

        if self.head is None:
            self.head = node
        else:
            node.next = self.head
            self.head = node

    def insertAtTail(self, value):

        node = SinglyListNode(value)

        if (self.head  == None):
            self.head = node
        else:
            current = self.head
            while (current.next != None):
                current = current.next
            current.next = node

    def delete(self, value):
        prev = None
        temp = self.head

        while temp != None and temp.data != value:
            prev = temp
            temp = temp.next

        if temp == self.head:
            self.deleteAtHead()

        elif temp != None:
            prev.next = temp.next
            del temp

        else:
            print('Value ', value, ' cannot be found')

    def deleteAt(self, index):
        temp = self.head
        prev = None
        counter = 0
        while temp is not None and counter < index:
            prev = temp
            temp = temp.next
            counter += 1

        else:
            if prev is None:
                self.head = temp.next
            else:
                prev.next = temp.next
            del temp

    def deleteAtHead(self):
        temp = self.head
        self.head = self.head.next
        del temp

    def printList(self):
        print("Current list content:")
        temp = self.head
        while temp is not None:
            print(temp.data)
            temp = temp.next

    def size(self):
        temp = self.head
        size = 0
        while temp is not None:
            size += 1
            temp = temp.next
        return size

    def convertToQueue(self):
        q = Queue()
        for i in range(self.size()):
            q.enqueue(copy.deepcopy(self.search(i)))
        return q

class Queue:
    def __init__(self):
        self.q = SinglyLinkedList()

    def enqueue(self, value):
        self.q.insertAtTail(value)

    def printQueue(self):
        self.q.printList()

    def dequeue(self):
        value = self.q.search(0)
        self.q.deleteAt(0)
        return value

    def isEmpty(self):
        return self.q.size() == 0

    def peek(self):
        return self.q.search(0)

    def peekAt(self, index):
        return self.q.search(index)

    def peekLast(self):
        return self.q.search(self.q.size()-1)

    def inQueue(self,value):
        for i in range(self.q.size()):
            if self.q.search(i) == value:
                return True
        return False

    def nodeInQueue(self,node):
        for i in range(self.q.size()):
            if self.q.search(i).id == node.id:
                return True
        return False

    def size(self):
        return self.q.size()

    def swapNodes(self,index,index2):

        tempNode = self.q.getNodeFromIndex(index)
        tempNode2 = self.q.getNodeFromIndex(index2)
        tempNodeData = copy.deepcopy(tempNode.data)
        tempNode.data = tempNode2.data
        tempNode2.data = tempNodeData


class Stack:
    def __init__(self):
        self.data = []

    def push(self, value):
        self.data.append(value)

    def pop(self):
        return self.data.pop()

    def peek(self):
        return self.data[len(self.data)-1];

    def peekAt(self,i):
        return self.data[i];

    def size(self):
        return len(self.data)

    def copyFrom(self, aStack):
        for x in aStack.data:
            self.push(x)

    def toString(self):
        return " ".join(self.data)

    def inStack(self,value):
        for x in self.data:
            if x == value:
                return True
        return False

    def printStack(self):
        print (self.data)

    def isEmpty(self):
        return len(self.data) == 0
