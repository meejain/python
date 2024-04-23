import socket
print(socket.gethostname())
if 'local' in socket.gethostname():
  print('success')
else:
  print("failure")

