import pickle
from bs4 import BeautifulSoup
import urllib2
import time 
import shutil
import os

print("Archiving old database")
old_version = open('VERSION').readline().strip()
os.mkdir(old_version + '.archive')
for f in [x for x in os.listdir('.') if x.endswith('.pickle')]:
    shutil.move(f, os.path.join(old_version + '.archive', f))

date=time.strftime("%d-%m-%Y")
with open('VERSION', 'w') as o:
    o.write(date+'\n')
print("Done")


output_pickle = 'compound_descriptions.%s.pickle' % date
output_dict = {}
br08001 = 'http://www.kegg.jp/kegg-bin/download_htext?htext=br08001&format=htext&filedir='
br08001_result = 'br08001.%s.pickle' % date

R2K = 'http://rest.kegg.jp/link/ko/reaction'
r2k_result = 'reaction_to_orthology.%s.pickle' % date
R2C = 'http://rest.kegg.jp/link/compound/reaction'
r2c_result = 'reaction_to_compound.%s.pickle' % date
C2R = 'http://rest.kegg.jp/link/reaction/compound'
c2r_result = 'compound_to_reaction.%s.pickle' % date
R2M = 'http://rest.kegg.jp/link/module/reaction'
r2m_result = 'reaction_to_module.%s.pickle' % date
M2R = 'http://rest.kegg.jp/link/reaction/module'
m2r_result = 'module_to_reaction.%s.pickle' % date
R2P = 'http://rest.kegg.jp/link/pathway/reaction'
r2p_result = 'reaction_to_pathway.%s.pickle' % date
P2R = 'http://rest.kegg.jp/link/reaction/pathway'
p2r_result = 'pathway_to_reaction.%s.pickle' % date
C   = 'http://rest.kegg.jp/list/compound'   
c_result = 'compound_descriptions.%s.pickle' % date
R   = 'http://rest.kegg.jp/list/reaction'
r_result = 'reaction_descriptions.%s.pickle' % date
P   = 'http://rest.kegg.jp/list/pathway'
p_result = 'pathway_descriptions.%s.pickle' % date
M   = 'http://rest.kegg.jp/list/module'
m_result = 'module_descriptions.%s.pickle' % date
R2RCLASS   = 'http://rest.kegg.jp/list/module'
r2rclass_result = 'reaction_to_rpair.%s.pickle' % date

def build_name_dict(url):
    output_dictionary = {}
    for entry in urllib2.urlopen(url).read().strip().split('\n'):
        sentry = entry.split('\t')
        key = sentry[0].split(':')[1]
        item = sentry[1].split(';')[0]
        output_dictionary[key]=item
    return output_dictionary    

def build_dict(url):
    output_dictionary = {}
    for entry in urllib2.urlopen(url).read().strip().split('\n'):
        key, item = [x.split(':')[1] for x in entry.split('\t')]
        if key in output_dictionary:
            output_dictionary[key].append(item)
        else:
            output_dictionary[key] = [item]
    return output_dictionary

print("Downloading reaction to orthology information from KEGG")
r2k = build_dict(R2K)
print("Done")
print("Pickling results: %s" % r2k_result)
pickle.dump(r2k, open(r2k_result, "wb"))

print("Downloading reaction to pathway information from KEGG")
r2p = build_dict(R2P)
print("Done")
print("Pickling results: %s" % r2p_result)
pickle.dump(r2p, open(r2p_result, "wb"))

print("Downloading pathway to reaction information from KEGG")
p2r = build_dict(P2R)
print("Done")
print("Pickling results: %s" %  p2r_result)
pickle.dump(p2r, open(p2r_result, "wb"))

print("Downloading reaction to module information from KEGG")
r2m = build_dict(R2M)
print("Done")
print("Pickling results: %s" % r2m_result)
pickle.dump(r2m, open(r2m_result, "wb"))

print("Downloading reaction to module information from KEGG")
m2r = build_dict(M2R)
print("Done")
print("Pickling results: %s" % m2r_result)
pickle.dump(m2r, open(m2r_result, "wb"))

print("Downloading reaction to compound information from KEGG")
r2c = build_dict(R2C)
print("Done")
print("Pickling results: %s" % r2c_result)
pickle.dump(r2c, open(r2c_result, "wb"))

print("Downloading compound to reaction information from KEGG")
c2r = build_dict(C2R)
print("Done")
print("Pickling results: %s" % c2r_result)
pickle.dump(c2r, open(c2r_result, "wb"))

print("Downloading compound descriptions from KEGG")
c   = build_name_dict(C)
print("Done")
print("Pickling results: %s" % c_result)
pickle.dump(c, open(c_result, "wb"))

print("Downloading pathway descriptions from KEGG")
p   = build_name_dict(P)
print("Done")
print("Pickling results: %s" % p_result)
pickle.dump(p, open(p_result, "wb"))

print("Downloading reaction descriptions from KEGG")
r   = build_name_dict(R)
print("Done")
print("Pickling results: %s" % r_result)
pickle.dump(r, open(r_result, "wb"))

print("Downloading module descriptions from KEGG")
m   = build_name_dict(M)
print("Done")
print("Pickling results: %s" % m_result)
pickle.dump(m, open(m_result, "wb"))


print("Downloading compound classification information from KEGG (br08001)")

A='A'
B='B'
C='C'
D='D'

for line in urllib2.urlopen(br08001).read().strip().split('\n'):
    if line.startswith(A):
        A_text = list(BeautifulSoup(line, "html.parser").find('b').stripped_strings)[0]
    elif line.startswith(B):
        if line.endswith('[Fig]\n'):  
            B_text = ' '.join([x for x in line.split(' ')[1:-1] if x])
        else:
            B_text = ' '.join(line.split()[1:])
    elif line.startswith(C):
        if line.endswith('[Fig]\n'):  
            C_text = ' '.join([x for x in line.split(' ')[1:-1] if x])
        else:
            C_text = ' '.join(line.split()[1:])
    elif line.startswith(D):
        CID = line.split()[1]
        D_text = ' '.join(line.split()[2:])
        if CID not in output_dict:
            output_dict[CID] = {A:[A_text],
                                B:[B_text],
                                C:[C_text],
                                D:[D_text]}
        else:
            output_dict[CID][A].append(A_text)
            output_dict[CID][B].append(B_text)
            output_dict[CID][C].append(C_text)
            output_dict[CID][D].append(D_text)

print("Pickling results: %s" % output_pickle)
pickle.dump(output_dict, open(br08001_result, "wb"))

print("Done")


print("Downloading rpair information from KEGG")
r2rclass={}
base='http://rest.kegg.jp/get/'
tot = float(len(r.keys()))
for idx, reaction_key in enumerate(r.keys()):
    url = base + reaction_key
    r2rclass[reaction_key]=[]
    try:
        for line in urllib2.urlopen(url).read().strip().split('\n'):
            if line.startswith('RCLASS'):
                r2rclass[reaction_key]+=line.split()[2:]
                
            elif line.startswith(' '):
                sline = line.split()
                if sline[0].startswith('RC'):
                    r2rclass[reaction_key]+=sline[1:]
    except:
        print reaction_key
    print "%s percent done" % str(round(float(idx+1)/tot, 2)*100)
    
print("Done")
print("Pickling results: %s" % m_result)
pickle.dump(r2rclass, open(r2rclass_result, "wb"))