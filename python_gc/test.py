import sys
# import objgraph

a = ['a', 'b', 'c']
print(sys.getrefcount(a))  # print 2
b = a 
print(b is a)              # print True
print(sys.getrefcount(b))  # print 3
c = a
del c
print(sys.getrefcount(a))  # print 3
del a
print(sys.getrefcount(b))  # print 2

def foo(b):
    # objgraph.show_backrefs([b], filename='./sample-graph.png')
    # objgraph.show_refs(b, refcounts=True, filename='roots.png')
    print(sys.getrefcount(b))  # print 5

foo(b)
print(sys.getrefcount(b))      # print 2