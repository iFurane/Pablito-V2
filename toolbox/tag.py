import yaml
import os

# Return 0 if operation successful
# Return 1 if tag not found or already exists
# Return 2 if other errors

# Giving syntax error is command's job
# Checking category and roles is command's job

# Check for correspoding tag file
def recall_tag(tag_name):
    if not os.path.exists(f'../data/tags/{tag_name}.yml'):   # Check if file doesn't exist
        return 1 #  File doesn't exist

    tmp = {}    # Holder
    try:
        with open(f'../data/tags/{tag_name}.yml', 'r') as f:
            tmp = yaml.safe_load(f)
    except:
        return 2    # Other error
    return tmp  # Return the tag data, checking appropriate catgory and roles is bot's job


# Name: name of the tag (string)
# Author: author of the tag (id)
# Content: data stored by tag
# Category: category in which tag is made
# Channel: channel in which tag is made
# Date: date and time at tag's creation in UTC
def tag_create(name, content, category, author, channel, date):
    if os.path.exists(f'../data/tags/{name}.yml'):
        return 1    # File (tag) exists
    tag_dt = {'content':f'{content}', 'category':f'{category}', 'author':f'{author}', 'channel':f'{channel}','date created':f'{date}'}
    try:
        with open(f'../data/tags/{name}.yml', 'x') as f:
            yaml.safe_dump(tag_dt, f)
    except:
        return 2    # File error
    return 0    # Tag created successfully


# tag_name: name of the tag being deleted
def tag_delete(tag_name):
    if not os.path.exists(f'../data/tags/{tag_name}.yml'):
        return 1    # Tag not found
    try:
        os.remove(f'../data/tags/{tag_name}.yml')
    except:
        return 2    # File error
    return 0    # Tag deleted successfully


# Returns true if edited successfully, false if tag not found
def edit_tag(name, new_content, m_date):
    if not os.path.exists(f'../data/tags/{tag_name}.yml'):
        return 1    # Tag not found
    store = {}
    try:
        with open(f'../data/tags/{name}.yml', 'w') as f:  # Open in overwrite mode
            store = yaml.safe_load(f)
    except:
        return 2    # File error
    store['content'] = f'{new_content}'
    if 'date modified' in store:
        store['date modified'] = str(m_date)
    else:
        store.append({'date modified':f'{m_date}'})
    return 0    # Tag edited successfully


# Dump all tags into a list
def list_all_tags():
    list = os.listdir(path='../data/tags/')
    tmp = {}
    for i in list:
        with open(f'../data/tags/{i}', 'r') as f:
            tmp.append(yaml.safe_load(f))
    return tmp


# Find tags belonging to a category
def find_tags_by_category(cat):
    list = list_all_tags()
    tmp = {}
    for i in list:
        if i['category'] == str(cat):
            tmp.append(i)
    return tmp
