# -*- coding: utf-8 -*-
"""This is the utils library for the ET_biomarker project maintained by Qing Wang (Vincent)."
Functions:
private lib for databsing, parsing paper json file and citation json file.
"""
import pandas as pd
def parse_abs_file(_abs_path, COUNTRY_DICT, paper_df, author_df, affi_df, area_df, journal_df, paper_cont_df):
    import json
    # parser for paper file
    _paper = str(_abs_path).split("/")[-2]
    with open(_abs_path, 'r') as _abs_data:
        print("processing abstract file: ", _abs_path.name)
        abs_dict = json.load(_abs_data)
        ## paper metadata
        _tmp_paper_dict = {}
        _tmp_paper_dict["paper_id"] = _paper
        [_year_paper, _month_paper, _day_paper] = abs_dict["abstracts-retrieval-response"]["coredata"]["prism:coverDate"].split("-")
        _tmp_paper_dict["year"]  = _year_paper
        _tmp_paper_dict["date"] = abs_dict["abstracts-retrieval-response"]["coredata"]["prism:coverDate"]
        _tmp_paper_dict["type"] = abs_dict["abstracts-retrieval-response"]["coredata"]["subtype"]
        _tmp_paper_dict["journal_id"] = abs_dict["abstracts-retrieval-response"]["coredata"]["source-id"]
        if "openaccess" in abs_dict["abstracts-retrieval-response"]["coredata"].keys():
            _tmp_paper_dict["open_access"] = abs_dict["abstracts-retrieval-response"]["coredata"]["openaccess"]
        else:
            print("No open_access info...")
            _tmp_paper_dict["open_access"] = None
        _tmp_paper_dict["total_citatedby"] = abs_dict["abstracts-retrieval-response"]["coredata"]["citedby-count"]
        if "prism:doi" in abs_dict["abstracts-retrieval-response"]["coredata"].keys():
            _tmp_paper_dict["DOI"] = abs_dict["abstracts-retrieval-response"]["coredata"]["prism:doi"]
        else:
            print("No DOI info...")
            _tmp_paper_dict["DOI"] = None
        _tmp_paper_dict["title"] = abs_dict["abstracts-retrieval-response"]["coredata"]["dc:title"]
        # creating areas list
        _tmp_area_list= [{"area_id":_x["@code"], "area_abbrev":_x["@abbrev"], "area_name":_x["$"]}
                         for _x in abs_dict["abstracts-retrieval-response"]["subject-areas"]["subject-area"]]
        _tmp_paper_dict["area_list"] = _tmp_area_list

        ## creating author list
        _tmp_authors_list = []
        if isinstance(abs_dict["abstracts-retrieval-response"]["authors"], dict) and "author" in abs_dict["abstracts-retrieval-response"]["authors"].keys():
            for _iter_author_authorlist in abs_dict["abstracts-retrieval-response"]["authors"]["author"]:
                _tmp_author_dict_ = {}
                _tmp_author_dict_["seq"] = _iter_author_authorlist["@seq"]
                _tmp_author_dict_["author_id"] = _iter_author_authorlist["@auid"]
                _tmp_author_dict_["author_name"] = _iter_author_authorlist["ce:indexed-name"]
                _tmp_author_dict_["affi_id_list"] = []
                _tmp_author_dict_["dept_id_list"] = []
                if "affiliation" in _iter_author_authorlist.keys():
                    if isinstance(_iter_author_authorlist["affiliation"], list):
                        for _y in _iter_author_authorlist["affiliation"]:
                            _tmp_author_dict_["affi_id_list"].append(_y["@id"])
                    else:
                        _tmp_author_dict_["affi_id_list"] = [_iter_author_authorlist["affiliation"]["@id"]]
                else:
                    _tmp_author_dict_["affi_id_list"]=[]
                _tmp_authors_list.append(_tmp_author_dict_)
        else:
            print("No author information for paper: ", _paper)
            _tmp_authors_list = []

        ## Creating affiliation db
        _tmp_affi_list = []
        _tmp_affi_country_dict = {}
        _tmp_affi_city_dict = {}
        _author_group_lacking = 0
        if "author-group" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"].keys():
            _raw_affi_list = abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["author-group"]
            _num_affi = len(_raw_affi_list)
        else:
            _author_group_lacking = 1
            _raw_affi_list = []

        if _author_group_lacking == 0 and isinstance(_raw_affi_list, dict):
            __tmp_affi_dict={}
            __tmp_affi_dict["year"] = _year_paper
            if "affiliation" in _raw_affi_list.keys():
                if "@afid" in _raw_affi_list["affiliation"]:
                    __tmp_affi_dict["affi_id"] = _raw_affi_list["affiliation"]["@afid"]
                else:
                    __tmp_affi_dict["affi_id"] = None

                # handling affiliation name 
                if "organization" in _raw_affi_list["affiliation"].keys():
                    if isinstance(_raw_affi_list["affiliation"]["organization"], list):
                        __tmp_affi_dict["affi_name"] = _raw_affi_list["affiliation"]["organization"][-1]["$"]
                    else:
                        __tmp_affi_dict["affi_name"] = _raw_affi_list["affiliation"]["organization"]["$"]
                else:
                    __tmp_affi_dict["affi_name"] = None
                # handling department info
                if "@dptid" in _raw_affi_list["affiliation"].keys():
                    __tmp_affi_dict["dept_id"] = _raw_affi_list["affiliation"]["@dptid"]
                    if "organization" in _raw_affi_list["affiliation"].keys():
                        if len(_raw_affi_list["affiliation"]["organization"])>1:
                            __tmp_affi_dict["dept_name"] = _raw_affi_list["affiliation"]["organization"][0]["$"]
                        else:
                            __tmp_affi_dict["dept_name"] = _raw_affi_list["affiliation"]["organization"]["$"]
                    else:
                        __tmp_affi_dict["dept_name"] = None
                    # updating author dept relationship for author db

                    if isinstance(_raw_affi_list, dict) and "author" in _raw_affi_list.keys():
                        for _iter_author_in_dept in [ _x["@auid"] for _x in _raw_affi_list["author"] ]:
                            for _iter_i in range(len(_tmp_authors_list)):
                                if _tmp_authors_list[_iter_i]["author_id"] == _iter_author_in_dept:
                                    _tmp_authors_list[_iter_i]["dept_id_list"].append(_raw_affi_list["affiliation"]["@dptid"])
                else:
                    __tmp_affi_dict["dept_id"] = None
                    __tmp_affi_dict["dept_name"] = None
                    if isinstance(_raw_affi_list, dict) and "author" in _raw_affi_list.keys():
                        for _iter_author_in_dept in [ _x["@auid"] for _x in _raw_affi_list["author"] ]:
                            for _iter_i in range(len(_tmp_authors_list)):
                                if _tmp_authors_list[_iter_i]["author_id"] == _iter_author_in_dept:
                                    _tmp_authors_list[_iter_i]["dept_id_list"]=[]

                # use previous affiliation country and city to complete missing parts
                if "country" in _raw_affi_list["affiliation"].keys():
                    __tmp_country = _raw_affi_list["affiliation"]["country"]
                    __tmp_affi_dict["country"] = __tmp_country
                    _tmp_affi_country_dict[__tmp_affi_dict["affi_id"]] =__tmp_country
                    if __tmp_country not in COUNTRY_DICT.values():
                        COUNTRY_DICT[_raw_affi_list["affiliation"]["@country"]]=__tmp_country
                else:
                    __tmp_affi_dict["country"] = None
                    _tmp_affi_country_dict[__tmp_affi_dict["affi_id"]] = None

                if "city-group" in _raw_affi_list["affiliation"].keys():
                    __tmp_affi_dict["city"] = _raw_affi_list["affiliation"]["city-group"]
                    _tmp_affi_city_dict[__tmp_affi_dict["affi_id"]] = _raw_affi_list["affiliation"]["city-group"]
                else:
                    __tmp_affi_dict["city"] = None
                    _tmp_affi_city_dict[__tmp_affi_dict["affi_id"]] = None
                _tmp_affi_list.append(__tmp_affi_dict)

            else:
                __tmp_affi_dict["affi_id"] = None
                __tmp_affi_dict["affi_name"] = None
                __tmp_affi_dict["dept_id"] = None
                __tmp_affi_dict["dept_name"] = None

        elif _author_group_lacking == 0 and isinstance(_raw_affi_list, list):
            for _i in range(_num_affi-1,-1,-1):
                __tmp_affi_dict={}
                __tmp_affi_dict["year"] = _year_paper
                if "affiliation" in _raw_affi_list[_i].keys():
                    if "@afid" in _raw_affi_list[_i]["affiliation"]:
                        __tmp_affi_dict["affi_id"] = _raw_affi_list[_i]["affiliation"]["@afid"]
                    else:
                        __tmp_affi_dict["affi_id"] = None
                    # affiliation name 
                    if "organization" in _raw_affi_list[_i]["affiliation"].keys():
                        if isinstance(_raw_affi_list[_i]["affiliation"]["organization"], list):
                            __tmp_affi_dict["affi_name"] = _raw_affi_list[_i]["affiliation"]["organization"][-1]["$"]
                        else:
                            __tmp_affi_dict["affi_name"] = _raw_affi_list[_i]["affiliation"]["organization"]["$"]
                    else:
                        __tmp_affi_dict["affi_name"] = None
                   # handling department info
                    if "@dptid" in _raw_affi_list[_i]["affiliation"].keys():
                        __tmp_affi_dict["dept_id"] = _raw_affi_list[_i]["affiliation"]["@dptid"]
                        if "organization" in _raw_affi_list[_i]["affiliation"].keys():
                            if isinstance(_raw_affi_list[_i]["affiliation"]["organization"], list):
                                __tmp_affi_dict["dept_name"] = _raw_affi_list[_i]["affiliation"]["organization"][0]["$"]
                            elif isinstance(_raw_affi_list[_i]["affiliation"]["organization"], dict):
                                __tmp_affi_dict["dept_name"] = _raw_affi_list[_i]["affiliation"]["organization"]["$"]
                            else:
                                __tmp_affi_dict["dept_name"]=None
                        else:
                            __tmp_affi_dict["dept_name"]=None
                        # updating author dept relationship for author db
                        if "author" in _raw_affi_list[_i].keys():
                            for _iter_author_in_dept in [ _x["@auid"] for _x in _raw_affi_list[_i]["author"] ]:
                                for _iter_i in range(len(_tmp_authors_list)):
                                    if _tmp_authors_list[_iter_i]["author_id"] == _iter_author_in_dept:
                                        _tmp_authors_list[_iter_i]["dept_id_list"].append(_raw_affi_list[_i]["affiliation"]["@dptid"])
                    else:
                        __tmp_affi_dict["dept_id"] = None
                        __tmp_affi_dict["dept_name"] = None
                        if "author" in _raw_affi_list[_i].keys():
                            for _iter_author_in_dept in [ _x["@auid"] for _x in _raw_affi_list[_i]["author"] ]:
                                for _iter_i in range(len(_tmp_authors_list)):
                                    if _tmp_authors_list[_iter_i]["author_id"] == _iter_author_in_dept:
                                        _tmp_authors_list[_iter_i]["dept_id_list"].append(None)

                    # use previous affiliation country and city to complete missing parts
                    if "country" in _raw_affi_list[_i]["affiliation"].keys():
                        __tmp_country = _raw_affi_list[_i]["affiliation"]["country"]
                        __tmp_affi_dict["country"] = __tmp_country
                        _tmp_affi_country_dict[__tmp_affi_dict["affi_id"]] =__tmp_country
                        if __tmp_country not in COUNTRY_DICT.values():
                            COUNTRY_DICT[_raw_affi_list[_i]["affiliation"]["@country"]]=__tmp_country
                    elif ("affiliation" in _raw_affi_list[_i-1].keys()) and ("country" in _raw_affi_list[_i-1]["affiliation"].keys()) :
                        __tmp_affi_dict["country"] = _raw_affi_list[_i-1]["affiliation"]["country"]
                        _tmp_affi_country_dict[__tmp_affi_dict["affi_id"]] = _raw_affi_list[_i-1]["affiliation"]["country"]
                    else:
                        __tmp_affi_dict["country"] = None
                        _tmp_affi_country_dict[__tmp_affi_dict["affi_id"]] = None

                    if "city-group" in _raw_affi_list[_i]["affiliation"].keys():
                        __tmp_affi_dict["city"] = _raw_affi_list[_i]["affiliation"]["city-group"]
                        _tmp_affi_city_dict[__tmp_affi_dict["affi_id"]] = _raw_affi_list[_i]["affiliation"]["city-group"]
                    elif ("affiliation" in _raw_affi_list[_i-1].keys()) and ("city-group" in _raw_affi_list[_i-1]["affiliation"].keys()):
                        __tmp_affi_dict["city"] = _raw_affi_list[_i-1]["affiliation"]["city-group"]
                        _tmp_affi_city_dict[__tmp_affi_dict["affi_id"]] = _raw_affi_list[_i-1]["affiliation"]["city-group"]
                    else:
                        __tmp_affi_dict["city"] = None
                        _tmp_affi_city_dict[__tmp_affi_dict["affi_id"]] = None
                else:
                    __tmp_affi_dict["affi_id"] = None
                    __tmp_affi_dict["affi_name"] = None
                    __tmp_affi_dict["dept_id"] = None
                    __tmp_affi_dict["dept_name"] = None
                    __tmp_affi_dict["country"] = None
                    __tmp_affi_dict["city"] = None
                _tmp_affi_list.append(__tmp_affi_dict)
            # Affiliation db updated
            affi_df = pd.concat([affi_df, pd.DataFrame(_tmp_affi_list)], ignore_index=True)
            del __tmp_affi_dict
        else:
             _tmp_affi_list=[]
             print("No affiliation info for paper: ", _paper)
 
        _tmp_author_db_dict = []
        if len(_tmp_authors_list) > 0:
            for _iter_author in _tmp_authors_list:
                if len(_iter_author["affi_id_list"]) == 0:
                    _iter_author["city_list"] = []
                    _iter_author["country_list"] = []
                else:
                    _iter_author["city_list"] = [ _tmp_affi_city_dict[_x] for _x in _iter_author["affi_id_list"]]
                    _iter_author["country_list"] = [ _tmp_affi_country_dict[_x] for _x in _iter_author["affi_id_list"]]
                _tmp_author_dict={}
                _tmp_author_dict["author_id"] =_iter_author["author_id"]
                _tmp_author_dict["author_name"] = _iter_author["author_name"]
                _tmp_author_dict["year"] = _year_paper
                _tmp_author_dict["affi_id_list"] = _iter_author["affi_id_list"]
                _tmp_author_dict["city_list"] = _iter_author["city_list"]
                _tmp_author_dict["country_list"] = _iter_author["country_list"]
                _tmp_author_dict["dept_id_list"] = _iter_author["dept_id_list"]
                _tmp_author_db_dict.append(_tmp_author_dict)
            author_df = pd.concat([author_df, pd.DataFrame(_tmp_author_db_dict)], ignore_index=True)
        else:
            # author db updated
            print("No author info added in author db since no author info in paper:", _paper)
        del _tmp_author_db_dict
        
        _corresponding_author_lack = 0
        if _author_group_lacking == 0:
            if "correspondence" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"].keys() and isinstance(abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"], dict):
                if "person" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"].keys():
                    if "ce:indexed-name" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"]["person"].keys():
                        _tmp_corr_author_name = abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"]["person"]["ce:indexed-name"]
                    else:
                        _corresponding_author_lack = 1
                else:
                    _corresponding_author_lack = 1
                    _tmp_corr_author_name = None
                if "affiliation" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"].keys():
                    if "city-group" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"]["affiliation"].keys():
                        _tmp_paper_dict["corr_author_city"] = abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"]["affiliation"]
                    else:
                        _tmp_paper_dict["corr_author_city"] = None
                    if "country" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"]["affiliation"].keys():
                        _tmp_paper_dict["corr_author_country"] = abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"]["affiliation"]
                    else:
                        _tmp_paper_dict["corr_author_country"] = None
                    if "organization" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"]["affiliation"]:
                        _tmp_paper_dict["corr_author_affi_id"] = abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["correspondence"]["affiliation"]["organization"]
                else:
                    _corresponding_author_lack = 1
                    _tmp_corr_author_name = _tmp_authors_list[-1]["author_name"]
                    print("No corresponding author affiliation information found, using last author instead: ", _tmp_authors_list)
            else:
                _corresponding_author_lack = 1
                if len(_tmp_authors_list) > 0:
                    _tmp_corr_author_name = _tmp_authors_list[-1]["author_name"]
                    print("No corresponding information found, using last author instead: ", _tmp_authors_list)
                else:
                    _tmp_corr_author_name = None
                    print("No corresponding information found, no last author info found... ")
        else:
            print("No author info, thus no corresponding author info updated for paper lib...")
            # Update 1st, corresponding and authors list
        
        # updating first and corresponding author for paper db
        if len(_tmp_authors_list) > 0:
            for _iter_author_list in _tmp_authors_list:
                # first author
                if _iter_author_list["seq"]=="1":
                    _tmp_paper_dict["first_author_id"] = _iter_author_list["author_id"]
                    _tmp_paper_dict["first_author_city"] = _iter_author_list["city_list"]
                    _tmp_paper_dict["first_author_country"] = _iter_author_list["country_list"]
                    _tmp_paper_dict["first_author_affi_id"] = _iter_author_list["affi_id_list"]
                # corresponding author
                if _corresponding_author_lack == 0 and _iter_author_list["author_name"]==_tmp_corr_author_name:
                    _tmp_paper_dict["corr_author_id"] = _iter_author_list["author_id"]
                    if _corresponding_author_lack == 1:
                        _tmp_paper_dict["corr_author_city"] = _iter_author_list["city_list"]
                        _tmp_paper_dict["corr_author_country"] = _iter_author_list["country_list"]
                        _tmp_paper_dict["corr_author_affi_id"] = _iter_author_list["affi_id_list"]
                else:
                    _tmp_paper_dict["corr_author_id"] = None
                    _tmp_paper_dict["corr_author_city"] = None
                    _tmp_paper_dict["corr_author_country"] = None
                    _tmp_paper_dict["corr_author_affi_id"] = None
        else:
             _tmp_paper_dict["first_author_id"] = None
             _tmp_paper_dict["first_author_city"] = None
             _tmp_paper_dict["first_author_country"] = None
             _tmp_paper_dict["first_author_affi_id"] = None
             _tmp_paper_dict["corr_author_id"] = None
             _tmp_paper_dict["corr_author_city"] = None
             _tmp_paper_dict["corr_author_country"] = None
             _tmp_paper_dict["corr_author_affi_id"] = None
     
        # paper affiliation directly from scopus
        if "affiliation" in abs_dict["abstracts-retrieval-response"].keys():
            if isinstance(abs_dict["abstracts-retrieval-response"]["affiliation"], list):
                _tmp_paper_dict["affi_id"] = [_y["@id"] for _y in abs_dict["abstracts-retrieval-response"]["affiliation"]]
                _tmp_paper_dict["affi_name"] = [_y["affilname"] for _y in abs_dict["abstracts-retrieval-response"]["affiliation"]]
                _tmp_paper_dict["affi_city"] = [_y["affiliation-city"] for _y in abs_dict["abstracts-retrieval-response"]["affiliation"]]
                _tmp_paper_dict["affi_country"] = [_y["affiliation-country"] for _y in abs_dict["abstracts-retrieval-response"]["affiliation"]]
            else:
                _tmp_paper_dict["affi_id"] = abs_dict["abstracts-retrieval-response"]["affiliation"]["@id"]
                _tmp_paper_dict["affi_name"] = abs_dict["abstracts-retrieval-response"]["affiliation"]["affilname"]
                _tmp_paper_dict["affi_city"] = abs_dict["abstracts-retrieval-response"]["affiliation"]["affiliation-city"]
                _tmp_paper_dict["affi_country"] = abs_dict["abstracts-retrieval-response"]["affiliation"]["affiliation-country"]
        else:
            _tmp_paper_dict["affi_id"] = None
            _tmp_paper_dict["affi_name"] = None
            _tmp_paper_dict["affi_city"] = None
            _tmp_paper_dict["affi_country"] = None

        #
        _tmp_paper_dict["author_country_affi_list"] = _tmp_authors_list
        # paper db updated.
        paper_df = pd.concat([paper_df, pd.DataFrame([_tmp_paper_dict])], ignore_index=True)
        del _tmp_paper_dict, _tmp_authors_list

        ## areas db updated
        _tmp_area_db_list = []
        for _area in _tmp_area_list:
            _tmp_area_dict={}
            _tmp_area_dict["area_id"] = _area["area_id"]
            _tmp_area_dict["area_abbrev"] = _area["area_abbrev"]
            _tmp_area_dict["area_name"] = _area["area_name"]
            _tmp_area_dict["paper_id"] = _paper
            _tmp_area_dict["year"] = _year_paper
            _tmp_area_db_list.append(_tmp_area_dict)
        area_df = pd.concat([area_df, pd.DataFrame(_tmp_area_db_list)], ignore_index=True)
        del _tmp_area_db_list

        ## journal db updated
        _tmp_journal_dict={}
        _tmp_journal_dict["journal_id"] = abs_dict["abstracts-retrieval-response"]["coredata"]["source-id"]
        _tmp_journal_dict["journal_name"] = abs_dict["abstracts-retrieval-response"]["coredata"]["prism:publicationName"]
        if "dc:publisher" in abs_dict["abstracts-retrieval-response"]["coredata"].keys():
            _tmp_journal_dict["publisher"] = abs_dict["abstracts-retrieval-response"]["coredata"]["dc:publisher"]
        else:
            _tmp_journal_dict["publisher"] = None
        if "@country" in abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["source"]:
            _tmp_journal_dict["country"] = abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["source"]["@country"]
        else:
            _tmp_journal_dict["country"] = None
        _tmp_journal_dict["IF_year_list"] = []
        _tmp_journal_dict["Quantile_year_list"] = []
        # journal db updated
        journal_df = pd.concat([journal_df, pd.DataFrame([_tmp_journal_dict])], ignore_index=True)
        del _tmp_journal_dict

        ## paper content db
        _tmp_paper_content_dict = {}
        _tmp_paper_content_dict["paper_id"] = _paper
        _tmp_paper_content_dict["year"] = _year_paper
        _tmp_paper_content_dict["month"] = _month_paper
        _tmp_paper_content_dict["type"] = abs_dict["abstracts-retrieval-response"]["coredata"]["subtype"]
        _tmp_paper_content_dict["area_list"] = _tmp_area_list
        _tmp_paper_content_dict["title" ] = abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["citation-title"]
        _tmp_paper_content_dict["abstract"] = abs_dict["abstracts-retrieval-response"]["item"]["bibrecord"]["head"]["abstracts"]
        paper_cont_df = pd.concat([paper_cont_df, pd.DataFrame([_tmp_paper_content_dict])], ignore_index=True)
        del _tmp_paper_content_dict
    return paper_df, author_df, affi_df, area_df, journal_df, paper_cont_df, COUNTRY_DICT

