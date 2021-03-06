#!/usr/bin/env python3

import os
import sys
from csv import DictReader, DictWriter
from json import loads
from math import ceil, floor
from random import choice, shuffle

import click

here = os.path.abspath(os.path.dirname(__file__))


class Assign:
    def __init__(self, ignore_error=False):
        self._name_list = self.loadNameList(ignore_error)

    @staticmethod
    def loadNameList(ignore_error=False):
        try:
            with open(os.path.join(here, 'Name_List.txt'), encoding='utf-8') as f:
                name_list = [i.rstrip('\n').strip() for i in f.readlines()]
                name_list = [i for i in name_list if i != '']
                name_list = [i for i in name_list if i[0] != '#']
            if len(name_list) == 0:
                raise ValueError('Empty list.')
            return name_list
        except FileNotFoundError:
            if not ignore_error:
                click.echo(
                    'Name_List.txt is missing. Already create it for you.')
                with open(os.path.join(here, 'Name_List.txt'), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(['Name1', 'Name2*2', '#Name3', 'Name4']))
                click.pause('Press any key to exit ...')
                sys.exit()
        except ValueError:
            if not ignore_error:
                click.echo('Name_List.txt has no valid content.')
                click.pause('Press any key to exit ...')
                sys.exit()
        return None

    @staticmethod
    def num(obj):
        if isinstance(obj, str):
            try:
                return int(obj)
            except ValueError:
                return float(obj)
        elif isinstance(obj, float):
            return round(obj, 2)
        else:
            return obj

    def sumDictList(self, dictList):
        return sum([self.num(i['number']) for i in dictList])


