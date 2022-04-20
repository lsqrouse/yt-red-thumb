import pickle
dict_prefix = './dicts/'
def save_dict(dictionary,File):
    with open(dict_prefix + File, "wb") as myFile:
        pickle.dump(dictionary, myFile)
        myFile.close()

def load_dict(File):
    with open(dict_prefix + File, "rb") as myFile:
        dict = pickle.load(myFile)
        myFile.close()
        return dict

empty_dict = {}
used_words = load_dict('used_words.dict')
parsed_vids = load_dict('parsed_vids.dict')

print(str(used_words.keys()))
print(str(parsed_vids.keys()))

print('\n')
print(str(len(used_words.keys())))
print(str(len(parsed_vids.keys())))

save_dict(empty_dict, 'used_words.dict')
save_dict(empty_dict, 'parsed_vids.dict')