def parse_citation_file(_citation_path_list, cite_df):
    import json
    _paper = str(_citation_path_list[0]).split("/")[-2]
    # parser for citation file
    _tmp_cited_list=[]
    _cited_no_affi_cnt = 0
    no_aff_paper_list = []
    for _citation_path in _citation_path_list: 
        with open(_citation_path, 'r') as _cite_data:
            print("processing citation file: ", _citation_path.name)
            citation_dict = json.load(_cite_data)
            for _iter_cited_paper_info in citation_dict["search-results"]["entry"]:
                #display(_iter_cited_paper_info)
                _tmp_cited_dict={}
                _tmp_cited_dict["paper_id"] = _paper
                _tmp_cited_dict["cite_paper_id"] = _iter_cited_paper_info['dc:identifier'].strip(" ").split(":")[-1]
                if 'dc:title' in _iter_cited_paper_info.keys():
                    _tmp_cited_dict["title"] = _iter_cited_paper_info['dc:title']
                else:
                    _tmp_cited_dict["title"] = None
                [_year_paper, _month_paper, _day_paper] = _iter_cited_paper_info['prism:coverDate'].split("-")
                _tmp_cited_dict["year"] = _year_paper
                _tmp_cited_dict["date"] = _iter_cited_paper_info['prism:coverDate']
                _tmp_cited_dict["type"] = _iter_cited_paper_info["subtype"]
                _tmp_cited_dict["cited_by"] = _iter_cited_paper_info["citedby-count"]
                if 'affiliation' in _iter_cited_paper_info.keys():
                    _tmp_cited_dict["affi_list"] = [ {"affi_id":_x["afid"], "affi_name":_x["affilname"], "affi_city":_x["affiliation-city"],
                                                   "affi_country":_x["affiliation-country"]} for _x in _iter_cited_paper_info['affiliation'] ]
                else:
                    _tmp_cited_dict["affi_list"]=[]
                    _cited_no_affi_cnt=_cited_no_affi_cnt+1
                    no_aff_paper_list.append(_tmp_cited_dict["cite_paper_id"])
                _tmp_cited_list.append(_tmp_cited_dict)        
    print(_cited_no_affi_cnt, " cited papers has no affliliations...")        
    cite_df = pd.concat([cite_df, pd.DataFrame(_tmp_cited_list)], ignore_index=True)
    return cite_df, no_aff_paper_list