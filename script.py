import mdl
from display import *
from matrix import *
from draw import *

def first_pass(commands):
    name = ""
    num_frames = 1
    isVary = False
    for command in commands:
        c = command["op"]
        args = command["args"]
        if c == "basename":
            name = args[0]
        if c == "frames":
            num_frames = int(args[0])
        if c == "vary":
            isVary = True
    if ((num_frames == 1) and (isVary)):
        print("There is no animation involved!")
        exit()
    if name == "":
        print("Set basename to \"frame\"")
        name = "frame"
    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob"s
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass(commands, num_frames):
    frames = [{} for i in range(num_frames)]
    for command in commands:
        c = command["op"]
        args = command["args"]
        if c == "vary":
            start = args[0]
            end = args[1]
            val0 = args[2]
            val1 = args[3]
            if (start >= end):
                print("Frame order in knob is wrong!")
                exit()
            for i in range(start, end + 1):
                value = (i - start) / (end - start) * (val1 - val0) + val0
                frames[i][name] = value
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0, 0, 1];
    ambient = [50, 50, 50]
    light = [[0.5, 0.75, 1],
             [255, 255, 255]]
    color = [0, 0, 0]
    symbols[".white"] = ["constants", {"red": [0.2, 0.5, 0.5],
                                       "green": [0.2, 0.5, 0.5],
                                       "blue": [0.2, 0.5, 0.5]}]
    reflect = ".white"

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    tmp = new_matrix()
    ident(tmp)

    stack = [[x[:] for x in tmp]]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 100
    consts = ""
    coords = []
    coords1 = []
    for i in range(num_frames):
        for command in commands:
            print(command)
            c = command["op"]
            args = command["args"]
            knob = command["knob"]
            knob_value = 1

            if c == "box":
                if command["constants"]:
                    reflect = command["constants"]
                add_box(tmp, args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult(stack[-1], tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = ".white"
            elif c == "sphere":
                if command["constants"]:
                    reflect = command["constants"]
                add_sphere(tmp, args[0], args[1], args[2], args[3], step_3d)
                matrix_mult(stack[-1], tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = ".white"
            elif c == "torus":
                if command["constants"]:
                    reflect = command["constants"]
                add_torus(tmp, args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult(stack[-1], tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = ".white"
            elif c == "line":
                add_edge(tmp, args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult(stack[-1], tmp)
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == "move":
                if (knob and (args[3] in frames[i])):
                    knob_value = frames[i][knob]
                tmp = make_translate(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
                knob_value = 1
            elif c == "scale":
                if (knob and (knob in frames[i])):
                    knob_value = frames[i][knob]
                tmp = make_scale(args[0] * knob_value, args[1] * knob_value, args[2] * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
                knob_value = 1
            elif c == "rotate":
                if (knob and (knob in frames[i])):
                    knob_value = frames[i][knob]
                theta = args[1] * (math.pi / 180)
                if args[0] == "x":
                    tmp = make_rotX(theta * knob_value)
                elif args[0] == "y":
                    tmp = make_rotY(theta * knob_value)
                else:
                    tmp = make_rotZ(theta * knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
                knob_value = 1
            elif c == "push":
                stack.append([x[:] for x in stack[-1]])
            elif c == "pop":
                stack.pop()
            elif c == "display":
                display(screen)
            elif c == "save":
                save_extension(screen, args[0])
