from collections import defaultdict

class Node:
    def __init__(self):
        self.level = 0
        self.content = ''

class TocTree(object):
    def __init__(self, toc):
        self.toc = toc
        self.graph = defaultdict(list)
        self.stack = []

    def get_node(self, toc_obj):
        node = Node()
        node.content = toc_obj[1]
        node.level = toc_obj[0]

    def construct_tree(self):
        search_map = dict()
        toc_length = len(self.toc)
        for index in xrange(toc_length):
            if not len(self.stack):
                self.stack.append(self.toc[index])
            elif self.stack[-1][0] < self.toc[index][0]:
                search_map[self.toc[index][1]] = self.stack[-1][1]
                self.stack.append(self.toc[index])
            elif self.stack[-1][0] == self.toc[index][0]:
                self.stack.pop()
                search_map[self.toc[index][1]] = self.stack[-1][1]
                self.stack.append(self.toc[index])
            else:
                self.stack.pop()
        with open('output_tree.json', 'w') as fp:
            import json
            json.dump(search_map, fp, indent=4)


