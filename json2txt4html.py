"""
Author: Eray Eren

This program converts a json file containing urls to 
txt file only containing urls. Opens it (optional),
or saves the urls (opt.).
"""

import json
import os
import sys
import subprocess
import lz4.block

def json2txt(urls_path, txt_path, firefox_path=None):
    wins_urls = []
    f = open(urls_path, "r", encoding='utf-8')
    f_out = open(out_txt_path, 'w', encoding='utf-8')
    html_data = json.load(f)

    for win_key, win_vals in html_data[0]['windows'].items():
        # for each window save tabs 
        tab_urls = [firefox_path]
        for tab_key, tab_val in win_vals.items(): # tabs
            tab_urls.append(tab_val['url'])
            f_out.write(tab_val['url'])
            f_out.write('\n')

        f_out.write('\n')
        wins_urls.append(tab_urls)

    f.close()
    f_out.close()

    return wins_urls

def url_from_txt(urls_path, firefox_path=None):
    wins_urls = []
    f = open(urls_path, "r", encoding='utf-8')
    lines = f.readlines()
    tab_urls = [firefox_path]

    for line in lines:
        line = line.strip()
        if line != '':
            tab_urls.append(line)
        else:
            wins_urls.append(tab_urls)
            tab_urls = [firefox_path]
    
    return wins_urls

def get_firefox_urls(firefox_profiles_dir):
    with os.scandir(firefox_profiles_dir) as entries:
        for entry in entries:
            if not entry.name.startswith('.') and entry.is_dir():
                yield from get_firefox_urls_from_profile(
                    os.path.join(firefox_profiles_dir, entry.name)
                )

def get_firefox_urls_from_profile(profiledir):
    filename = os.path.join(profiledir, "sessionstore-backups", "recovery.jsonlz4")
    if not os.path.exists(filename):
        return
    profile_hash, _, profile_name = os.path.basename(profiledir).partition(".")
    with open(filename, "rb") as f:
        # the first 8 bytes in recovery.jsonlz4 should contain
        # the string mozLz40
        assert f.read(8) == b"mozLz40\0"
        # after these 8 bytes the file is a lz4 stream
        compressed_data = f.read()
    data = lz4.block.decompress(compressed_data)
    root = json.loads(data.decode("utf-8"))
    for w, window in enumerate(root["windows"]):
        for t, tab in enumerate(window["tabs"]):
            url = tab["entries"][tab["index"]-1]["url"]
            yield profile_name, w, t, url

def get_windows_list(get_firefox_urls_gen, firefox_profiles_dir):
    wins_list = []
    tab_url_list = []
    w_prev = 0
    for _, w, t, url in get_firefox_urls_gen(firefox_profiles_dir):
        if w_prev != w:
            wins_list.append(tab_url_list)
            tab_url_list = []
        else:
            tab_url_list.append(url)       
        w_prev = w 

    wins_list.append(tab_url_list)
    return wins_list

def save_urls(wins_list, out_txt_path):
    f_out = open(out_txt_path, 'w', encoding='utf-8')
    for tab_list in wins_list:
        for tab in tab_list:
            f_out.write(tab)
            f_out.write('\n')    
        f_out.write('\n')        
    f_out.close()



def main():
    #urls_path = 'C:\\Users\\eraye\\Downloads\\json_tabs.json'
    urls_path = 'C:\\Users\\eraye\\Downloads\\tabs_txt.txt'
    out_txt_path = 'C:\\Users\\eraye\\Downloads\\tabs_txt.txt'

    is_open = True
    if is_open:
        firefox_path = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'

    is_save_urls = True
    if is_save_urls:
        firefox_profiles_dir = 'C:\\Users\\eraye\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles'

    if is_save_urls == False: # opens urls and/or converts them to txt if there is json
        if urls_path.endswith('.json'): 
            # loading json file urls
            wins_urls = json2txt(urls_path, out_txt_path, firefox_path)  
        else:
            # loading txt file urls
            wins_urls = url_from_txt(urls_path, firefox_path)

        # open windows
        for tab_urls in wins_urls:
            if is_open:
                subprocess.call(tab_urls)

    else: # save urls 
        wins_list = get_windows_list(get_firefox_urls, firefox_profiles_dir)
        save_urls(wins_list, out_txt_path)

if __name__ == '__main__':
    main()
    

