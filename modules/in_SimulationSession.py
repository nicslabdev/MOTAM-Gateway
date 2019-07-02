#     print(data)

#     # this variables will control the sample frequency
#     currentSimulatedTime = None
#     lastSimulatedTime = data["time"]
    
#     try:
#         # send the first json
#         sock.sendall (json.dumps(data["json"]).encode())

#         # this will stop the execution with keyboard interrupt
#         while not sendDataThreadStop.is_set():
#             # if this is the first iteration...
#             if currentSimulatedTime is None:
#                 # take the data unit from the queue
#                 data = dbParsedQueue.get()
#                 currentSimulatedTime = data["time"]
            
#             # if this isn't the first iteration
#             else:
#                 time.sleep(currentSimulatedTime-lastSimulatedTime)

#                 # send the next json
#                 sock.sendall (json.dumps(data["json"]).encode())
                
#                 try:
#                     # take the data unit from the queue
#                     data = dbParsedQueue.get(block=False)
#                     lastSimulatedTime = currentSimulatedTime
#                     currentSimulatedTime = data["time"]
                    
#                 except queue.Empty:
#                     pass

#     # if the other side close the socket...
#     except socket.error:
#         pass