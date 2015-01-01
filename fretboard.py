#!/usr/bin/python

import argparse

acc_list = ["b", "", "#"]
all_base_notes = []
all_notes = []
sharps = []
flats = []
fretboard = []
preferences = {}
help_opts = {}
scale_forms = []
chord_forms = []

def char_range(c1, c2):
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

all_base_notes = list(char_range('A', 'G'))

def pivotList(thelist, newstart):
    if newstart < 0:
        return []
    if newstart == 0:
        newlist = []
        for x in thelist:
            newlist.append(x)
        return newlist
    newList = []
    for i in range(newstart-1, len(thelist)):
        newList.append(thelist[i])
    for i in range(0, newstart-1):
        newList.append(thelist[i])
    return newList

def baseNote(someNote):
    return someNote[0]

class Fretboard:
    strings = []
    distance = 0

    def __init__(self, distance=15):
        self.strings = []
        self.distance = distance
        stringf = lambda x: pivotList(sharps,sharps.index(x)+1) + pivotList(sharps,sharps.index(x)+1)[0:distance-12]
        stringE = stringf('E')
        stringA = stringf('A')
        stringD = stringf('D')
        stringG = stringf('G')
        stringB = stringf('B')
        self.strings.append(stringE)
        self.strings.append(stringB)
        self.strings.append(stringG)
        self.strings.append(stringD)
        self.strings.append(stringA)
        self.strings.append(stringE)

    def __str__(self):
        res = '\t'.join(map(str,range(0, self.distance))) + '\n'
        for i in self.strings:
            res += '\t'.join(i) + '\n'
        return res


class Note:
    name = ""
    acc = ""
    def __init__(self, note_name, note_acc=""):
        self.name = note_name.upper()
        self.acc = note_acc
    def __str__(self):
        res = self.name + self.acc
        return res

class Scale:
    root = ""
    keysig = ""
    ident = ""
    notes = []
    def __init__(self, root="C", ident="major", notes=[]):
        self.root = root
        if ident != "major":
            self.notes = getValidScale(notes)
        else:
            self.notes = getValidScale(scale(self.root))
        self.keysig = findKeySig(self.notes)
        self.ident = ident
    def __str__(self):
        res = str(self.notes) + '\t' + str(self.keysig)
        return res
    def harmMinorScale(self):
        minorNotes = pivotList(self.notes, 6)
        minorNotes[-1] = raiseNote(minorNotes[-1],1)
        return Scale(self.root, ident="harmonic minor", notes=minorNotes)
    def natMinorScale(self):
        minorNotes = pivotList(self.notes, 6)
        return Scale(self.root, ident="natural minor", notes=minorNotes)
    def melMinorScale(self):
        minorNotes = pivotList(self.notes, 0)
        minorNotes[2] = raiseNote(minorNotes[2], -1)
        return Scale(self.root, ident="melodic minor", notes=minorNotes)
    def minorPentaScale(self):
        minorNotes = pivotList(self.notes, 6)
        minorNotes.pop(5)
        minorNotes.pop(1)
        return Scale(self.root, ident="minor pentatonic", notes=minorNotes)
    def majorPentaScale(self):
        pentaNotes = list(self.notes)
        pentaNotes.pop(6)
        pentaNotes.pop(3)
        return Scale(self.root, ident="major pentatonic", notes=pentaNotes)
    def majorChord(self):
        chordNotes = list(self.notes)
        chordNotes = [chordNotes[0], chordNotes[2], chordNotes[4]]
        return Scale(self.root, ident="major chord", notes=chordNotes)
    def minorChord(self):
        chordNotes = list(self.notes)
        chordNotes = [chordNotes[0], raiseNote(chordNotes[2], -1), chordNotes[4]]
        return Scale(self.root, ident="minor chord", notes=chordNotes)
    def augChord(self):
        chordNotes = list(self.notes)
        chordNotes = [chordNotes[0], chordNotes[2], raiseNote(chordNotes[4], 1)]
        return Scale(self.root, ident="augmented chord", notes=chordNotes)
    def dimChord(self):
        chordNotes = list(self.notes)
        chordNotes = [chordNotes[0], raiseNote(chordNotes[2], -1), raiseNote(chordNotes[4], -1)]
        return Scale(self.root, ident="diminished chord", notes=chordNotes)
    def chord(self, noteList, chordIdent):
        chordNotes = noteList
        return Scale(self.root, ident=chordIdent, notes=chordNotes)
    def genChord(self, intervList, chordIdent):
        masterNotes = getValidScale(scale(self.root))
        newNotes = []
        for interv in intervList:
            newNote = masterNotes[int(interv[0])-1]
            if len(interv) > 1 and interv[1] == '#':
                newNote = raiseNote(newNote, 1)
            elif len(interv) > 1 and interv[1] == 'b':
                newNote = raiseNote(newNote, -1)
            newNotes.append(newNote)
        return Scale(self.root, ident=chordIdent, notes=newNotes)