class AssignByName(Assign):
    def __init__(self, total, random):
        super().__init__()
        self.total = total
        self.random = random
        self.assign()
        shuffle(self.list)
        if (total * 100) % (self.sumDictList(self.list) * 100):
            click.echo('Total:{}, Assign:{}, Per number:{}-{}'.format(
                total, self.sumDictList(self.list), int(total//self.sumDictList(self.list)), int(total//self.sumDictList(self.list))+1))
        else:
            click.echo('Total:{}, Assign:{}, Per number:{}'.format(
                total, self.sumDictList(self.list), int(total//self.sumDictList(self.list))))

    def assign(self):
        self.list = []
        for i in self._name_list:
            if '*' in i and isinstance(loads(scale := i.split('*', maxsplit=1)[1].strip()), (int, float)):
                if self.num(scale) > 0 and self.num(scale) <= self.total/len(self._name_list):
                    self.list.append(
                        {'id': i.split('*')[0].strip(), 'number': self.num(scale)})
                else:
                    print(f'[Warning]Ignoring invalid scale in {i}.')
                    self.list.append(
                        {'id': i.split('*')[0].strip(), 'number': 1})
            else:
                self.list.append({'id': i, 'number': 1})

    @staticmethod
    def get_num(num):
        return eval('{}({})'.format(choice(['ceil', 'floor']), num))

    def run(self):
        result = []
        print_result = []
        while True:
            try:
                name = self.list.pop()
                scale = name['number']
                num = self.get_num(
                    self.total/(self.sumDictList(self.list)+scale) * scale)
                result += [name['id']] * num
                print_result += ['%s: %s' % (name['id'] if name['number']
                                             == 1 else name['id']+'*'+str(name['number']), num)]
                self.total -= num
            except IndexError:
                break
        if self.random:
            shuffle(result)
        try:
            with open(os.path.join(here, 'Result.txt'), 'w', encoding='utf-8') as f:
                f.write('\n'.join(result))
        except PermissionError:
            click.echo(
                'Write Result.txt failed. Permission denied. Maybe this file was opened.')
            click.pause('Press any key to exit ...')
            sys.exit()
        click.echo('\n'.join(print_result))
        click.pause('Job done. Press any key to exit ...')


class AssignByContent(Assign):
    def __init__(self, count=None):
        super().__init__(ignore_error=True)
        if count:
            self._name_list = range(1, count+1)
        else:
            if not self._name_list:
                click.echo(
                    'Name_List.txt has no valid content or missing. Use NUMBER argument instead.')
        self._content_list = self.loadContentList()
        self._count = len(self._name_list)
        self.result = []
        self.loop = 0
        self._content_list.sort(key=lambda i: int(i['number']))
        if len(self._content_list) % len(self._name_list):
            self.max_count = ceil(len(self._content_list)/self._count)
            click.echo('Total:{}, Count:{}, Assign:{}-{}'.format(
                len(self._content_list), self._count, self.max_count-1, self.max_count))
        else:
            self.max_count = len(self._content_list)//self._count
            click.echo('Total:{}, Count:{}, Assign:{}'.format(
                len(self._content_list), self._count, self.max_count))

    @staticmethod
    def loadContentList():
        content_list = []
        try:
            with open(os.path.join(here, 'Content_List.csv'), encoding='utf-8-sig', newline='') as f:
                reader = DictReader(f)
                for i in reader:
                    content_list.append(i)
                if len(content_list) == 0:
                    raise ValueError('Empty list.')
        except FileNotFoundError:
            click.echo(
                'Content_List.csv is missing. Already create it for you.')
            with open(os.path.join(here, 'Content_List.csv'), 'w', encoding='utf-8-sig', newline='') as f:
                f.write('id,number')
            click.pause('Press any key to exit ...')
            sys.exit()
        except ValueError:
            click.echo('Content_List.csv has no valid content.')
            click.pause('Press any key to exit ...')
            sys.exit()
        return content_list

    def assign_once(self):
        if len(self.result[0]) < self.max_count - 1:
            self.result[0].append(self._content_list.pop())
        _average = 0
        for i in self.result:
            _average += self.sumDictList(i)
        _average = _average/len(self.result)
        for _ in range(self.max_count):
            if self.sumDictList(self.result[0]) < _average:
                if len(self.result[0]) == self.max_count - 1:
                    break
                self.result[0].append(self._content_list.pop())
        _max = 0
        for i in self.result:
            if _max < self.sumDictList(i):
                _max = self.sumDictList(i)
        for n in range(1, self._count):
            if len(self.result[n]) == self.max_count - 1:
                continue
            for i in self._content_list:
                if self.sumDictList(self.result[n]) + int(i['number']) > _max:
                    self.result[n].append(
                        self._content_list.pop(self._content_list.index(i)))
                    break
            if len(self.result[n]) < self.loop + 1:
                self.result[n].append(self._content_list.pop())
        self.result.sort(key=self.sumDictList)

    def run(self):
        for _ in range(self._count):
            self.result.append([self._content_list.pop()])
        self.loop += 1
        self.result.sort(key=self.sumDictList)
        for _ in range(self.max_count-2):
            self.assign_once()
            self.loop += 1
        for n in range(self._count):
            if len(self.result[n]) == self.max_count:
                continue
            if len(self._content_list) != 0:
                self.result[n].append(self._content_list.pop())
        self.result.sort(key=self.sumDictList)
        try:
            with open(os.path.join(here, 'Result.csv'), 'w', encoding='utf-8-sig', newline='') as f:
                fieldnames = ['id', 'number', 'name']
                output = DictWriter(f, fieldnames, extrasaction='ignore')
                output.writeheader()
                for n in range(self._count):
                    for i in self.result[n]:
                        i['name'] = self._name_list[n]
                    output.writerows(self.result[n])
                    click.echo('{} - assign: {}, number: {}'.format(
                        self._name_list[n], len(self.result[n]), self.sumDictList(self.result[n])))
        except PermissionError:
            click.echo(
                'Write Result.csv failed. Permission denied. Maybe this file was opened.')
            click.pause('Press any key to exit ...')
            sys.exit()
        click.pause('Job done. Press any key to exit ...')


@click.command(help='Assign by name or content.')
@click.argument('number', required=False, default=0, type=click.IntRange(0))
@click.option('--by', 'mode', default='name', type=click.Choice(['name', 'content']), show_default=True, help='Assign mode.')
@click.option('--random', '-r', is_flag=True, help='Random result when assigning by name.')
def run(number, mode, random):
    if mode == 'name':
        if not number:
            number = click.prompt('Please input total number',
                                  type=click.IntRange(1))
        AssignByName(number, random).run()
    elif mode == 'content':
        if number:
            AssignByContent(number).run()
        else:
            try:
                AssignByContent().run()
            except TypeError:
                number = click.prompt('Please input count number',
                                      type=click.IntRange(1))
                AssignByContent(number).run()


if __name__ == '__main__':
    run()
