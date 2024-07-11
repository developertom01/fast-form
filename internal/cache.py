import pylru

# Replace this with a distributed cache on the server in the future
cache = pylru.lrucache(200)