def raiseNote(original, steps):
    index = 0
    if isSharp(original) or not isFlat(original):
        index = sharps.index(original)
        return sharps[index+steps]
    else:
        index = flats.index(original)
        return flats[index+steps]

def showNotes(note_list):
    '-'.join(note_list)

def switchAcc(note):
    note2 = note
    if len(note) > 1:
        if note[1] == '#':
            try:
                note2 = all_base_notes[all_base_notes.index(note[0]) + 1] + 'b'
            except IndexError:
                note2 = "Ab"
        else:
            note2 = all_base_notes[all_base_notes.index(note[0]) - 1] + '#'
    return note2

def isSharp(note):
    if len(note) > 1:
        if note[1] == '#':
            return True
        else:
            return False
    return False

def isFlat(note):
    if len(note) > 1:
        if note[1] == 'b':
            return True
        else:
            return False
    return False

def scale(note, mode=1):
    sharplist = []
    if isFlat(note):
        note = switchAcc(note)
    sharplist = pivotList(sharps, sharps.index(note)+1)
    scale = []
    pattern = [2, 2, 1, 2, 2, 2, 1]
    pos = 0
    for i in pattern:
        scale.append(sharplist[pos])
        pos += i
    scale = pivotList(scale, mode)
    return scale

def validateScale(scale):
    for i in range(0, len(scale)-1):
        if scale[i][0] == scale[i+1][0]:
            return False
    return True

def getValidScale(scale):
    if validateScale(scale):
        return scale
    else:
        return map(switchAcc, scale)

def findKeySig(scale):
    count = 0
    sigchar = ''
    for note in scale:
        if len(note) > 1:
            count+=1
            sigchar = note[1]
    return str(count)+sigchar

def parseChord(chordName):
    chordBase = chordName[:3]    #maj/min/aug/dim/sus/whatever
    chordTonesP = 0
    if chordBase == 'sus':
        if int(chordName[3]) not in [2, 4]:
            print 'Error parsing chord name: invalid added tone'
            return
        else:
            chordTonesP = chordName[3]
    elif chordBase in ['maj', 'min', 'aug', 'dim']:
        if int(chordName[3]) not in [7, 9, 11, 13]:
            print 'Error parsing chord name: invalid added tone'
            return
        else:
            chordTonesP = chordName[3]
#TODO <-- finish this here i guess
    elif chordBase == '5':      #power chord!!
        chordTonesP

def parseChord2(chordName):
    noteList = ['1']
    if chordName == '5':
        noteList.append('5')
    elif chordName[:3] == 'sus':
        if chordName[3] == '4':
            noteList.append('4')
        elif chordName[3] == '2':
            noteList.append('2')
        noteList.append('5')
    elif chordName[:3] == 'dim':  #assume dim7
        noteList.append('3b')
        noteList.append('5b')
        noteList.append('7b')
    elif chordName[:3] == 'aug':
        noteList.append('5#')
        noteList.append('3')
        if '7' in chordName:
            noteList.append('7')
    elif chordName[:3] == 'min':
        noteList.append('3b')
        noteList.append('5')
        if '7' in chordName:
            noteList.append('7')
    elif chordName[:3] == 'dom':
        noteList.append('3')
        noteList.append('5')
        noteList.append('7b')
    elif chordName[:3] == 'maj':
        noteList.append('3')
        noteList.append('5')
        if '7' in chordName:
            noteList.append('7')
    else:
        return ['invalid']
    return noteList



