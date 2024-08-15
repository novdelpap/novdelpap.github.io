import hytek_parser
from hytek_parser.hy3.enums import Course
import attrs
from pyscript import document
from js import Uint8Array
from io import StringIO
from io import BytesIO
import base64
import zipfile
import hashlib

VERBOSE = True

def format_auto_quals(aq,k,pool):
    vs = vf = ""
    saq = sorted(aq, key=lambda x: x.converted_seed_time)
    if k > 0:
     vs += "\tAUTOMATIC QUALIFIERS\n"
     for entry in saq:
        for line in pool[entry.event_number][entry.swimmers[0].last_name][entry.swimmers[0].first_name]['%02d%02d%04d' % (entry.swimmers[0].date_of_birth.month, entry.swimmers[0].date_of_birth.day, entry.swimmers[0].date_of_birth.year)]:
            vf += line
        vs += "\t(AUTO) %s, %s %s, %s%s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time, 'S' if entry.converted_seed_time_course == Course.SCM else 'Y')
    return (vs, vf)

def format_k_wildcards(k,out,wl,pool):
    vs = vf = ""
    fwl = filter(lambda x: type(x.converted_seed_time) == float, wl)
    swl = sorted(fwl, key=lambda x: x.converted_seed_time)
    if k > 0:
     vs += "\t%d WILDCARDS\n" % k
     for entry in swl[:k]:
        for line in pool[entry.event_number][entry.swimmers[0].last_name][entry.swimmers[0].first_name]['%02d%02d%04d' % (entry.swimmers[0].date_of_birth.month, entry.swimmers[0].date_of_birth.day, entry.swimmers[0].date_of_birth.year)]:
            vf += line
        vs += "\t(WILDCARD) %s, %s %s, %s%s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time, 'S' if entry.converted_seed_time_course == Course.SCM else 'Y')
    if out > 0:
     vs += "\tfirst %d OUT\n" % out
     dropped = filter(lambda x: not (type(x.converted_seed_time) == float), wl)
     for entry in swl[k:k+out]:
        for line in pool[entry.event_number][entry.swimmers[0].last_name][entry.swimmers[0].first_name]['%02d%02d%04d' % (entry.swimmers[0].date_of_birth.month, entry.swimmers[0].date_of_birth.day, entry.swimmers[0].date_of_birth.year)][:-1]:
            vf += line
        vs += "\t(OUT) \t%s, %s %s, %s%s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time, 'S' if entry.converted_seed_time_course == Course.SCM else 'Y')
        #for entry in dropped:
        #    for line in pool[entry.event_number][entry.swimmers[0].last_name][entry.swimmers[0].first_name]['%02d%02d%04d' % (entry.swimmers[0].date_of_birth.month, entry.swimmers[0].date_of_birth.day, entry.swimmers[0].date_of_birth.year)][:-1]:
        #        vf += line
        #    vs += "\t(OUT) \t%s, %s %s, %s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time)
    return (vs, vf)

def accumulate_entries(hyfile, accum):
        running_accum = []
        for line in open(hyfile).readlines():
                if line[0:2] == 'C1':
                      race = first_name = last_name = birthday = ''
                      if len(running_accum) == 4:
                              race = int(running_accum[3][38:43])
                              first_name = running_accum[2][28:48].strip()
                              last_name = running_accum[2][8:28].strip()
                              birthday = running_accum[2][88:96]  
                      elif len(running_accum) == 3 and running_accum[0][:2] == 'C1':
                              race = int(running_accum[2][38:43])
                              first_name = running_accum[1][28:48].strip()
                              last_name = running_accum[1][8:28].strip()
                              birthday = running_accum[1][88:96]
                      if race not in accum:
                            accum[race] = {}
                      if last_name not in accum[race]:
                            accum[race][last_name] = {}
                      if first_name not in accum[race][last_name]:
                            accum[race][last_name][first_name] = {}
                      if birthday not in accum[race][last_name][first_name]:
                            accum[race][last_name][first_name] = {}
                      accum[race][last_name][first_name][birthday] = running_accum
                      
                      running_accum = []
                running_accum.append(line)

        race = first_name = last_name = birthday = ''
        if len(running_accum) == 4:
            race = int(running_accum[3][38:43])
            first_name = running_accum[2][28:48].strip()
            last_name = running_accum[2][8:28].strip()
            birthday = running_accum[2][88:96]
        elif len(running_accum) == 3 and running_accum[0][:2] == 'C1':
            race = int(running_accum[2][38:43])
            first_name = running_accum[1][28:48].strip()
            last_name = running_accum[1][8:28].strip()
            birthday = running_accum[1][88:96]
        if race not in accum:
            accum[race] = {}
        if last_name not in accum[race]:
            accum[race][last_name] = {}
        if first_name not in accum[race][last_name]:
            accum[race][last_name][first_name] = {}
        if birthday not in accum[race][last_name][first_name]:
            accum[race][last_name][first_name] = {}
        accum[race][last_name][first_name][birthday] = running_accum
        return accum

