# -*- coding: utf-8 -*-

"""
    Copyright © 2020 Galyfray
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this module.  If not, see <https://www.gnu.org/licenses/>.
"""
__author__ = "Galyfray"

import hjson
from googletrans import Translator

from os import path
from threading import Thread
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
    "zh-cn":"zh_CN",
    "zh-tw":"zh_TW"
}

class BundleTranslator(Thread):
    def __init__(self,to_translate:dict,lang:str,override:dict={}):
        Thread.__init__(self)
        self.bundle=dict(override)
        self.to_translate=dict(to_translate)
        self.lang=str(lang)
    
    def run(self):
        translator = Translator()
        override_keys=self.bundle.keys()
        keys = [k for k in self.to_translate.keys() if not(k in override_keys ) ]
        for key in keys :
            if self.to_translate[key] == "Oh No":
                self.bundle[key] = "Oh No"
            else :
                self.bundle[key]=translator.translate(self.to_translate[key],dest=self.lang).text

def write_bundle(bundle:dict,bundle_name:str):
    f = open(path.join("bundles" , bundle_name + ".properties"),"w+",encoding="utf8")
    for key in bundle.keys() :
        line = key + " = " + bundle[key] + "\n"
        f.write(line)
    f.close()

def parse_bundle(bundle_name:str):
    if path.exists(path.join("bundles" , bundle_name + ".properties")):
        with open(path.join("bundles" , bundle_name + ".properties"),"r",encoding="utf8") as f:
            bundle = {}
            for line in f.readlines():
                split = [k.strip() for k in line.split("=")]
                bundle[split[0]]=split[1]
        return bundle
    else :
        return {}

if not(path.exists("content") and (path.exists("mod.json") or path.exists("mod.hjson"))) :
    print("Please copy the content folder from your mod and the mod.(h)json to the script root to make it work")
else :
    mod={}
    #TODO Cleanup this
    if path.exists("mod.json"):
        with open("mod.json","r") as f :
            try:
                mod=hjson.loads(f.read())
            finally:
                f.close()
    else :
         with open("mod.hjson","r") as f :
            try:
                mod=hjson.loads(f.read())
            finally:
                f.close()
    mod_name = mod["name"].lower().replace(" ","-") + "-"
    # TODO adding recovery of older bundles and updates them instead of errasing everything
    # file chooser and making an ui or something better than the actual nonexistant CLI
    print("parsing Content to create default bundle")
    bundle = {}
    file_error = []
    uncompleate_data=[]
    # iterating over every files in the content folder and checking for the content type
    for folder in os.listdir("content"):
        if folder in content_type.keys():
            content = content_type[folder]
            for subdir, dirs, files in os.walk(path.join("content",folder)):
                for filename in files :
                    
                    # getting the unlocalized name of the content and keeping the type of the original content (json or hsjon)
                    json=False
                    if filename.endswith(".json"):
                        json=True
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
                    
                    # adding data to the bundle dic and removing existing description and name that would make the bundle not working properly
                    if (not(dat == None)) :
                        if (not (("name" in dat.keys() or "localizedName" in dat.keys()) and "description" in dat.keys())) :
                            uncompleate_data.append(path.join(subdir,filename))
                        if ("localizedName" in dat.keys()) :
                            bundle[content + mod_name + rawname + ".name"]=dat.pop("localizedName")
                        else:        
                            bundle[content + mod_name + rawname + ".name"]=dat.pop("name","Oh No")
                        bundle[content + mod_name + rawname + ".description"]=str(dat.pop("description","Oh No")).replace("\n","\\n")

                    # expoting back to it's original form without any anoying content
                    
                    with open(path.join(subdir,filename),'w+') as f :
                        if json :
                            hjson.dumpJSON(dat,f,indent="  ")
                        else :
                            hjson.dump(dat,f,indent="  ")
                    f.close()
                    
    if not ( path.exists("bundles") & path.isdir("bundles")):
        os.mkdir("bundles")
    # if we have an already made bundle then we use it to update the new one
    else : 
        if path.exists(path.join("bundles" , "bundle.properties")) :
            older = parse_bundle("bundle")
            bundle.update(older)
    
    write_bundle(bundle,"bundle")
    
    translators=[]

    for lang in langs :
        print("starting translation for lang :" + lang)
        older = parse_bundle("bundle_"+lang)
        trans = BundleTranslator(bundle,lang,older)
        trans.start()
        translators.append(trans)
    
    for translator in translators :
        translator.join()
        print("translation ended for lang :"  + translator.lang + " now writing")
        write_bundle(translator.bundle,"bundle_"+translator.lang)

    translators=[]

    for lang in  exept_languages.keys() :
        print("starting translation for lang :" + lang)
        older = parse_bundle("bundle_"+exept_languages[lang])
        trans = BundleTranslator(bundle,lang,older)
        trans.start()
        translators.append(trans)

    for translator in translators :
        translator.join()
        write_bundle(translator.bundle,"bundle_"+exept_languages[translator.lang])

    logger.log("latest","unable to parse files :\n" + "\n".join(file_error))
    logger.log("latest","unable to read description or name from files :" + "\n".join(uncompleate_data))

    print("Work done")
                        
                        