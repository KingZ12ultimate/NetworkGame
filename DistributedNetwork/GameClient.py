# imports for the engine
from direct.showbase.ShowBase import ShowBase

from ClientRepository import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode


base.accept("escape", exit)


# Function to put instructions on the screen.
def add_instruction(pos, msg):
    return OnscreenText(text=msg, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
                        parent=base.a2dTopLeft, align=TextNode.ALeft,
                        pos=(0.08, -pos - 0.04), scale=0.06)


# Function to put title on the screen.
def add_title(text):
    return OnscreenText(text=text, pos=(-0.1, 0.09), scale=0.08,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))


title = add_title("Panda3D: Tutorial - Distributed Network (NOT CONNECTED)")
inst1 = add_instruction(0.06, "esc: Close the client")
inst2 = add_instruction(0.12, "See console output")


def set_connected_message():
    title["text"] = "Panda3D: Tutorial - Distributed Network (CONNECTED)"


base.accept("client-ready", set_connected_message)

client = GameClientRepository()
base.accept("space", client.send_roundtrip_to_ai)

base.run()
