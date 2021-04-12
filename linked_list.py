
class Node:
    def __init__(self, datum):
        self.datum = datum
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.len = 0

        self._tmp = None

    def add(self, datum):
        if self.head:
            self._tmp.next = Node(datum)
            self._tmp = self._tmp.next
        else:
            self.head = Node(datum)
            self._tmp = self.head
        self.len += 1

    def remove_last(self):
        if self.head == None:
            return

        if self.head.next == None:
            self.head = None
            return

        head = self.head
        while head.next.next:
            head = head.next
        head.next = None

    def remove(self, node):
        if node.next:
            node.datum = node.next.datum
            node.next = node.next.next
        else:
            self.remove_last()
        self.len -= 1
