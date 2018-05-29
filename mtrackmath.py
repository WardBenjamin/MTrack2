import math


def compute(framearr, orgarr, dataarr):
    res = [0, 0, 0]
    tmp = []
    rc = 0
    rm = len(framearr)
    tmp.clear()
    while rc < rm:
        tmp.append(framearr[rc])
        rc += 1
    if framearr[3] - framearr[1] == 0:
        tmp[0] = dataarr[0]
        tmp[1] = dataarr[1]
        tmp[2] = dataarr[0]
        tmp[3] = dataarr[1] + 10
        res[2] = 1
    elif framearr[2] - framearr[0] == 0:
        tmp[0] = dataarr[0]
        tmp[1] = dataarr[1]
        tmp[2] = dataarr[0] + 10
        tmp[3] = dataarr[1]
        res[2] = 2
    else:
        tmp[0] = dataarr[0]
        tmp[1] = dataarr[1]
        tmp[2] = dataarr[0] + 10
        tmp[3] = dataarr[1] + ((framearr[3] - framearr[1]) / (framearr[2] - framearr[0]) * 10)
        res[2] = 3
    px = origin(tmp)
    rc = 0
    rm = len(framearr)
    tmp.clear()
    while rc < rm:
        tmp.append(framearr[rc])
        rc = rc + 1
    if framearr[7] - framearr[5] == 0:
        tmp[4] = dataarr[0]
        tmp[5] = dataarr[1]
        tmp[6] = dataarr[0]
        tmp[7] = dataarr[1] + 10
        res[2] = str(res[2]) + "1"
    elif framearr[6] - framearr[4] == 0:
        tmp[4] = dataarr[0]
        tmp[5] = dataarr[1]
        tmp[6] = dataarr[0] + 10
        tmp[7] = dataarr[1]
        res[2] = str(res[2]) + "2"
    else:
        tmp[4] = dataarr[0]
        tmp[5] = dataarr[1]
        tmp[6] = dataarr[0] + 10
        tmp[7] = dataarr[1] + ((framearr[7] - framearr[5]) / (framearr[6] - framearr[4]) * 10)
        res[2] = str(res[2]) + "3"
    py = origin(tmp)
    res[1] = math.sqrt((orgarr[0] - px[0]) ** 2 + (orgarr[1] - px[1]) ** 2) * (dataarr[3] / math.sqrt((framearr[4] - framearr[6]) ** 2 + (framearr[5] - framearr[7]) ** 2))
    res[0] = math.sqrt((orgarr[0] - py[0]) ** 2 + (orgarr[1] - py[1]) ** 2) * (dataarr[2] / math.sqrt((framearr[0] - framearr[2]) ** 2 + (framearr[1] - framearr[3]) ** 2))
    rc = 0
    rm = len(framearr)
    tmp.clear()
    while rc < rm:
        tmp.append(framearr[rc])
        rc = rc + 1
    if framearr[3] - framearr[1] == 0:
        if ((orgarr[0] < py[0] and framearr[2] < framearr[0]) or (orgarr[0] > py[0] and framearr[2] > framearr[0])):
            res[0] = -res[0]
    else:
        if ((orgarr[1] < py[1] and framearr[3] < framearr[1]) or (orgarr[1] > py[1] and framearr[3] > framearr[1])):
            res[0] = -res[0]
    if framearr[7] - framearr[5] == 0:
        if ((orgarr[0] < px[0] and framearr[6] < framearr[4]) or (orgarr[0] > px[0] and framearr[6] > framearr[4])):
            res[1] = -res[1]
    else:
        if ((orgarr[1] < px[1] and framearr[7] < framearr[5]) or (orgarr[1] > px[1] and framearr[7] > framearr[5])):
            res[1] = -res[1]
    return res


def origin(d):
    r = [0, 0, 0]
    r[2] = 0
    if ((d[3] - d[1]) * (d[6] - d[4])) == ((d[7] - d[5]) * (d[2] - d[0])):
        r[0] = 0
        r[1] = 0
        r[2] = -1
        return r
    elif d[2] - d[0] == 0:
        r[0] = d[0]
        if d[7] - d[5] == 0:
            r[1] = d[5]
        else:
            r[1] = ((d[7] - d[5]) / (d[6] - d[4])) * (r[0] - d[4]) + d[5]
        r[2] = 1
    elif d[3] - d[1] == 0:
        r[1] = d[1]
        if d[6] - d[4] == 0:
            r[0] = d[4]
        else:
            r[0] = ((r[1] - d[5]) / ((d[7] - d[5]) / (d[6] - d[4]))) + d[4]
        r[2] = 2
    elif d[6] - d[4] == 0:
        r[0] = d[4]
        if d[3] - d[1] == 0:
            r[1] = d[1]
        else:
            r[1] = ((d[3] - d[1]) / (d[2] - d[0])) * (r[0] - d[0]) + d[1]
        r[2] = 3
    elif d[7] - d[5] == 0:
        r[1] = d[5]
        if d[2] - d[0] == 0:
            r[0] = d[0]
        else:
            r[0] = ((r[1] - d[1]) / ((d[3] - d[1]) / (d[2] - d[0]))) + d[0]
        r[2] = 4
    else:
        r[0] = ((((d[7] - d[5]) / (d[6] - d[4])) * d[4]) - (((d[3] - d[1]) / (d[2] - d[0])) * d[0]) + d[1] - d[5]) / (((d[7] - d[5]) / (d[6] - d[4])) - ((d[3] - d[1]) / (d[2] - d[0])))
        r[1] = ((d[3] - d[1]) / (d[2] - d[0])) * (r[0] - d[0]) + d[1]
        r[2] = 5
    return r