#TODO, warn if there are more than three files
#TODO, more gracefully handle bad zip
def merge_hyfiles(the_arg):

    num_auto = int(document.getElementById('num_auto').value)
    num_wildcards = int(document.getElementById('num_wildcards').value)
    num_out = int(document.getElementById('num_out').value)

    files_div = document.getElementById('files')
    output_div = document.getElementById('output')
    output_div.innerText = "Calculating merge, standby... (todo: progress bar)"

    d = {}
    rvs = ""
    rvf = ""

    rvf += "A102Meet Entries             Hy-Tek, Ltd    SwimTopia     08012024 05:35 AMTanoan CC                                            10\n"
    rvf += "B1Sundance Championships                       West Mesa Aquatic Center                     071320240713202405012024   0        74\n"
    rvf += "B2                                                                                          010101S1  0.00                      61\n"
    entries_accum = {}
    
    for filenum in range(files_div.children.length):
        file_div = files_div.children.item(filenum)
        file_name = file_div.children.item(0).innerText
        
        file_contents = file_div.children.item(2).value
        
        if file_name[-4:].lower() == '.zip':
            ba = Uint8Array.new(file_contents)
            hy3_file = BytesIO(bytearray(ba))
            with open(file_name, "wb") as f:
                for line in hy3_file.readlines():
                    f.write(line)
            z = zipfile.ZipFile(file_name)
            if len(z.filelist) > 1:
                print('bailing, [%s] had more than one file' % file_name)
                return
            if not (z.filelist[0].filename[-4:].lower() == '.hy3'):
                print('bailing, the first file in [%s] is not a .hy3' % file_name)
                return
            z.extractall()
            file_name = z.filelist[0].filename
            
        elif file_name[-4:].lower() == '.hy3':
            hy3_file = StringIO(file_contents) 
            with open(file_name, "w") as f: 
                for line in hy3_file.readlines():
                    f.write(line)

        rvs += "processing file [%s]\n" % file_name 

        entries_accum = accumulate_entries(file_name,entries_accum)

        hf = hytek_parser.parse_hy3(file_name)
        for event_key in hf.meet.events.keys():
            event_record = hf.meet.events[event_key]
            if event_key not in d:
                d[event_key] = {'auto_qual': [], 'wildcard_pool': [], 'age_min': event_record.age_min, 'age_max': event_record.age_max, 'event_gender': event_record.gender, 'distance': event_record.distance, 'stroke': event_record.stroke}
            sorted_entries = sorted(event_record.entries, key=lambda x: x.converted_seed_time)
            for (i, entry) in enumerate(sorted_entries):
                if i <= (num_auto-1):
                    d[event_key]['auto_qual'] += [entry]
                else:
                    d[event_key]['wildcard_pool'] += [entry]

    for i in range(1,81):
        if i not in d:
            pass
            #rvs += "===race %s: no racers\n" % (i)
        else:
            rvs += "===race %s (%s-%s %s %s meters %s): \n" % (i, d[i]['age_min'], d[i]['age_max'], d[i]['event_gender'], d[i]['distance'], d[i]['stroke'])
            (vs, vf) = format_auto_quals(d[i]['auto_qual'],num_auto,entries_accum)
            rvs += vs
            rvf += vf
            (vs, vf) = format_k_wildcards(num_wildcards, num_out, d[i]['wildcard_pool'],entries_accum)
            rvs += vs
            rvf += vf

    output_div.innerText = rvs

    download_div = document.getElementById('download')
    s = base64.b64encode(rvf.encode("ascii")).decode('ascii')
    download_div.innerHTML = "Download <a href=\"data:application/octet-stream;base64,%s\" download=\"entry_file.hy3\">hy3 file</a>" % s
    