def init():
    scale_forms.append('minor pentatonic')
    scale_forms.append('major pentatonic')
    scale_forms.append('major')
    scale_forms.append('minor')
    scale_forms.append('melodic minor')
    scale_forms.append('natural minor')
    scale_forms.append('harmonic minor')
    chord_forms.append('maj(7)')
    chord_forms.append('min(7)')
    chord_forms.append('aug(7)')
    chord_forms.append('dom')
    chord_forms.append('dim')
    chord_forms.append('sus2/sus4')

    for i in all_base_notes:
        for acc in acc_list:
            temp = i + acc
            if temp != 'Cb' and temp != 'Fb' and temp != 'E#' and temp != 'B#':
                all_notes.append(i + acc)

    for i in all_base_notes:
        sharps.append(i)
        if i != 'B' and i != 'E':
            sharps.append(i + '#')

    for i in all_base_notes:
        flats.append(i)
        if i != 'C' and i != 'F':
            flats.append(i + 'b')

def fretboardScale(fb, scalestuff):
    for string in fb.strings:
        if string[0] != '0':
            for note in string:
                if scalestuff.count(note) == 0 and scalestuff.count(switchAcc(note)) == 0:
                    string[string.index(note)] = ""
    return fb

def showGuitarScale(scalex, fret_count):
    inp_scale = scalex.notes
    print "{0} {2} {1}".format(inp_scale, scalex.ident, scalex.keysig)
    fret = Fretboard(fret_count)
    res = fretboardScale(fret, inp_scale)
    print res,"\n\n"

def test():
    print 'Testing base scales'
    for asdf in all_notes:
        rawr = Scale(asdf)
        valid = getValidScale(rawr.notes)
        print '{0}\t{1}'.format(valid,findKeySig(valid))

def helpOpts():
    help_opts['q'] = 'quit'
    help_opts['h'] = 'help'
    help_opts['p'] = 'change preferences'
    help_opts['k'] = 'look up (comma-separated for multiple notes)'
    help_opts['l'] = 'list scales'
    help_opts['ch'] = 'show chord'

def getHelp(option):
    if option == 'h' or option == 'H':
        for k,v in help_opts.iteritems():
            print ' {0}\t\t{1}'.format(k, v)
    elif option == 'ch':
        x = raw_input('Root note of chord > ')
        y = parseChord2(preferences['chord_type'])
        print y
        print showGuitarScale(Scale(x).genChord(y, preferences['chord_type']), preferences['length'])
    elif option == 'p':
        x = raw_input("Scale/chord type or fret count you would like to change to\n > ")
        if x in scale_forms:
            preferences['scale_type'] = x
        elif x in chord_forms or parseChord2(x) != ['invalid']:
            preferences['chord_type'] = x
        else:
            try:
                asdf = int(x)
                if asdf in range(1, 25):
                    preferences['length'] = asdf
            except ValueError:
                print "Sorry, that's not valid"
    elif option == 'k':
        x = raw_input('Notes to look up > ')
        x = x.split(',')
        correct_scales = []
        for scale in all_notes:
            temp_scale = Scale(scale)
            if set(x).issubset(set(temp_scale.notes)):
                    correct_scales.append(temp_scale.root)
        print 'Notes are in: ',' '.join(correct_scales)
    elif option == 'l':
        print " Scales:"
        for x in scale_forms:
            print "  ", x
        print " Chords:"
        for x in chord_forms:
            print "  ", x

def parsePrefs(prefs):
    pass

