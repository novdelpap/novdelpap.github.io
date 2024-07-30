import hytek_parser
import attrs
from pyscript import document
from js import Uint8Array
from io import StringIO
from io import BytesIO
import zipfile
import hashlib

VERBOSE = True
NUM_AUTO = 3
NUM_WILDCARDS = 7

def format_auto_quals(aq):
    rvs = ""
    saq = sorted(aq, key=lambda x: x.converted_seed_time)
    rvs += "\tAUTOMATIC QUALIFIERS\n"
    for entry in saq:
        rvs += "\t(AUTO) %s, %s %s (%s) %s [%s]\n" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.swimmers[0].team_code, entry.converted_seed_time, entry.converted_seed_time_course)
    return rvs

def format_k_wildcards(k,wl):
    rvs = ""
    fwl = filter(lambda x: type(x.converted_seed_time) == float, wl)
    swl = sorted(fwl, key=lambda x: x.converted_seed_time)
    rvs += "\t%d WILDCARDS\n" % k
    for entry in swl[:NUM_WILDCARDS]:
        rvs += "\t(WILDCARD) %s, %s %s, %s, [%s]\n" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time, entry.converted_seed_time_course)
    if VERBOSE:
        dropped = filter(lambda x: not (type(x.converted_seed_time) == float), wl)
        for entry in swl[NUM_WILDCARDS:]:
            rvs += "\t(OUT) \t%s, %s %s, %s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time)
        for entry in dropped:
            rvs += "\t(OUT) \t%s, %s %s, %s\n" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time)
    return rvs

#TODO, warn if there are more than three files
#TODO, more gracefully handle bad zip
def merge_hyfiles(the_arg):

    files_div = document.getElementById('files')
    output_div = document.getElementById('output')
    output_div.innerText = "Calculating merge, standby... (todo: progress bar)"
    
    d = {}
    rvs = ""
    
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
        hf = hytek_parser.parse_hy3(file_name)
        for event_key in hf.meet.events.keys():
            event_record = hf.meet.events[event_key]
            if event_key not in d:
                d[event_key] = {'auto_qual': [], 'wildcard_pool': [], 'age_min': event_record.age_min, 'age_max': event_record.age_max, 'event_gender': event_record.gender, 'distance': event_record.distance, 'stroke': event_record.stroke}
            sorted_entries = sorted(event_record.entries, key=lambda x: x.converted_seed_time)
            for (i, entry) in enumerate(sorted_entries):
                if i <= (NUM_AUTO-1):
                    d[event_key]['auto_qual'] += [entry]
                else:
                    d[event_key]['wildcard_pool'] += [entry]

    for i in range(1,81):
        if i not in d:
            rvs += "===race %s: no racers\n" % (i)
        else:
            rvs += "===race %s (%s-%s %s %s meters %s): \n" % (i, d[i]['age_min'], d[i]['age_max'], d[i]['event_gender'], d[i]['distance'], d[i]['stroke'])
            rvs += format_auto_quals(d[i]['auto_qual'])
            rvs += format_k_wildcards(NUM_WILDCARDS, d[i]['wildcard_pool'])

    output_div.innerText = rvs

