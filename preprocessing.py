import pandas as pd
import regex as re

from collections import Counter

title_finder = re.compile(r'"(.*)"')
scene_continues_pattern = '^\d+.*'
sub_scene_pattern = '^\d+\w+.*'

def get_title(s):
    '''
    Returns from the string version of the script the title
    of the episode
    '''
    import re 
    # title_finder = re.compile(r'"(.*)"')
    
    return title_finder.search(s).group(1)


def tab_return(num_tabs, ep_lines):
    '''
    Returns a list of lines that start with num_tabs tabs.
    Input must be a list of lines.
    '''
    assert type(ep_lines) == list
    
    def line_starts_with_only_n(line, n=num_tabs):
        tabs = '\t' * num_tabs
        try:
            return (line[:n] == tabs) and (line[n] != '\t')
        except IndexError:
            return False
    
    return [line for line in ep_lines if line_starts_with_only_n(line)]


def get_header_cutoff(ep_lines):
    '''
    Determines the index cutoff for where the episode header ends.
    Input should be a list of strings.
    '''
    # used on lines not str
    assert type(ep_lines) == list
    
    cutoff = 0
    for ix, line in enumerate(ep_lines):
        if line.strip() == 'TEASER':
            cutoff = ix
            break
    return cutoff

def make_header_and_ep(ep_lines):
    ''' Partitions episode into header and body. '''
    cutoff = get_header_cutoff(ep_lines)
    header = ep_lines[:cutoff]
    ep = ep_lines[cutoff:]
    return header, ep


def match_page_header(line):
    '''
    This function identifies if a line is a page header.
    Input is a single line.
    '''
    # later eps say DEEP SPACE NINE:
    # hopefully this will be more flexible
    return (line.strip().startswith('DEEP SPACE')) and (":" in line)

def match_scene_continues(line):
    ''' Matches scene continues. '''
    # scene_continues_pattern = '^\d+.*'
    return (re.match(scene_continues_pattern, line)) and ('CONTINUED:' in line)

def match_sub_scene(line):
    ''' Matches sub scenes. '''
    # sub_scene_pattern = '^\d+\w+.*'
    return re.match(sub_scene_pattern, line)

def clean_ep_lines(ep_lines):
    fns = [match_page_header, match_scene_continues, match_sub_scene]
    for f in fns:
        ep_lines = [l for l in ep_lines if not f(l)]
    return ep_lines



def act_partition(ep_lines, to_dict=False):
    '''
    Accepts a list of episode lines.
    Returns six lists, one list per act, including the teaser.
    '''
    
    assert type(ep_lines) == list
    
    stripped_lines = [l.strip() for l in ep_lines]
    
    teaser_begin = stripped_lines.index('TEASER')
    act_1_begin = stripped_lines.index('ACT ONE')
    act_2_begin = stripped_lines.index('ACT TWO')
    act_3_begin = stripped_lines.index('ACT THREE')
    act_4_begin = stripped_lines.index('ACT FOUR')
    act_5_begin = stripped_lines.index('ACT FIVE')
    
    teaser = ep_lines[:act_1_begin]
    act_1 = ep_lines[act_1_begin:act_2_begin]
    act_2 = ep_lines[act_2_begin:act_3_begin]
    act_3 = ep_lines[act_3_begin:act_4_begin]
    act_4 = ep_lines[act_4_begin:act_5_begin]
    act_5 = ep_lines[act_5_begin:]
    
    if to_dict:
        d = {}
        d['teaser'] = teaser
        d['act_1'] = act_1
        d['act_2'] = act_2
        d['act_3'] = act_3
        d['act_4'] = act_4
        d['act_5'] = act_5
        return d
    
    return teaser, act_1, act_2, act_3, act_4, act_5


def clean_speaker(s):
    '''
    Works on a single string to clear common prefixes and suffixes.
    '''
    
    clean_up = [
        '(V.O.)','(O.S.)', '(OS)', "'S COM VOICE",'(MONITOR)',
        '\'S COMPUTER VOICE', "(cont'd)", "(Cont'd)", '(ON SCREEN)',
        '(0.S.)', '(FAR O.S.)', 'ON SCREEN', '(Cont,d)', '(O. C.. )',
        "(Cont' d)", "'S VOICE", '(0. S. )', ' (0. S.)', ' (0.S)',
        "'S COM VOICE", "'S VOICE", "'S COMM VOICE", '(indicates)',
        '(thru door)', "(OPTICAL)", "(COM VOICE)", "...", "(O.S)",
        "(CONTINUING)", "(BEAT)", ",", "(V. O.)", "(V.O)"
    ]
    
    for each in clean_up:
        if each in s:
            s = s.replace(each, '')
    
    s = s.strip()
    s = s.replace('0', 'O')
    s = s.upper()
    if s == '':
        s = 'BLANK'
    return s

def return_speakers(lines):
    '''
    Accepts a list of episode lines.
    Returns only the speakers.
    '''
    raw_speakers = tab_return(5, ep_lines=lines)
    raw_speakers = [s.strip() for s in raw_speakers]
    raw_speakers = [clean_speaker(s) for s in raw_speakers]
    return raw_speakers

def speakers_from_act(lines):
    return dict(Counter(return_speakers(lines)))

def process_episode(filename, season=False):
    
    with open(f'scripts/{filename}') as f:
        ep = f.read()
    
    ep_num = filename.split('.')[0]
    ep_lines = ep.split('\n')
    ep_title = get_title(ep)
    
    header, body = make_header_and_ep(ep_lines)
    body = clean_ep_lines(body)
    acts = act_partition(body, to_dict=True)
    acts_speakers = {
        f"{ep_num}_{k}": speakers_from_act(v) for k, v in acts.items()
    }
    
    # ep_dict = {}
    # ep_dict['title'] = ep_title
    # ep_dict['num'] = ep_num
    # if season:
    #     ep_dict['season'] = season
    # ep_dict.update(acts_speakers)
    
    # ep_dict = {}
    
    return acts_speakers
    