def menu(prefs):
    helpOpts()
    print "Loading default preferences..."
    print "Remember, just typing \"h\" and pressing Enter shows the help!"
    if prefs == "":
        preferences['scale_type'] = 'major'
        preferences['length'] = 14
        preferences['chord_type'] = 'maj'
    else:
        with open(prefs) as f:
            for line in f:
                parts = line.split()
                preferences[parts[0]] = parts[1]
    quit = False
    while not quit:
        print "Current mode: {0} {1}".format(preferences['scale_type'], preferences['length'])
        inp = raw_input("Input scale\n > ")
        if inp == 'q' or inp == 'Q':
            quit = True
            break
        elif str.lower(inp) in help_opts.iterkeys():
            getHelp(str.lower(inp))
        elif inp == 'q' or inp == 'Q':
            quit = True
            break
        elif all_notes.count(inp) > 0:
            inp_scale = Scale(inp)
            ln = preferences['length']
            if preferences['scale_type'] == 'major':
                showGuitarScale(inp_scale, ln)
            else:
                scale_parts = preferences['scale_type'].split()
                if scale_parts[0] == 'major':
                    if scale_parts[1] == 'pentatonic':
                        showGuitarScale(inp_scale.majorPentaScale(), ln)
                    if scale_parts[1] == 'chord':
                        showGuitarScale(inp_scale.majorChord(),ln)
                elif scale_parts[0] == 'minor':
                    if len(scale_parts) == 1:
                        showGuitarScale(inp_scale.natMinorScale(), ln)
                    elif scale_parts[1] == 'pentatonic':
                        showGuitarScale(inp_scale.minorPentaScale(), ln)
                    elif scale_parts[1] == 'chord':
                        showGuitarScale(inp_scale.minorChord(), ln)
                elif scale_parts[0] == 'diminished' or scale_parts[0] == 'dim':
                    if scale_parts[1] == 'chord':
                        showGuitarScale(inp_scale.dimChord(), ln)
                elif scale_parts[0] == 'augmented' or scale_parts[0] == 'aug':
                    if scale_parts[1] == 'chord':
                        showGuitarScale(inp_scale.augChord(), ln)
                else:
                    if scale_parts[0] == 'harmonic' and scale_parts[1] == 'minor':
                        showGuitarScale(inp_scale.harmMinorScale(), ln)
                    elif scale_parts[0] == 'relative' and scale_parts[1] == 'minor':
                        showGuitarScale(inp_scale.relMinorScale(), ln)
                    elif scale_parts[0] == 'natural' and scale_parts[1] == 'minor':
                        showGuitarScale(inp_scale.natMinorScale(), ln)

def main():
    parser = argparse.ArgumentParser(description='Shows notes for some scale on a virtual guitar fretboard') #TODO: maybe need more description as features get added?
    parser.add_argument('-s',  '--scale', nargs='?', default=None, required=False, help='The scale to be displayed')
    parser.add_argument('-f', '--frets', nargs='?', default=None, required=False, help='The number of frets to show')
    parser.add_argument('-i', '--interactive', nargs='?', default="", const=None, help='If non-None, will start in interactive mode')
    args = parser.parse_args()

    init()
    if args.interactive != None:
        menu(args.interactive)
    elif args.scale == None:
        x = raw_input("Scale?")
        if False:
#else:
            x = args.scale
            if args.frets == None:
                length = int(raw_input("Number of frets?"))
            else:
                length = int(args.frets)
            blah = Scale(x)

            showGuitarScale(blah, length)
            Hmin = blah.harmMinorScale()
            showGuitarScale(Hmin, length)
            Nmin = blah.natMinorScale()
            showGuitarScale(Nmin, length)
            Mmin = blah.melMinorScale()
            showGuitarScale(Mmin, length)
            minPenta = blah.minorPentaScale()
            showGuitarScale(minPenta, length)
            majPenta = blah.majorPentaScale()
            showGuitarScale(majPenta, length)

if __name__ == "__main__":
    main()
