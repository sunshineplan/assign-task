#!/usr/bin/env python3

import os
import sys
from csv import DictReader, DictWriter
from math import ceil

import click

here = os.path.abspath(os.path.dirname(__file__))

_list = []
try:
    with open(os.path.join(here, 'ProductContent_List.csv'), newline='') as csvfile:
        reader = DictReader(csvfile)
        for i in reader:
            _list.append(i)
except FileNotFoundError:
    click.echo('ProductContent_List.csv is missing. Already create it for you.')
    with open(os.path.join(here, 'ProductContent_List.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        f.write('id,total')
    click.pause('Press any key to exit ...')
    sys.exit()


def getDictValue(d):
    return int(d['total'])


_list.sort(key=getDictValue)


def sumDictList(dictList):
    total = 0
    for i in dictList:
        total += getDictValue(i)
    return total


class AssignProduct:
    def __init__(self, count):
        self._product_count = count
        self.result = []
        self.loop = 1

    def assign_once(self):
        self.result.sort(key=sumDictList)
        self.result[0].append(_list.pop())
        _max = 0
        for i in self.result:
            if _max < sumDictList(i):
                _max = sumDictList(i)
        for n in range(1, self._product_count):
            for i in _list:
                if sumDictList(self.result[n]) + getDictValue(i) > _max:
                    self.result[n].append(_list.pop(_list.index(i)))
                    break
            if len(self.result[n]) != self.loop + 1:
                self.result[n].append(_list.pop(-1))

    def run(self):
        for _ in range(self._product_count):
            self.result.append([_list.pop()])
        for _ in range(ceil(len(_list)/self._product_count)-1):
            self.assign_once()
            self.loop += 1
        self.result.sort(key=sumDictList)
        for n in range(self._product_count):
            if len(_list) != 0:
                self.result[n].append(_list.pop())
        try:
            with open(os.path.join(here, 'Result.csv'), 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = ['id', 'total', 'product']
                output = DictWriter(f, fieldnames, extrasaction='ignore')
                output.writeheader()
                for n in range(self._product_count):
                    click.echo(
                        str(n+1)+': '+str(len(self.result[n]))+'-'+str(sumDictList(self.result[n])))
                    for i in self.result[n]:
                        i['product'] = n+1
                    output.writerows(self.result[n])
        except PermissionError:
            click.echo(
                'Write Result.csv failed. Permission denied. Maybe this file was opened.')
            click.pause('Press any key to exit ...')
            sys.exit()
        click.pause('Job done. Press any key to exit ...')


@click.command(help='Assign products according product content list.')
@click.argument('count', required=False, default=0, type=click.IntRange(0))
def run(count):
    if not count:
        count = click.prompt('Please input product count',
                             type=click.IntRange(1))
    AssignProduct(count).run()


if __name__ == '__main__':
    run()
