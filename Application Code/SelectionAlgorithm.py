from DataStructure import *
from geopy.geocoders import Nominatim
from LocationNode import LocationNode
from geopy.distance import geodesic
import copy
import geopy
import random
import random
import decimal
import uuid
import sys
import time
from itertools import chain, permutations, combinations
from math import factorial
import time


class SelectionAlgorithm:

    def __init__(self):
        #self.geolocator = Nominatim(user_agent="specify_your_app_name_here")
        self.geolocator = geopy.geocoders.GoogleV3(api_key='')
        self.nodeList = SinglyLinkedList()
        self.nodeSequence = None
        self.totalIteration = 0
        self.totalDistance = 0
        self.start = None;
        self.end = None;
        self.returnNode = None
        self.currentAlgorithm = None;
        self.numberOfNodes = 0
        self.threadSleepTime = 0

    def setThreadSleepTime(self, value):
        if "Fast" in value:
            self.threadSleepTime = 0.01
        elif "Normal" in value:
            self.threadSleepTime = 0.1
        elif "Slow" in value:
            self.threadSleepTime = 0.5
        elif "Disabled" in value:
            self.threadSleepTime = 0
        else:
            self.threadSleepTime = 0.1

    def getTime(self):
        return round(self.end - self.start, 5)

    def getTotalDistance(self):
        return round(self.totalDistance, 2)

    def getSize(self):
        return self.numberOfNodes

    def getIteration(self):
        return self.totalIteration

    def getNodeListAsQueue(self):

        q = Queue()

        for i in range(self.nodeList.size()):
            q.enqueue(self.nodeList.search(i))
        if self.returnNode != None:
            q.enqueue(self.returnNode)
        return q

    def getDistanceFromQueue(self, queue):

        queue = copy.deepcopy(queue)
        distance = 0
        previousNode =  queue.dequeue()

        while not queue.isEmpty():
            nextNode = queue.dequeue()
            distance += self.getDistanceBetweenNode(previousNode,nextNode)
            previousNode = nextNode

        return distance

    def getDistanceBetweenNode(self,node1, node2):

        distance = geodesic([node1.lat, node1.long], [node2.lat, node2.long]).kilometers
        return distance

    def setFirstItemAsReturnNode(self):
        self.returnNode = self.nodeList.search(0)
        self.numberOfNodes = self.nodeList.size()

    def setLastItemAsReturnNode(self):
        self.returnNode = self.nodeList.search(self.nodeList.size()-1)
        self.nodeList.deleteAt(self.nodeList.size()-1)
        self.numberOfNodes = self.nodeList.size() + 1

    def setRandomNodes(self,numberOfNodes,getAddress = False):

        self.nodeList = SinglyLinkedList()

        while numberOfNodes != 0:
            demicalPlace = 1000000

            #bottom top
            #left right
            rndlat = random.randrange(1.280 * demicalPlace, 1.424 * demicalPlace) / demicalPlace
            rndlong = random.randrange(103.718 * demicalPlace, 103.999 * demicalPlace) / demicalPlace

            if getAddress == True:
                while True:
                    try:
                        location = self.geolocator.reverse([rndlat, rndlong], exactly_one=True)

                    except:
                        print("Exception")

                    if location == None or location.address == "Unnamed Road, Singapore" or "Pulau Ubin" in location.address or "Jln Noordin" in location.address :
                        rndlat = random.randrange(1.280 * demicalPlace, 1.424 * demicalPlace) / demicalPlace
                        rndlong = random.randrange(103.718 * demicalPlace, 103.999 * demicalPlace) / demicalPlace
                    else:
                        break

                self.setNode("{}".format(location.address),"{}".format(location.address), location.latitude, location.longitude)
            else:
                self.setNode("Node {}".format(self.nodeList.size() + 1),"Node {}".format(self.nodeList.size() + 1), rndlat, rndlong)

            numberOfNodes-= 1

    def setNode(self, term, actualAddress = "", lat = 0,long = 0):
        if lat == 0 and long == 0:

            for i in range(self.nodeList.size()):
                node = self.nodeList.search(i)
                if node.name == term and i != 0: #ignore first node as user may want to loop back
                    return False

            try:
                location = self.geolocator.geocode(term)
            except:
                return False

            if location == None:
                return False
            else:
                actualAddress = location.address

            lat = location.latitude
            long = location.longitude

        self.nodeList.insertAtTail(LocationNode(self.nodeList.size()+1,actualAddress, term, lat, long))
        return True

    def reset(self):

        self.nodeSequence = Queue()
        self.totalIteration = 0
        self.totalDistance = 0
        self.start = None;
        self.end = None;
        self.currentAlgorithm = None;


    def printSequence(self,displaySequence = True):
        tempQueue = copy.deepcopy(self.nodeSequence)
        if displaySequence:
            print("Algrothim: ", self.currentAlgorithm)
            print("Total Nodes: ", self.nodeSequence.size()-1)
            print("Total Iterations: ",self.iteration)
            print ("Total Distance: ", round(self.totalDistance,2), "Km")
            print ("Time Taken: ",round(self.end - self.start,5),"s")

            i = 1
            print()
            print("Node Sequence")
            while not tempQueue.isEmpty():
                node = tempQueue.dequeue()
                print (i,node.name)
                i+=1
            print()

    def nearestNeighbour(self, progress_callback = False):

        self.reset()
        self.start = time.time();
        self.currentAlgorithm = "Nearest Neighbour"

        nodeSequence = Queue()
        leftOverNodes = copy.deepcopy(self.nodeList)
        iteration  = 0

        # INSERT Starting Node From First item in the list
        nodeSequence.enqueue(leftOverNodes.search(0))
        leftOverNodes.deleteAt(0)
        totalDistance = 0

        while (leftOverNodes.size()):
            previousNode = nodeSequence.peekLast()
            nearestNodeIndex = 0
            nearestNode = None
            nearestDistance = None

            for i in range(leftOverNodes.size()):
                selectedNode = leftOverNodes.search(i)
                selectedNodeDistance = self.getDistanceBetweenNode(selectedNode,previousNode)

                if(nearestDistance == None or nearestDistance > selectedNodeDistance):
                    nearestNode = selectedNode
                    nearestDistance = selectedNodeDistance
                    nearestNodeIndex = i

                self.end = time.time()
                tempnodeSequence = copy.deepcopy(nodeSequence)
                tempnodeSequence.enqueue(selectedNode)

                if self.threadSleepTime:
                    self.end = time.time()
                    self.totalDistance = totalDistance
                    self.totalIteration = iteration
                    self.nodeSequence = tempnodeSequence
                    progress_callback.emit()
                    time.sleep(self.threadSleepTime)

            iteration+= 1
            nodeSequence.enqueue(nearestNode)
            leftOverNodes.deleteAt(nearestNodeIndex)
            totalDistance += nearestDistance


        # Insert first node as last node to form a tour

        if self.returnNode != None:
            totalDistance += self.getDistanceBetweenNode(nodeSequence.peekLast(), self.returnNode)
            nodeSequence.enqueue(self.returnNode)

        self.end = time.time()
        self.totalDistance = totalDistance
        self.nodeSequence = nodeSequence
        self.totalIteration = iteration

        if self.threadSleepTime:
            progress_callback.emit()

    def bruteForce(self,progress_callback = False):
        self.reset()
        self.start = time.time();
        self.currentAlgorithm = "Brute Force"

        nodeSequence = Queue()
        self.leftOverNodes = copy.deepcopy(self.nodeList)

        mainQueue = Queue()
        subQueue = Queue()
        iteration = 0

        subQueue.enqueue(self.leftOverNodes.search(0))
        self.leftOverNodes.deleteAt(0)
        mainQueue.enqueue(subQueue)

        # Generate All Possible Instant Till All nodes are reached
        while mainQueue.isEmpty() == False:

            iterationComplete = True
            subQueue = mainQueue.dequeue()

            for i in range(self.leftOverNodes.size()):

                if self.threadSleepTime:
                    self.end = time.time()
                    progress_callback.emit()
                    time.sleep(self.threadSleepTime)

                selectedNode = self.leftOverNodes.search(i)

                if not subQueue.nodeInQueue(selectedNode):
                    subQueueCopy = copy.deepcopy(subQueue)
                    subQueueCopy.enqueue(selectedNode)
                    mainQueue.enqueue(subQueueCopy)
                    iterationComplete = False


            if iterationComplete:
                mainQueue.enqueue(subQueue)
                break

        nearestSubQueueIteration = None
        nearestSubQueueDistance = None

        while not mainQueue.isEmpty():
            iteration += 1

            totalDistance = 0
            subQueue = mainQueue.dequeue()
            tempSubQueue = copy.deepcopy(subQueue)
            previousNode = tempSubQueue.dequeue()

            while not tempSubQueue.isEmpty():
                nextNode = tempSubQueue.dequeue()
                totalDistance += self.getDistanceBetweenNode(previousNode, nextNode)
                previousNode = nextNode
                
            #Add return node
            if self.returnNode != None:
                nextNode = copy.deepcopy(self.returnNode)
                totalDistance += self.getDistanceBetweenNode(previousNode, nextNode)
                subQueue.enqueue(nextNode)

            if nearestSubQueueDistance is None or nearestSubQueueDistance > totalDistance:
                nearestSubQueueIteration = subQueue
                nearestSubQueueDistance = totalDistance

            if self.threadSleepTime:
                self.end = time.time()
                self.totalDistance = totalDistance
                self.totalIteration = iteration
                self.nodeSequence = subQueue
                progress_callback.emit()
                time.sleep(self.threadSleepTime)


        self.end = time.time();
        self.nodeSequence = nearestSubQueueIteration
        self.totalDistance = nearestSubQueueDistance
        self.totalIteration = iteration

        if self.threadSleepTime:
            progress_callback.emit()

    def twoOpt(self,progress_callback = False):
        self.reset()
        self.currentAlgorithm = "Two Opt"
        self.start = time.time()
        self.nodeSequence = self.nodeList.convertToQueue() # treat as best
        self.nodeSequence.enqueue(copy.deepcopy(self.returnNode))
        self.totalDistance = self.getDistanceFromQueue(self.nodeSequence)

        improved = True

        while improved:
            improved = False
            for i in range(1, self.nodeSequence.size() - 1):
                for i2 in range(i + 1, self.nodeSequence.size() - 1):

                    newRoute = copy.deepcopy(self.nodeSequence)
                    newRoute.swapNodes(i,i2)
                    distanceOfNewRoute = self.getDistanceFromQueue(newRoute)

                    if distanceOfNewRoute <= self.totalDistance:
                        self.end = time.time();
                        self.totalDistance = distanceOfNewRoute
                        self.totalIteration += 1
                        self.nodeSequence = newRoute
                        improved = True

                        if self.threadSleepTime:
                            progress_callback.emit()
                            time.sleep(self.threadSleepTime)

        self.end = time.time();


    def branchAndBound(self,progress_callback = False):

        self.reset()
        self.start = time.time();
        self.currentAlgorithm = "Branch And Bound"
        self.leftOverNodes = copy.deepcopy(self.nodeList)

        mainQueue = Queue()
        subQueue = Queue()

        self.nodeSequence = self.nodeList.convertToQueue()  # treats user defined node sequence as the best sequence

        if self.returnNode != None:
            self.nodeSequence.enqueue(copy.deepcopy(self.returnNode))

        self.totalDistance = self.getDistanceFromQueue(self.nodeSequence)

        subQueue.enqueue(self.leftOverNodes.search(0))
        self.leftOverNodes.deleteAt(0)
        mainQueue.enqueue(subQueue)

        bestDistance = 0

        # Generate All Possible Instant Till All nodes are reached
        bestSequence = self.nodeSequence
        bestDistance = self.totalDistance

        while mainQueue.isEmpty() == False:

            subQueue = mainQueue.dequeue()

            for i in range(self.leftOverNodes.size()):

                selectedNode = copy.deepcopy(self.leftOverNodes.search(i))

                if self.threadSleepTime:
                    self.end = time.time();
                    progress_callback.emit()
                    time.sleep(self.threadSleepTime)

                if not subQueue.nodeInQueue(selectedNode):

                    subQueueCopy = copy.deepcopy(subQueue)
                    lastNode = subQueueCopy.peekLast()

                    subQueueDistance = lastNode.accumulatedDistance

                    subQueueDistance += self.getDistanceBetweenNode(lastNode, selectedNode)
                    selectedNode.accumulatedDistance = subQueueDistance
                    subQueueDistance += self.getDistanceBetweenNode(selectedNode,self.returnNode)  # add distance of returning node
                    subQueueCopy.enqueue(selectedNode)

                    if self.threadSleepTime:
                        self.end = time.time();
                        progress_callback.emit()
                        time.sleep(self.threadSleepTime)

                    if bestSequence.size() == subQueueCopy.size()+1:

                        if self.returnNode != None:
                            subQueueCopy.enqueue(copy.deepcopy(self.returnNode))

                        self.totalIteration += 1
                        self.nodeSequence = subQueueCopy
                        self.totalDistance = subQueueDistance

                        if bestDistance > subQueueDistance:
                            bestSequence = subQueueCopy
                            bestDistance = subQueueDistance
                        continue  # break branch when branch reaches reach its max height

                        if self.threadSleepTime:
                            self.end = time.time();
                            progress_callback.emit()
                            time.sleep(self.threadSleepTime)

                    elif subQueueDistance > bestDistance :
                        continue  # break off branches that are greater than the best case

                    mainQueue.enqueue(subQueueCopy)


        self.end = time.time();
        self.totalDistance = bestDistance
        self.nodeSequence = bestSequence

        if self.threadSleepTime:
            progress_callback.emit()





