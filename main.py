import hytek_parser
import attrs
from pyscript import document
from io import StringIO
from io import BytesIO
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
    fwl = filter(lambda x: type(x.converted_seed_time) == float, wl)
    swl = sorted(fwl, key=lambda x: x.converted_seed_time)
    print("\t%d WILDCARDS" % k)
    for entry in swl[:NUM_WILDCARDS]:
        print("\t(WILDCARD) %s, %s %s, %s, [%s]" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time, entry.converted_seed_time_course))
    if VERBOSE:
        dropped = filter(lambda x: not (type(x.converted_seed_time) == float), wl)
        for entry in swl[NUM_WILDCARDS:]:
            print("\t(OUT) \t%s, %s %s, %s" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time))
        for entry in dropped:
            print("\t(OUT) \t%s, %s %s, %s" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.converted_seed_time))


async def merge_hyfiles(the_arg):
    #<input type="hidden" id="hid1" value="generatedValue1" />
    #<input type="hidden" id="hid2" value="generatedValue2" />
    hid1 = document.querySelector("#hid1")
    val1 = hid1.value;
    hid1.value = "blah1"
    hid2 = document.querySelector("#hid2")
    hid2.value = "blah2"
    val2 = hid2.value;
    output_div = document.querySelector("#output")
    output_div.innerText = repr(the_arg) + "/" + repr(val1) + "/" + repr(val2)
    
    hy3_file = document.getElementById('fileElem').files.item(0)
    file_text = await hy3_file.text() # Get arrayBuffer from file
    hy3_file = StringIO(file_text) # Wrap in Python BytesIO file-like object

    d = {}
    for hyfile in [hy3_file]:
        output_div.innerText = ""
        with open("a.hy3", "w") as f: 
            for line in hy3_file.readlines():
                f.write(line)
        with open("a.hy3", "rb") as ff:
             output_div.innerText += str(hashlib.file_digest(ff, 'md5').hexdigest())
        hf = hytek_parser.parse_hy3("a.hy3")
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
            print("===race %s: no racers" % (i))
        else:
            print("===race %s (%s-%s %s %s meters %s): " % (i, d[i]['age_min'], d[i]['age_max'], d[i]['event_gender'], d[i]['distance'], d[i]['stroke']))
            output_div.innerText += format_auto_quals(d[i]['auto_qual'])
            format_k_wildcards(NUM_WILDCARDS, d[i]['wildcard_pool'])


