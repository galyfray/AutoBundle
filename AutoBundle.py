# -*- coding: utf-8 -*-
import hjson
from googletrans import Translator

from os import path  
import os
import traceback
import sys

from logger import logger

sys.stderr = logger()

content_type = {
    "items":"item.",
    "blocks":"block.",
    "mechs":"mech.",
    "liquids":"liquid.",
    "units":"unit."
}

# storing all languages supported by mindustry
langs = [
    "cs",
    "de",
    "es",
    "et",
    "eu",
    "fr_BE",
    "fr",
    #"in_ID", # Not suported by googletrans
    "it",
    "ja",
    "ko",
    "nl_BE",
    "nl",
    "pl",
    "pt_BR",
    "pt",
    "ru",
    "sv",
    #"tk", # Not suported by googletrans
    "tr",
    "uk_UA",
]
# storing language where there is differrence between mindutry norm and google norm
exept_languages = {
    "zh_CN":"zh-cn",
    "zh_TW":"zh-tw"
}

def write_bundle(bundle:dict,bundle_name:str):
    f = open(path.join("bundles" , bundle_name + ".properties"),"w+",encoding="utf8")
    for key in bundle.keys() :
        line = key + " = " + bundle[key] + "\n"
        f.write(line)
    f.close()

if not(path.exists("content")) :
    print("Please copy the content folder from your mod to the script root to make it work")
else :
    print("parsing Content to create default bundle")
    bundle = {}
    file_error = []
    uncompleate_data=[]
    for folder in os.listdir("content"):
        if folder in content_type.keys():
            content = content_type[folder]
            for subdir, dirs, files in os.walk(path.join("content",folder)):
                for filename in files :
                    if filename.endswith(".json"):
                        rawname = filename[:-5]
                    else:
                        rawname = filename[:-6]
                    with open(path.join(subdir,filename),'r') as f :
                        dat = None
                        try:
                            dat = hjson.loads(f.read())
                        except Exception as error:
                            file_error.append(path.join(subdir,filename))
                            logger.log("SeralisationError","#===#===#===# Seralisation Error Start #===#===#===#")
                            logger.log("SeralisationError","Unable to read JSON file : " + path.join(subdir,filename))
                            for lines in traceback.format_exception(type(error), error, error.__traceback__):
                                logger.log("SeralisationError",lines)
                        finally:
                            f.close()
                    if (not(dat == None)) :
                        if (not (("name" in dat.keys() or "localizedName" in dat.keys()) and "description" in dat.keys())) :
                            uncompleate_data.append(path.join(subdir,filename))
                        if ("localizedName" in dat.keys()) :
                            bundle[content + rawname + ".name"]=dat.get("localizedName")
                        else:        
                            bundle[content + rawname + ".name"]=dat.get("name","Oh No")
                        bundle[content + rawname + ".description"]=str(dat.get("description","Oh No")).replace("\n","\\n")
    if not ( path.exists("bundles") & path.isdir("bundles") ):
        os.mkdir("bundles")
    write_bundle(bundle,"bundle")
    
    for lang in langs :
        print("translating and writing for lang :" + lang)
        trans_bundle={}
        translator = Translator()
        for key in bundle.keys() :
            if bundle[key] == "Oh No":
                trans_bundle[key] = "Oh No"
            else :
                trans_bundle[key]=translator.translate(bundle[key],dest=lang).text
        write_bundle(trans_bundle,"bundle_"+lang)

    for lang in  exept_languages.keys() :
        print("translating and writing for lang :" + lang)
        trans_bundle={}
        translator = Translator()
        for key in bundle.keys() :
            if bundle[key] == "Oh No":
                trans_bundle[key] = "Oh No"
            else :
                trans_bundle[key]=translator.translate(bundle[key],dest=exept_languages[lang]).text
        write_bundle(trans_bundle,"bundle_"+lang)

    logger.log("latest","unable to parse files :\n" + "\n".join(file_error))
    logger.log("latest","unable to read description or name from files :" + "\n".join(uncompleate_data))

    print("Work done")
                        
                        