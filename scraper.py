import requests
import re
from bs4 import BeautifulSoup


def scrape(course):
    out = []
    course = course.lower()
    utsg = re.compile(r'^\w{3}\d{3}$')
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
    if info != []:
        if is_utsg:
            description_i = text_labels.index("Hours:") + 1
        else:
            description_i = 0
        description = text_info[description_i]
        exclu_i = -1
        exclu = "Exclusion:\nNone"
        prereq_i = -1
        prereq = "Prerequisite:\nNone"
        coreq_i = -1
        coreq = "Corequisite:\nNone"
        if "Prerequisite:" in text_labels:
            prereq_i = text_labels.index("Prerequisite:")
        if "Exclusion:" in text_labels:
            exclu_i = text_labels.index("Exclusion:")
        breadth_i = text_labels.index("Breadth Requirements:")
        if prereq_i != -1:
            prereq = text_labels[prereq_i] + "\n" + text_info[prereq_i+1]
        if exclu_i != -1:
            exclu = text_labels[exclu_i] + "\n" + text_info[exclu_i+1]
        breadth = text_labels[breadth_i] + "\n" + text_info[breadth_i+1]
        if "Corequisite:" in text_labels:
            coreq_i = text_labels.index("Corequisite:")
        if coreq_i != -1:
            coreq = text_labels[coreq_i] + "\n" + text_info[coreq_i+1]
            prereq = coreq + "\n\n" + prereq

        out.append(description)
        out.append(prereq)
        out.append(exclu)
        out.append(breadth)
        out.append(link)
    else:
        return []

    return out


def course_info(course):
    if scrape(course) == []:
        return ['Course not found']
    elif len(scrape(course)) == 1:
        return [scrape(course)[0]]
    return scrape(course)


def course_name(course):
    if scrape(course) == []:
        return 'Course not found'
    elif len(scrape(course)) == 1:
        return scrape(course)[0]
    return [scrape(course)[0]]


def course_descrip(course):
    if scrape(course) == []:
        return 'Course not found'
    elif len(scrape(course)) == 1:
        return scrape(course)[0]
    return [scrape(course)[1]]


def course_prereq(course):
    if scrape(course) == []:
        return 'Course not found'
    elif len(scrape(course)) == 1:
        return scrape(course)[0]
    return [scrape(course)[2]]


def course_exclu(course):
    if scrape(course) == []:
        return 'Course not found'
    elif len(scrape(course)) == 1:
        return scrape(course)[0]
    return [scrape(course)[3]]


def course_breadth(course):
    if scrape(course) == []:
        return 'Course not found'
    elif len(scrape(course)) == 1:
        return scrape(course)[0]
    return [scrape(course)[4]]


def course_link(course):
    if scrape(course) == []:
        return 'Course not found'
    elif len(scrape(course)) == 1:
        return scrape(course)[0]
    return [scrape(course)[5]]


print(scrape('mat137'))