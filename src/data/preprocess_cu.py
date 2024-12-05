import json
import os
import traceback

def extract_paper(file_location, year):
    with open(file_location) as json_data:
        d = json.load(json_data)
    title = d['abstracts-retrieval-response']['item']['bibrecord']['head']['citation-title']
    author_group = d['abstracts-retrieval-response']['item']['bibrecord']['head']['author-group']


    #each affiliation has multiple authors
    author_list = []
    if isinstance(author_group, list):
        for i in author_group: #iterate through each affiliation
            try: #some author group doesn't have affiliation
                affiliation = i['affiliation']['country']
            except:
                continue;
            try:
                if isinstance(i['author'], list):
                    for j in i['author']:
                        author = j['preferred-name']['ce:given-name']
                        if ({'author': author, 'affiliation': affiliation}) not in author_list:
                            author_list.append({'author': author, 'affiliation': affiliation})
                else:
                    author = i['author']['preferred-name']['ce:given-name']
                    if ({'author': author, 'affiliation': affiliation}) not in author_list:
                            author_list.append({'author': author, 'affiliation': affiliation})
            except:
                continue;
    else:
        try:
            affiliation = author_group['affiliation']['country']
        except:
            affiliation = "N/A"
        if isinstance(author_group['author'], list):
            for j in author_group['author']:
                author = j['preferred-name']['ce:given-name']
                if ({'author': author, 'affiliation': affiliation}) not in author_list:
                        author_list.append({'author': author, 'affiliation': affiliation})
        else:
            author = author_group['author']['preferred-name']['ce:given-name']
            if ({'author': author, 'affiliation': affiliation}) not in author_list:
                        author_list.append({'author': author, 'affiliation': affiliation})
    
    
    # if isinstance(author_group, list):
    #     for i in author_group:
    #         item = i['ce:given-name']
    #         author_list.add(item)
    # else:
    #     author_list.add(author_group['ce:given-name'])
    #         # author_list.append({x['ce:given-name'],i['affiliation']['country']})
    
    # if isinstance(affiliation, list):
    #     for i in affiliation:
    #         affiliation_list.add(i['affiliation-country'])
    # else:
    #     affiliation_list.add(affiliation['affiliation-country'])
    


    subjects = []
    subject_area = d['abstracts-retrieval-response']['subject-areas']['subject-area']
    for i in subject_area:
        subjects.append(i['@code'])


    # print(f'title: {title}')      
    # print(f'author: {author_list}')
    # print(f'subject code: {subjects}')
    if len(author_list) == 0:
        return ""
    # for i in author_list:
    #     if (i['author'] is None):
    #         author_list.remove(i)
    #         continue
    #     if (i['author'].count('.') > 0):
    #         author_list.remove(i)
    #         continue
        
    author_list = [i for i in author_list if i['author'] is not None and i['author'].count('.') == 0]
    
    if len(author_list) == 0:
        return ""
    
    
    
    
    
    combined = {'title': title, 
                'author_list': (author_list), 
                'subject code': subjects,
                'cited_count': d['abstracts-retrieval-response']['coredata']['citedby-count'], 
                'year': year}
    json_string = json.dumps(combined, ensure_ascii=False)
    return json_string





import traceback
for year in range(2018,2024):
    directory = f'../../data/cu_paper_data/{year}'
    for name in os.listdir(directory):
        if name.endswith('.json'):
            try:
                jsonString = extract_paper(file_location=f'{directory}/{name}', year=year)
                if jsonString != "":
                    print(name + jsonString)
            except Exception as e:
                print(f'error on {name} with: {e}')
                traceback.print_exc()
            
            
        