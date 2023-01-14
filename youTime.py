import urllib.request
from urllib.error import HTTPError
import json
from datetime import timedelta
import csv
from datetime import datetime


def parse_time(str_time):
    str_time = str_time.replace("PT", "")

    time_tmp = ""
    m_t = "0"
    h_t = "0"
    s_t = "0"

    for i in str_time:
        if i == "H":
            h_t = time_tmp
            time_tmp = ""
        elif i == "M":
            m_t = time_tmp
            time_tmp = ""
        elif i == "S":
            s_t = time_tmp
            time_tmp = ""
        else:
            time_tmp += i
    try:
        return ((int(m_t) * 60) + (int(h_t) * 3600) + int(s_t))
    except ValueError:
        print(m_t, "+" , h_t, "+" ,s_t)
        return 0



def parse_ids():
    ids = []
    with open("watch-history.html", "r", encoding="utf8") as file:
        lines = file.readlines()
        count = 0
        for line in lines:
            if line.find('href="https://www.youtube.com/watch?v=') != -1:
                ids.append(line.split('"')[1].split("=")[1])
                count += 1
        return ids
def gen_files():
    with open("idsFile.txt", "w") as file:
        for i in parse_ids():
            file.write(i + "\n")

    with open("dataOut.csv", "w") as file:
        file.write("id,title,channel,length,publishDate\n")

def get_ids():
    id_list = []
    with open("idsFile.txt", "r", encoding="utf-8") as file:
        for i in file.readlines():
            id_list.append(i.replace("\n", ""))
    return id_list

def call_api():
    out_file = open("dataOut.csv", "a", encoding="utf8")
    counter = 0
    ids = get_ids()
    key = ""
    with open("apikry.sec", "r") as file:
        key = file.read()
    for url in ids:
        furl = "https://www.googleapis.com/youtube/v3/videos?id="+ url+ "&part=contentDetails&part=snippet&key=" + key
        with urllib.request.urlopen(furl) as url:
            data = json.load(url)
            try:
                data_items = data['items'][0]
                snippet = data_items['snippet']
                content_details = data_items['contentDetails']

                video_id = data_items['id']
                video_title = snippet['title']
                channel_name = snippet['channelTitle']
                date_published = snippet['publishedAt']
                duration = content_details['duration']

                duration_parsed = timedelta(seconds=parse_time(duration))

                out_text = "{0},{1},{2},{3},{4}\n".format(video_id, video_title, channel_name, duration_parsed, date_published)
                out_file.write(out_text)
                counter +=1

            except IndexError:
                print(data)
            except HTTPError:
                print("limit Reached", data)
                out_file.close()
                with open("idsFile.txt", "w") as file:
                    rem_ids = ids[counter:]
                    for i in rem_ids:
                        file.write(i + "\n")
    out_file.close()

def fix_file():
    with open("dataOut.csv", "r", encoding="utf8") as file_in:
        with open("dataOutNew.csv", "w", encoding="utf8") as file_out:
            data=file_in.readlines()
            count_char = 0
            count_komma = 0
            coma_in_line = 0
            for l in data:
                for c in l:
                    if c == ",":
                        coma_in_line +=1
                if coma_in_line > 4:
                    for c in reversed(l):
                        if c == ",":
                            count_komma +=1
                        if c == "," and count_komma > 3:
                            l = l[:-count_char-1] + "." + l[-count_char:]
                        count_char += 1
                    count_char = 0
                    for c in l:
                        if c == ".":
                            l = l[:count_char] + "," + l[count_char+1:]
                            break
                        count_char +=1
                file_out.write(l)
                count_char = 0
                coma_in_line = 0
                count_komma = 0


def calc_time():
    time_all = 0
    with open("dataOutNew.csv", "r", encoding="utf8") as file:
        data = csv.reader(file, delimiter=",")
        for row in data:
            length = row[3]
            if length != "length":
                pt = datetime.strptime(length, '%H:%M:%S')
                time_all += (pt.second + pt.minute*60 + pt.hour*3600)
    
    print(timedelta(seconds=time_all))

"""
this function generates the neccesarry files
"""
#gen_files()

"""
this function gets the data from youtube. limited to 10000 requests a day
"""
#call_api()

"""
this function fixes the file -> if the video title has a comma in it it breakes the csv file so they get replaced py dots
"""
#fix_file()

"""
this function outputs the time watched in hours 
"""
#calc_time()

