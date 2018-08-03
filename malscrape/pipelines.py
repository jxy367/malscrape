# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime as datetime
import time
import os


class MalscrapePipeline(object):
    def process_item(self, item, spider):
        return item


class UrlMembersPipeline(object):
    def __init__(self):
        self.url_members_dict = {}

    def close_spider(self, spider):
        print("closing")
        url_members_file = open("url_members.txt", 'a+')
        for url in self.url_members_dict.keys():
            url_members_file.write(url + ":" + self.url_members_dict[url] + "\n")
        url_members_file.close()

    def process_item(self, item, spider):
        if all(i in item.keys() for i in ["num_members", "url"]):
            self.url_members_dict[str(item['url'])] = str(item['num_members'])


class UsernameListPipeline(object):
    def __init__(self):
        self.username_set = set()
        self.count = 0

    #def close_spider(self, spider):
        #usernames_file = open("usernames.txt", 'a+')
        #for username in self.username_set:
        #    usernames_file.write(username + "\n")
        #usernames_file.close()

    def process_item(self, item, spider):
        #start = time.time()
        if 'usernames' in item.keys():
            username_list = set(item['usernames'])
            new_usernames = (username_list - self.username_set)
            #print(new_usernames)
            check_file_name = "current_all_usernames.txt"
            if check_file(check_file_name):
                new_usernames = remove_old_usernames(check_file_name, new_usernames)
                #print(new_usernames)
            with open("usernames.txt", 'a+') as new_usernames_file:
                for new_username in new_usernames:
                    new_usernames_file.write(new_username + "\n")

            self.username_set.update(new_usernames)

            self.count = self.count + 1
            #print(self.count)
            if self.count % 100 == 0:
                data_string = str(self.count) + "," + str(len(self.username_set))
                data_file = open("user_gathering_data.txt", 'a+')
                data_file.write(data_string + "\n")
                data_file.close()
                print("[ " + str(datetime.now()) + " ] " + data_string)
        #end = time.time()
        #print("Process_item: " + str(end-start))

def check_file(filename):
    return os.path.isfile(filename)


def remove_old_usernames(filename, new_usernames):
    #start = time.time()
    remaining_usernames = new_usernames
    with open(filename, 'r') as old_usernames:
        for line in old_usernames:
            if len(remaining_usernames) == 0:
                return remaining_usernames
            line = line.strip()
            remaining_usernames.discard(line)
    #end = time.time()
    #print("Remove_old_users: " + str(end-start))
    return remaining_usernames
