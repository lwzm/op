#!/usr/bin/env python3

import collections
import sys

import xlrd


week_days = set(map("周{}".format, range(1, 8)))


def extract(fn):
    data = {}
    xls = xlrd.open_workbook(fn)
    for sheet in xls.sheets():
        keys = sheet.row_values(0)
        assert all([isinstance(k, str) for k in keys])
        data[sheet.name] = [dict(zip(keys, sheet.row_values(idx))) for idx in range(1, sheet.nrows)]
    return data


def convert_row_to_resources(row):
    row = row.copy()
    name = row.pop("姓名")
    up = row.pop("师父")
    l = []
    times = []

    for d in week_days:
        times.extend((d, i.strip()) for i in row.pop(d).split(","))

    for d, t in times:
        if not t:
            continue
        for skill, n in row.items():
            if not n:
                continue
            l.append(
                (
                    (d, t, skill),
                    {"name": name, "point": float(n)}
                )
            )

    return l


def convert_row_to_requirements(row, day):
    row = row.copy()
    l = []

    for k, v in row.items():
        if "/" not in k:
            continue
        if not v:
            continue
        t, skill = k.split("/")
        l.append({
            "area": row["区域"],
            "target": row["任务"],
            "require": (day, t, skill),
            "cost": float(v),
        })

    return l


def generate_resources(xls):
    producers = collections.defaultdict(list)
    for name, rows in xls.items():
        if name.startswith("人员"):
            for row in rows:
                for task, resource in convert_row_to_resources(row):
                    producers[task].append(resource)
    return producers


def generate_requirements(xls):
    requirements = []
    for day, rows in xls.items():
        if day in week_days:
            for row in rows:
                for r in convert_row_to_requirements(row, day):
                    requirements.append(r)

    def key(x):
        day, t, skill = x["require"]
        return skill == "普通", day, t

    requirements.sort(key=key)
    return requirements


def plan(resources, requirements):
    empty = []
    accumulated = collections.Counter()
    lst = []
    areas_map = {}

    for item in requirements:
        require = item["require"]
        cost = item["cost"]
        target = item["target"]
        area = item["area"]
        reses = resources.get(require, empty)

        for res in reses:
            name, point = res["name"], res["point"]
            flag = (name, require[0], require[1])
            if point >= cost and areas_map.setdefault(flag, area) == area:
                res["point"] -= cost
                accumulated[name] += 1
                break
        else:
            name = "----"

        lst.append((name, target, require))
        reses.sort(key=lambda x: accumulated[x["name"]])

        #print(name, target, *require, sep="\t")
    #print(accumulated, areas_map)

    return lst


def main(fn="test.xls"):
    xls = extract(fn)

    resources = generate_resources(xls)
    requirements = generate_requirements(xls)

    p = plan(resources, requirements)
    return p

    p.sort(key=lambda x: (x[1], x[0]))
    p.sort()
    for a, b, c in p:
        print(a, b, *c, sep="\t")


if __name__ == '__main__':
    main(*sys.argv[1:2])
