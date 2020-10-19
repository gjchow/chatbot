import requests
import re
from bs4 import BeautifulSoup


def scrape(course):
    out = []
    course = course.lower()
    utsg = re.compile(r'^\w{3}[1-4]\d{2}$')
    utsc = re.compile(r'^\w{3}[A-Da-d]\d{2}$')
    is_utsg = re.match(utsg, course)
    is_utsc = re.match(utsc, course)
    if is_utsg:
        urly = "https://fas.calendar.utoronto.ca/course/" + course + "y1"
        urlh = "https://fas.calendar.utoronto.ca/course/" + course + "h1"
    elif is_utsc:
        urly = "https://utsc.calendar.utoronto.ca/course/" + course + "y3"
        urlh = "https://utsc.calendar.utoronto.ca/course/" + course + "h3"
    else:
        out.append('Not a valid course')
        return out
    pagey = requests.get(urly)
    pageh = requests.get(urlh)

    soupy = BeautifulSoup(pagey.content, 'html.parser')
    souph = BeautifulSoup(pageh.content, 'html.parser')

    namey = soupy.find(id='page-title')
    nameh = souph.find(id='page-title')
    namey = namey.text.strip()
    nameh = nameh.text.strip()
    if nameh != "Sorry, this course is not in the current Calendar." and \
            nameh != "Sorry, this course has been retired and is no longer offered.":
        out.append(nameh)
        link = urlh
        info = souph.find_all("div", class_="field-items")
        labels = souph.find_all("div", class_="field-label")
    elif namey != "Sorry, this course is not in the current Calendar." and \
            namey != "Sorry, this course has been retired and is no longer offered.":
        out.append(namey)
        link = urly
        info = soupy.find_all("div", class_="field-items")
        labels = soupy.find_all("div", class_="field-label")
    else:
        return []
    text_info = []
    text_labels = []
    for thing in info:
        text_info.append(thing.text.strip())
    for thing in labels:
        text_labels.append(thing.text.strip())
    if info == []:
        return[]
    if "Hours:" in text_labels:
        description_i = text_labels.index("Hours:") + 1
    else:
        description_i = 0
    description = text_info[description_i]
    out.append(description)
    if "Prerequisite:" in text_labels:
        prereq_i = text_labels.index("Prerequisite:")
        prereq = text_labels[prereq_i] + "\n" + text_info[prereq_i + 1]
        out.append(prereq)
    else:
        out.append(None)
    if "Corequisite:" in text_labels:
        coreq_i = text_labels.index("Corequisite:")
        coreq = text_labels[coreq_i] + "\n" + text_info[coreq_i + 1]
        if out[2] is None:
            out[2] = coreq
        else:
            out[2] = coreq + "\n\n" + out[2]
    if "Exclusion:" in text_labels:
        exclu_i = text_labels.index("Exclusion:")
        exclu = text_labels[exclu_i] + "\n" + text_info[exclu_i + 1]
        out.append(exclu)
    else:
        out.append(None)
    if "Breadth Requirements:" in text_labels:
        breadth_i = text_labels.index("Breadth Requirements:")
        breadth = text_labels[breadth_i] + "\n" + text_info[breadth_i+1]
        out.append(breadth)
    else:
        out.append(None)
    out.append(link)
    return out
