#!/usr/bin/env python3

import os
import sys
from csv import DictReader, DictWriter
from math import ceil

import click

here = os.path.abspath(os.path.dirname(__file__))

_list = []
try:
    with open(os.path.join(here, 'ProductContent_List.csv'), encoding='utf-8-sig', newline='') as csvfile:
        reader = DictReader(csvfile)
        for i in reader:
            _list.append(i)
except FileNotFoundError:
    click.echo('ProductContent_List.csv is missing. Already create it for you.')
    with open(os.path.join(here, 'ProductContent_List.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        f.write('id,total')
    click.pause('Press any key to exit ...')
    sys.exit()


class AssignProduct:
    def __init__(self, contentlist, productCount):
        self._list = contentlist
        self._product_count = productCount
        self.result = []
        self.loop = 0
        self._list.sort(key=self.getDictValue)

    @staticmethod
    def getDictValue(d):
        return int(d['total'])

    @staticmethod
    def sumDictList(dictList):
        total = 0
        for i in dictList:
            total += int(i['total'])
        return total

    def assign_once(self):
        self.result.sort(key=self.sumDictList)
        self.result[0].append(self._list.pop())
        _max = 0
        _average = 0
        for i in self.result:
            _average += self.sumDictList(i)
            if _max < self.sumDictList(i):
                _max = self.sumDictList(i)
        _average = _average/len(self.result)
        if self.sumDictList(self.result[0]) < _average:
            self.result[0].append(self._list.pop())
        for n in range(1, self._product_count):
            if len(self.result[n]) == self.loop + 1:
                continue
            for i in self._list:
                if self.sumDictList(self.result[n]) + self.getDictValue(i) > _max:
                    self.result[n].append(self._list.pop(_list.index(i)))
                    break
            if len(self.result[n]) < self.loop + 1:
                self.result[n].append(self._list.pop())

    def run(self):
        for _ in range(self._product_count):
            self.result.append([self._list.pop()])
        self.loop += 1
        for _ in range(ceil(len(self._list)/self._product_count)-1):
            self.assign_once()
            self.loop += 1
        self.result.sort(key=self.sumDictList)
        for n in range(self._product_count):
            if len(self.result[n]) == self.loop + 1:
                continue
            if len(self._list) != 0:
                self.result[n].append(self._list.pop())
        try:
            with open(os.path.join(here, 'Result.csv'), 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = ['id', 'total', 'product']
                output = DictWriter(f, fieldnames, extrasaction='ignore')
                output.writeheader()
                for n in range(self._product_count):
                    click.echo(
                        str(n+1)+': '+str(len(self.result[n]))+'-'+str(self.sumDictList(self.result[n])))
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
    AssignProduct(_list, count).run()


if __name__ == '__main__':
    run()
