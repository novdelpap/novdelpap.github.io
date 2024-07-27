import hytek_parser
from pyscript import document

import hytek_parser
import sys

VERBOSE = True
NUM_AUTO = 3
NUM_WILDCARDS = 7

def format_auto_quals(aq):
    saq = sorted(aq, key=lambda x: x.converted_seed_time)
    print("\tAUTOMATIC QUALIFIERS")
    for entry in saq:
        print("\t(AUTO) %s, %s %s (%s) %s [%s]" % (entry.swimmers[0].last_name, entry.swimmers[0].first_name, entry.swimmers[0].middle_initial, entry.swimmers[0].team_code, entry.converted_seed_time, entry.converted_seed_time_course))

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


def merge_hyfiles(hyfiles)
    d = {}
    for hyfile in hyfiles:
        hf = hytek_parser.parse_hy3(hyfile)
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
            format_auto_quals(d[i]['auto_qual'])
            format_k_wildcards(NUM_WILDCARDS, d[i]['wildcard_pool'])


def translate_english(event):
    input_text = document.querySelector("#english")
    english = input_text.value
    output_div = document.querySelector("#output")
    output_div.innerText = english + ", yeah!"
