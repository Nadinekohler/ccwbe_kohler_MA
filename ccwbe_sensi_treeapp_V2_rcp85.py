import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd
import os
import shapefile
import shapely
#import pyshp
from osgeo import ogr
import psycopg2
import sqlalchemy
import geoalchemy2
from sqlalchemy import create_engine
import xlrd
import openpyxl


#*************************************
#functions
def givenexthigheraltitudinalvegetationbelt(in_belt):
    if in_belt=="obersubalpin":
        out_belt="obersubalpin"
    elif in_belt == "subalpin":
        out_belt = "obersubalpin"
    elif "hochmontan" in in_belt:
        out_belt="subalpin"
    elif in_belt=="obermontan":
        out_belt="hochmontan"
    elif in_belt=="untermontan":
        out_belt="obermontan"
    elif in_belt=="submontan":
        out_belt="untermontan"
    elif in_belt=="unter- & obermontan":
        out_belt="hochmontan"
    elif in_belt=="collin":
        out_belt = "submontan"
    elif in_belt=="collin mit Buche":
        out_belt = "submontan"
    elif in_belt=="hyperinsubrisch":
        out_belt = "collin mit Buche"
    return out_belt
def givenextloweraltitudinalvegetationbelt(in_belt, in_standortregion):
    out_belt=in_belt
    if in_belt=="obersubalpin":
        out_belt="subalpin"
    elif in_belt=="subalpin":
        out_belt="hochmontan"
    elif "hochmontan" in in_belt and in_standortregion not in ["5", "5a", "5b", "4", "Me"]:
        out_belt="obermontan"
    elif "hochmontan" in in_belt and in_standortregion in ["5", "5a", "5b", "4", "Me"]:
        out_belt="unter- & obermontan"
    elif in_belt=="obermontan":
        out_belt="untermontan"
    elif in_belt=="untermontan":
        out_belt="submontan"
    elif in_belt in ["unter- & obermontan", "unter-/obermontan"] and in_standortregion in ["5", "5a", "5b", "Me"]:
        out_belt="collin mit Buche"
    elif in_belt in ["unter- & obermontan", "unter-/obermontan"] and in_standortregion in ["2b","3", "4"]:
        out_belt="collin"
    elif in_belt=="submontan" and in_standortregion not in ["2b","3", "4","5", "5a", "5b", "Me"]:
        out_belt="collin mit Buche"
    elif in_belt=="submontan" and in_standortregion in ["2b","3", "4"]:
        out_belt="collin"
    elif in_belt=="collin mit Buche":
        out_belt="hyperinsubrisch"
    elif in_belt=="collin" and in_standortregion in ["5", "5a", "5b", "Me"]:
        out_belt="hyperinsubrisch"
    elif in_belt=="hyperinsubrisch":
        out_belt="hyperinsubrisch"
    return out_belt
def give_standortregionencombi_from_projektionspfade(in_Standortregion):
    if in_Standortregion in ["1","J","M","2","2a","2b","3"]:# and in_hoehenstufe != "collin":
        out_combi="R, J, M, 1, 2, 3"
    #elif in_Standortregion in ["1","J","M","2","2a","2b","3"]:# and in_hoehenstufe == "collin":
        #out_combi = "R J, M,1, 2 Beginn co "
    elif in_Standortregion == "4":
        out_combi = "R 4"
    elif in_Standortregion in ["5","5a","5b"]:
        out_combi = "R 5"
    elif in_Standortregion == "Me":
        out_combi = "R Mendrisiotto"
    else:
        out_combi=""
    return out_combi
def give_future_foresttype_from_projectionspathways(sto_heute,hs_heute,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion,instandortregionplain,inslope,inlage, inradiation):
    #create a  query from projections pathways
    sto_zukunft = ""
    #if intannenareal_heute ==
    if hs_heute==hs_zukunft:
        sto_zukunft=sto_heute
    else:
        if [instandortregion,sto_heute,hs_heute,hs_zukunft] in pairsofforesttypesandaltitudinalvegetationbelts_inprojektionspfade:
            query_possiblepathways=projectionswegedf[((projectionswegedf["Standortstyp_heute"]==sto_heute) & (projectionswegedf["Standortsregionen"]==instandortregion))]
            if "hochmontan" in hs_zukunft:
                query_possiblepathwayszukunft=query_possiblepathways[query_possiblepathways["Hoehenstufe_Zukunft"].isin([hs_zukunft,"hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne"])]
            else:
                query_possiblepathwayszukunft = query_possiblepathways[query_possiblepathways["Hoehenstufe_Zukunft"] == hs_zukunft]
            if len(query_possiblepathwayszukunft)==0:
                sto_zukunft="nopath"
            elif len(query_possiblepathwayszukunft)==1:
                sto_zukunft=query_possiblepathwayszukunft["Standortstyp_Zukunft"].tolist()[0]
            else:
                #check conditions
                # tannenareal
                # hochmontan
                if "hochmontan" in query_possiblepathwayszukunft["Standortstyp_Zukunft"].unique().tolist():
                    if intannenareal_zukunft == 1:
                        query_possiblepathwayszukunft1 = query_possiblepathwayszukunft[(
                                    (query_possiblepathwayszukunft["Hoehenstufe_Zukunft"] == "hochmontan") & (
                                        query_possiblepathwayszukunft[
                                            "Tannenareal_Zukunft"] == "Hauptareal"))]  # Hauptareal der Tanne"]
                    elif intannenareal_zukunft == 2:
                        query_possiblepathwayszukunft1 = query_possiblepathwayszukunft[(
                                    (query_possiblepathwayszukunft["Hoehenstufe_Zukunft"] == "hochmontan") & (
                                        query_possiblepathwayszukunft[
                                            "Tannenareal_Zukunft"] == "Nebenareal"))]  # Nebenareal der Tanne"]
                    elif intannenareal_zukunft == 3:
                        query_possiblepathwayszukunft1 = query_possiblepathwayszukunft[(
                                    (query_possiblepathwayszukunft["Hoehenstufe_Zukunft"] == "hochmontan") & (
                                        query_possiblepathwayszukunft[
                                            "Tannenareal_Zukunft"] == "Reliktareal"))]  # Reliktareal der Tanne"]
                else:
                    query_possiblepathwayszukunft1=query_possiblepathwayszukunft
                if len(query_possiblepathwayszukunft1) == 0:
                    sto_zukunft = "no path"
                elif len(query_possiblepathwayszukunft1) == 1:
                    sto_zukunft = query_possiblepathwayszukunft1["Standortstyp_Zukunft"].tolist()[0]
                else:
                # Standortregion
                    if len(query_possiblepathwayszukunft1["Standortsregion"].unique().tolist()) > 1:
                        if instandortregionplain == "3":
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(['2b, 3', '3', '1, 2, 3'])]
                        elif instandortregionplain == "2a":
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(
                                    ['M, J, 1, 2a', '1, 2, 3', 'J, M, 1, 2a'])]
                        elif instandortregionplain == "2b":
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(['2b, 3', '2b', '1, 2, 3'])]
                        elif instandortregionplain in ['M', 'J']:
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(
                                    ['M, J, 1, 2a', 'J, M', 'J, M, 1, 2a'])]
                        elif instandortregionplain == '1':
                            query_possiblepathwayszukunft2= query_possiblepathwayszukunft[
                                query_possiblepathwayszukunft["Standortsregion"].isin(
                                    ['M, J, 1, 2a', 'J, M, 1, 2a', '1, 2, 3'])]
                        else:
                            query_possiblepathwayszukunft2 = query_possiblepathwayszukunft1
                    else:
                        query_possiblepathwayszukunft2=query_possiblepathwayszukunft1
                    if len(query_possiblepathwayszukunft2) == 0:
                        sto_zukunft = "no path"
                    elif len(query_possiblepathwayszukunft2) == 1:
                        sto_zukunft = query_possiblepathwayszukunft2["Standortstyp_Zukunft"].tolist()[0]
                    else:
                        #inslope
                        inslopeconditions =query_possiblepathwayszukunft2["Hangneigung"].unique().tolist()
                        if len(inslopeconditions)>1 and inslope in inslopeconditions:
                            query_possiblepathwayszukunft3 = query_possiblepathwayszukunft2[query_possiblepathwayszukunft2["Hangneigung"] == inslope]
                        else:
                            query_possiblepathwayszukunft3=query_possiblepathwayszukunft2
                        if len(query_possiblepathwayszukunft3) == 0:
                            sto_zukunft = "no path"
                        elif len(query_possiblepathwayszukunft3) == 1:
                            sto_zukunft = query_possiblepathwayszukunft3["Standortstyp_Zukunft"].tolist()[0]
                        else:
                            #inlage
                            if len(query_possiblepathwayszukunft3["Relief"].unique().tolist())>1 and inlage ==2:
                                query_possiblepathwayszukunft4 = query_possiblepathwayszukunft3[query_possiblepathwayszukunft3["Relief"] == 'Hang- und Muldenlage']
                            elif len(query_possiblepathwayszukunft3["Relief"].unique().tolist())>1 and inlage ==3:
                                query_possiblepathwayszukunft4 = query_possiblepathwayszukunft3[query_possiblepathwayszukunft3["Relief"].isin(['Hang- oder Muldenlage','Hang- und Muldenlage'])]
                            elif len(query_possiblepathwayszukunft3["Relief"].unique().tolist())>1 and inlage ==4:
                                query_possiblepathwayszukunft4 = query_possiblepathwayszukunft3[query_possiblepathwayszukunft3["Relief"] == 'Kuppenlage']
                            else:
                                query_possiblepathwayszukunft4=query_possiblepathwayszukunft3
                            if len(query_possiblepathwayszukunft4) == 0:
                                sto_zukunft = "no path"
                            elif len(query_possiblepathwayszukunft4) == 1:
                                sto_zukunft = query_possiblepathwayszukunft4["Standortstyp_Zukunft"].tolist()[0]
                            else:
                                # Weitere (inradiation)
                                if len(query_possiblepathwayszukunft4["Weitere"].unique().tolist()) > 1:
                                    if inradiation == "-1":
                                        query_possiblepathwayszukunft5 = query_possiblepathwayszukunft4[query_possiblepathwayszukunft4["Weitere"].isin(['schattig, kühl','kühl'])]
                                    elif inradiation == "1":
                                        query_possiblepathwayszukunft5 = query_possiblepathwayszukunft4[query_possiblepathwayszukunft4["Standortsregion"].isin(['warm','warm und strahlungsreich'])]
                                    elif inradiation == "0":
                                        query_possiblepathwayszukunft5 = query_possiblepathwayszukunft4[query_possiblepathwayszukunft4["Standortsregion"].isin([nan,"","normal", " "])]
                                    else:
                                        query_possiblepathwayszukunft5 = query_possiblepathwayszukunft4
                                else:
                                    query_possiblepathwayszukunft5=query_possiblepathwayszukunft4
                                if len(query_possiblepathwayszukunft5) == 0:
                                    sto_zukunft = "no path"
                                elif len(query_possiblepathwayszukunft5) >= 1:
                                    sto_zukunft = query_possiblepathwayszukunft5["Standortstyp_Zukunft"].tolist()[0]
    return sto_zukunft
def count_changes_altitudinalvegetationbelts(hs_in, hs_out):
    count=0
    if hs_in==hs_out:
        count=0
    elif "hochmontan" in hs_in and "hochmontan" in hs_out:
        count =0
    elif hs_in == 'obersubalpin' and hs_out!=hs_in:
        if hs_out=="subalpin":
            count=1
        elif hs_out in ["hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
            count=2
        elif hs_out in ["obermontan","unter-/obermontan", "unter- & obermontan"]:
            count=3
        elif hs_out in ["untermontan"]:
            count=4
        elif hs_out in ["submontan"]:
            count=5
        elif hs_out in ["collin", "collin mit Buche"]:
            count=6
        elif hs_out in ["hyperinsubrisch"]:
            count=7
        elif hs_out in ["mediterran"]:
            count=8
    elif hs_in == 'subalpin' and hs_out!=hs_in:
        if hs_out in ["hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
            count=1
        elif hs_out in ["obermontan","unter-/obermontan", "unter- & obermontan"]:
            count=2
        elif hs_out in ["untermontan"]:
            count=3
        elif hs_out in ["submontan"]:
            count=4
        elif hs_out in ["collin", "collin mit Buche"]:
            count=5
        elif hs_out in ["hyperinsubrisch"]:
            count=6
        elif hs_out in ["mediterran"]:
            count=7
    elif  hs_out!=hs_in and hs_in in ["hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        if hs_out in ["obermontan","unter-/obermontan", "unter- & obermontan"]:
            count=1
        elif hs_out in ["untermontan"]:
            count=2
        elif hs_out in ["submontan"]:
            count=3
        elif hs_out in ["collin", "collin mit Buche"]:
            count=4
        elif hs_out in ["hyperinsubrisch"]:
            count=5
        elif hs_out in ["mediterran"]:
            count=6
    elif hs_in == "obermontan" and hs_out!=hs_in:
        if hs_out in ["untermontan"]:
            count=1
        elif hs_out in ["submontan"]:
            count=2
        elif hs_out in ["collin", "collin mit Buche"]:
            count=3
        elif hs_out in ["hyperinsubrisch"]:
            count=4
        elif hs_out in ["mediterran"]:
            count=5
    elif hs_in in ["unter-/obermontan", "unter- & obermontan"] and hs_out!=hs_in:
        if hs_out in ["submontan"]:
            count=1
        elif hs_out in ["collin", "collin mit Buche","hyperinsubrisch"]:
            count=1
        elif hs_out in ["mediterran"]:
            count=2
    elif hs_in== "untermontan" and hs_out!=hs_in:
        if hs_out in ["submontan"]:
            count=1
        elif hs_out in ["collin", "collin mit Buche"]:
            count=2
        elif hs_out in ["hyperinsubrisch"]:
            count=3
        elif hs_out in ["mediterran"]:
            count=4
    elif hs_in == "submontan" and hs_out!=hs_in:
        if hs_out in ["collin", "collin mit Buche"]:
            count=1
        elif hs_out in ["hyperinsubrisch"]:
            count=2
        elif hs_out in ["mediterran"]:
            count=3
    elif hs_in =="collin mit Buche" and hs_out!=hs_in:
        if hs_out in ["hyperinsubrisch"]:
            count=1
        elif hs_out in ["mediterran"]:
            count=2
        elif "collin" in hs_out:
            count=0
    elif hs_in == "collin" and hs_out!=hs_in:
        if hs_out in ["mediterran"]:
            count=1
    else:
        count=0
    return count
def is_hszukunft_higherthan_hsheute(hsheute,hszukunft):
    if hsheute=="subalpin" and hszukunft=="obersubalpin":
        out=True
    elif "hochmontan" in hsheute and hszukunft in ["subalpin","obersubalpin"]:
        out=True
    elif "obermontan" in hsheute and hszukunft in ["subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    elif "unter" in hsheute and hszukunft in ["obermontan","subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    elif "submontan" in hsheute and hszukunft in ["unter-/obermontan","unter- & obermontan","untermontan","obermontan","subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    elif "collin" in hsheute and hszukunft in ["submontan","unter-/obermontan","unter- & obermontan","untermontan","obermontan","subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    elif "hyperinsubrisch" in hsheute and hszukunft in ["collin", "collin mit Buche","submontan","unter-/obermontan","unter- & obermontan","untermontan","obermontan","subalpin","obersubalpin","hochmontan","hochmontan Hauptareal der Tanne","hochmontan Nebenareal der Tanne","hochmontan Reliktareal der Tanne","hochmontan im Tannen-Hauptareal","hochmontan im Tannen-Nebenareal","hochmontan im TannenReliktareal"]:
        out=True
    else:
        out=False
def concatenate_pathways(sto_heute, hs_heute, hs_zukunft, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope, inlage, inradiation):
    if count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 1:
        outnais=give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hs_zukunft, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope, inlage, inradiation)
    elif hs_heute =="obersubalpin" and hs_zukunft=="collin" and instandortregionplain in ["2b","3","4"]:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,
                                                                            intannenareal_heute, intannenareal_zukunft,
                                                                            instandortregion, instandortregionplain,
                                                                            inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1,
                                                                            hsintermediary2, intannenareal_heute,
                                                                            intannenareal_zukunft, instandortregion,
                                                                            instandortregionplain, inslope, inlage,
                                                                            inradiation)
        if naisintermediary2 in hochmontandirektzucollinlist:
            outnais = give_future_foresttype_from_projectionspathways(naisintermediary2, hsintermediary2, hs_zukunft,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregionplain in ["2b","3","4"]:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,
                                                                            intannenareal_heute, intannenareal_zukunft,
                                                                            instandortregion, instandortregionplain,
                                                                            inslope, inlage, inradiation)
        outnais = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hs_zukunft,
                                                                  intannenareal_heute, intannenareal_zukunft,
                                                                  instandortregion, instandortregionplain, inslope,
                                                                  inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 2:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary1,hsintermediary1,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 3:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hsintermediary2,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary2,hsintermediary2,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 4:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hsintermediary2,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary3 = givenextloweraltitudinalvegetationbelt(hsintermediary2, instandortregion)
        naisintermediary3 = give_future_foresttype_from_projectionspathways(naisintermediary2, hsintermediary2,hsintermediary3, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary3,hsintermediary3,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 5:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hsintermediary2,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary3 = givenextloweraltitudinalvegetationbelt(hsintermediary2, instandortregion)
        naisintermediary3 = give_future_foresttype_from_projectionspathways(naisintermediary2, hsintermediary2,hsintermediary3, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        hsintermediary4 = givenextloweraltitudinalvegetationbelt(hsintermediary3, instandortregion)
        naisintermediary4 = give_future_foresttype_from_projectionspathways(naisintermediary3, hsintermediary3,hsintermediary4, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary4,hsintermediary4,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    elif count_changes_altitudinalvegetationbelts(hs_heute, hs_zukunft) == 6:
        hsintermediary1 = givenextloweraltitudinalvegetationbelt(hs_heute, instandortregionplain)
        naisintermediary1 = give_future_foresttype_from_projectionspathways(sto_heute, hs_heute, hsintermediary1,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary2 = givenextloweraltitudinalvegetationbelt(hsintermediary1, instandortregion)
        naisintermediary2 = give_future_foresttype_from_projectionspathways(naisintermediary1, hsintermediary1, hsintermediary2,intannenareal_heute, intannenareal_zukunft,instandortregion, instandortregionplain, inslope, inlage, inradiation)
        hsintermediary3 = givenextloweraltitudinalvegetationbelt(hsintermediary2, instandortregion)
        naisintermediary3 = give_future_foresttype_from_projectionspathways(naisintermediary2, hsintermediary2,hsintermediary3, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        hsintermediary4 = givenextloweraltitudinalvegetationbelt(hsintermediary3, instandortregion)
        naisintermediary4 = give_future_foresttype_from_projectionspathways(naisintermediary3, hsintermediary3,hsintermediary4, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        hsintermediary5 = givenextloweraltitudinalvegetationbelt(hsintermediary4, instandortregion)
        naisintermediary5 = give_future_foresttype_from_projectionspathways(naisintermediary4, hsintermediary4,hsintermediary5, intannenareal_heute,intannenareal_zukunft, instandortregion, instandortregionplain, inslope,inlage, inradiation)
        outnais=give_future_foresttype_from_projectionspathways(naisintermediary5,hsintermediary5,hs_zukunft,intannenareal_heute,intannenareal_zukunft,instandortregion, instandortregionplain, inslope,inlage, inradiation)
    else:
        outnais="no path c"
    return outnais
def correct_nopaths_exemptions(instandortregion,instandortregionplain,sto_heute,hs_heute,hs_zukunft, codetannenareal, inslope, inlage, inradiation):
    #correct combinations with no paths
    nais_zukunft_out= "no path"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25as', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '42Q', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '33m', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '4', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="3L/4L"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25a', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="25a med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '32V', 'collin mit Buche', 'collin']:
        nais_zukunft_out="32C"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '42Q', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="42Q med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '42C', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="42C med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '33m', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="33m med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '40P', 'collin mit Buche', 'collin']:
        nais_zukunft_out="40Pt"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25au', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="25au med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25au', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25as', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="25as med"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '33V', 'collin mit Buche', 'collin']:
        nais_zukunft_out="3L/4L"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '42C', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '4', 'collin mit Buche', 'collin']:
        nais_zukunft_out="3L/4L"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '25a', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '32C', 'collin mit Buche', 'collin']:
        nais_zukunft_out=sto_heute
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R 5', '3', 'hyperinsubrisch', 'mediterran']:
        nais_zukunft_out="42V med"
    if instandortregion in ["R 5", "R 4", "R Mendrisiotto"] and hs_heute in ["collin","collin mit Buche", "hyperinsubrisch"] and hs_zukunft=="mediterran" and sto_heute in ["3","4","47","19LP","25a","25as""25au","32*","32V","33m","33V","40P","42C","42Q"]:
        nais_zukunft_out = sto_heute+" med"
    if instandortregion in ["R 5", "R 4", "R Mendrisiotto"] and hs_heute in ["collin","collin mit Buche", "hyperinsubrisch"] and hs_zukunft=="mediterran" and sto_heute2 in ["3","4","47","19LP","25a","25as""25au","32*","32V","33m","33V","40P","42C","42Q"]:
        combinations_df.loc[index, "naiszuk2"] = sto_heute2+" med"
    if instandortregion =="R, J, M, 1, 2, 3" and hs_heute =="submontan" and hs_zukunft=="collin" and sto_heute in ["18","19","20","51","52","18*","18M","18v","18w","1h","24*","27h","32*","32V","53*"]:
        nais_zukunft_out = sto_heute+" med"
    if instandortregion =="R, J, M, 1, 2, 3" and hs_heute =="submontan" and hs_zukunft=="collin" and sto_heute2 in ["18","19","20","51","52","18*","18M","18v","18w","1h","24*","27h","32*","32V","53*"]:
        combinations_df.loc[index, "naiszuk2"] = sto_heute2+" med"
    #AV
    if sto_heute=="AV" and hs_zukunft in ["collin mit Buche","hyperinsubrisch"]:
        nais_zukunft_out = "25au"
    if sto_heute=="AV" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "50 collin"
    if sto_heute=="AV" and hs_zukunft =="collin" and instandortregion in ["R 4", "R 5"]:
        nais_zukunft_out = "25au"
    if sto_heute=="AV" and hs_zukunft in ["unter- & obermontan"]:
        nais_zukunft_out = "25au"
    if sto_heute=="AV" and hs_zukunft in ["hochmontan, subalpin"]:
        nais_zukunft_out = "AV"
    if sto_heute=="AV" and hs_heute=="subalpin" and hs_zukunft == "hochmontan":
        nais_zukunft_out = "50"
    if sto_heute=="AV" and hs_heute=="obersubalpin" and hs_zukunft == "hochmontan":
        nais_zukunft_out = "47D"
    #N
    if sto_heute=="19L" and hs_heute == "obermontan" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "3"
    if sto_heute=="10a" and hs_heute == "untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "10a"
    if sto_heute=="10a" and hs_heute == "untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "10a collin"
    if sto_heute=="23" and hs_heute in ["hochmontan", "obermontan"] and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "23 collin"
    if sto_heute=="23" and hs_heute in ["hochmontan", "obermontan"] and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "25* collin"
    if sto_heute=="40*" and hs_heute == "obersubalpin" and hs_zukunft=="hochmontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute=="47" and hs_heute =="obermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "42t"
    if sto_heute=="47" and hs_heute =="obermontan" and hs_zukunft =="collin mit Buche" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "42t"
    if sto_heute=="47" and hs_heute =="obermontan" and hs_zukunft =="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "47"
    if sto_heute=="47" and hs_heute =="obermontan" and hs_zukunft =="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "47"
    if sto_heute=="51" and hs_heute in ["hochmontan", "obermontan"] and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "51 collin"
    if sto_heute=="51" and hs_heute =="hochmontan" and hs_zukunft in ["submontan","untermontan", "unter- & obermontan"] and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="51" and hs_heute =="hochmontan" and hs_zukunft =="obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18"
    if sto_heute=="51" and hs_heute =="untermontan" and hs_zukunft =="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="52" and hs_heute =="untermontan" and hs_zukunft =="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18*"
    if sto_heute=="52" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "52 collin"
    if sto_heute=="52" and hs_heute =="obermontan" and hs_zukunft =="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute=="52" and hs_heute =="obermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14 collin"
    if sto_heute=="53" and hs_heute =="subalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "62 collin"
    if sto_heute=="65" and hs_heute =="obermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute=="19L" and hs_heute =="obermontan" and hs_zukunft =="collin mit Buche" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "3L/4L"
    if sto_heute=="29A" and hs_heute =="obermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "29A collin"
    if sto_heute=="41*" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "41* collin"
    if sto_heute=="46M" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "46M collin"
    if sto_heute=="50P" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7S collin"
    if sto_heute=="53*" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34b"
    if sto_heute=="53*" and hs_heute =="untermontan" and hs_zukunft =="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute=="53VM" and hs_heute =="subalpin" and hs_zukunft in ["untermontan", "unter- & obermontan", "submontan"] and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "19L"
    if sto_heute=="53VM" and hs_heute =="subalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34a"
    if sto_heute=="58Bl" and hs_heute =="subalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "47H collin"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft =="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "1"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "1 collin"
    if sto_heute=="59C" and hs_heute =="obersubalpin" and hs_zukunft =="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34* collin"
    if sto_heute=="60A" and hs_heute =="subalpin" and hs_zukunft =="collin mit Buche" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "50 collin"
    if sto_heute=="51C" and hs_heute in ["hochmontan", "obermontan"] and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "51 collin"
    if sto_heute=="51Re" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "51 collin"
    if sto_heute=="53*" and hs_heute in ["hochmontan", "obermontan", "untermontan"] and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "53* collin"
    if sto_heute=="56" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "45 collin"
    if sto_heute=="56" and hs_heute =="hochmontan" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute=="65" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "68 collin"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "41* collin"
    if sto_heute=="25*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "25* collin"
    if sto_heute=="29A" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "29A collin"
    if sto_heute=="32C" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "32C collin"
    if sto_heute=="32C" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "28 collin"
    if sto_heute=="32V" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "32C collin"
    if sto_heute=="32V" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "32C"
    if sto_heute=="40*" and hs_heute in ["obersubalpin", "untermontan"] and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute=="59" and hs_heute =="obersubalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "19a"
    if sto_heute=="32S" and hs_heute =="subalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "28"
    if sto_heute=="32S" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "28 collin"
    if sto_heute=="40PBl" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "40PBl collin"
    if sto_heute=="40PBl" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "34* collin"
    if sto_heute=="41*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "41* collin"
    if sto_heute=="46M" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "1h"
    if sto_heute=="50P" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "20"
    if sto_heute=="51Re" and hs_heute =="hochmontan" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3" and codetannenareal in [0,1,2]:
        nais_zukunft_out = "51"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3" and codetannenareal==3:
        nais_zukunft_out = "54A"
    if sto_heute=="49*" and hs_heute =="subalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "26h"
    if sto_heute=="49*Ta" and hs_heute =="hochmontan" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "26h"
    if sto_heute=="59H" and hs_heute =="subalpin" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18"
    if sto_heute=="59H" and hs_heute =="obersubalpin" and hs_zukunft=="obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "18"
    if sto_heute=="60A" and hs_heute =="subalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "20"
    if sto_heute=="51" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain in ["2b", "3"]:
        nais_zukunft_out = "51 collin"
    if sto_heute=="51" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "7a collin"
    if sto_heute=="53" and hs_heute in ["obermontan", "untermontan"] and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "62"
    if sto_heute=="29A" and hs_heute =="obermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain not in ["2b", "3"]:
        nais_zukunft_out = "29A collin"
    if sto_heute=="51C" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a"
    if sto_heute=="51Re" and hs_heute =="hochmontan" and hs_zukunft=="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="51Re" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a"
    if sto_heute=="57VM" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            if tannenareal_heute== 3:
                nais_zukunft_out = "54A collin"
            else:
                nais_zukunft_out = "51 collin"
        else:
            nais_zukunft_out = "7a collin"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "55* collin"
    if sto_heute=="60*Ta" and hs_heute =="obermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute=="19" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "6"
    if sto_heute=="19" and hs_heute in ["hochmontan"] and hs_zukunft in ["collin"] and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "6 collin"
    if sto_heute=="19" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "6 collin"
    if sto_heute=="19" and hs_heute =="hochmontan" and hs_zukunft=="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8d"
    if sto_heute=="55*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            nais_zukunft_out = "55* collin"
        else:
            nais_zukunft_out = "1 collin"
    if sto_heute=="55*" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "1"
    if sto_heute=="47Re" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "25a"
    if sto_heute=="18*" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute=="18*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14 collin"
    if sto_heute=="18*" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute=="18*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "14 collin"
    if sto_heute=="50*" and hs_heute =="untermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "50* collin"
        else:
            nais_zukunft_out = "9a collin"
    if sto_heute=="57C" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"] and codetannenareal in [1,2]:
            nais_zukunft_out = "51 collin"
        elif instandortregionplain in ["2b","3"] and codetannenareal==3:
            nais_zukunft_out = "55 collin"
    if sto_heute=="53*s" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            nais_zukunft_out = "53* collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute=="59A" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if codetannenareal==3:
            if instandortregionplain in ["2b","3"]:
                nais_zukunft_out = "50 collin"
            else:
                nais_zukunft_out = "7S collin"
        else:
            if instandortregionplain in ["2b", "3"]:
                nais_zukunft_out = "50 collin"
            else:
                nais_zukunft_out = "7S collin"
    if sto_heute=="59A" and hs_heute =="subalpin" and hs_zukunft=="hochmontan" and instandortregion =="R, J, M, 1, 2, 3":
        if codetannenareal==3:
            nais_zukunft_out = "50Re"
        else:
            nais_zukunft_out = "50"
    if sto_heute=="40*" and hs_heute =="hochmontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute=="40*" and hs_heute =="obermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute=="40*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute=="40*" and hs_heute =="obermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute=="53*" and hs_heute =="obermontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if codetannenareal == 3:
            nais_zukunft_out = "53* collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute=="53*" and hs_heute =="submontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if codetannenareal == 3:
            nais_zukunft_out = "53* collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute=="53*" and hs_heute =="obermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute=="53*" and hs_heute =="untermontan" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute=="69" and hs_heute in ["obermontan", "untermontan"] and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["J", "M"]:
            nais_zukunft_out = "38"
        else:
            nais_zukunft_out = "40*"
    if sto_heute=="69" and hs_heute in ["obermontan", "untermontan"] and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute=="59E" and hs_heute =="obersubalpin" and hs_zukunft=="unter- & obermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "53Ta"
    if sto_heute=="59H" and hs_heute =="obersubalpin" and hs_zukunft=="untermontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "8a"
    if sto_heute=="59H" and hs_heute =="obersubalpin" and hs_zukunft=="submontan" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a"
    if sto_heute=="59H" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "7a collin"
    if sto_heute=="59H" and hs_heute in ["obersubalpin","hochmontan"] and hs_zukunft in ["collin","submontan","untermontan"] and instandortregion =="R, J, M, 1, 2, 3" and instandortregionplain in ["2b","3"]:
        if tannenareal_heute in [1,2]:
            nais_zukunft_out = "51 collin"
        else:
            nais_zukunft_out = "54A collin"
    if sto_heute=="59R" and hs_heute =="obersubalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34* collin"
    if sto_heute=="59R" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "34* collin"
    if sto_heute=="67*" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        nais_zukunft_out = "38 collin"
    if sto_heute == "53*s" and hs_heute == "subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "53* collin"
    if sto_heute == "59E" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "53* collin"
    if sto_heute == "10a" and hs_heute == "untermontan" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "10a"
    if sto_heute == "47" and hs_heute == "obermontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "3"
    if sto_heute=="32*" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion =="R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "32* collin"
        else:
            nais_zukunft_out = "26 collin"
    if sto_heute == "19" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "6 collin"
    if sto_heute == "47Re" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "25a"
    if sto_heute == "18*" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute == "18*" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "14"
    if sto_heute == "57C" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if codetannenareal == 3:
            nais_zukunft_out = "55 collin"
        else:
            nais_zukunft_out = "51 collin"
    if sto_heute == "59A" and hs_heute == "subalpin" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        if codetannenareal == 3:
            nais_zukunft_out = "50Re"
        else:
            nais_zukunft_out = "50"
    if sto_heute == "40*" and hs_heute == "hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute == "53*" and hs_heute == "untermontan" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute == "53*" and hs_heute == "submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "53* collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute == "69" and hs_heute == "submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "62 collin"
    if sto_heute == "69" and hs_heute == "untermontan" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "38"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '10a', 'untermontan', 'submontan']:
        nais_zukunft_out='10a'
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '47', 'obermontan', 'untermontan']:
        nais_zukunft_out='3'
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '19', 'hochmontan', 'collin']:
        nais_zukunft_out='6 collin'
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '69', 'submontan', 'collin']:
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "62 collin"
    if [instandortregion,sto_heute, hs_heute, hs_zukunft]==['R, J, M, 1, 2, 3', '69', 'untermontan', 'submontan']:
        nais_zukunft_out = "38"
    #***************************
    #S
    if sto_heute=="24" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="24" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="25a" and hs_heute =="hyperinsubrisch" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="32*" and hs_heute =="collin mit Buche" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "27"
    if sto_heute=="32V" and hs_heute =="collin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "32C"
    if sto_heute=="32V" and hs_heute =="collin mit Buche" and hs_zukunft=="hyperinsubrisch" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "32C"
    if sto_heute=="42C" and hs_heute =="obersubalpin" and hs_zukunft=="subalpin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42C"
    if sto_heute=="47" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="47" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="47" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a med"
    if sto_heute=="56" and hs_heute == "hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "27"
    if sto_heute=="56" and hs_heute == "subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "27"
    if sto_heute=="58" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="58" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42C"
    if sto_heute=="59" and hs_heute =="obersubalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42V"
    if sto_heute=="59*" and hs_heute =="obersubalpin" and hs_zukunft=="subalpin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "47*"
    if sto_heute=="AV" and hs_heute =="obersubalpin" and hs_zukunft=="subalpin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "AV"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42r"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42r"
    if sto_heute=="68" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42r med"
    if sto_heute=="60" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="60" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="19LP" and hs_heute =="unter- & obermontan" and hs_zukunft=="submontan" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "19LP"
    if sto_heute=="25a" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="25as" and hs_heute =="collin" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as med"
    if sto_heute=="25as" and hs_heute =="collin mit Buche" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as med"
    if sto_heute=="25au" and hs_heute =="collin mit Buche" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au med"
    if sto_heute=="25au" and hs_heute =="collin" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au med"
    if sto_heute=="32*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "27"
    if sto_heute=="32C" and hs_heute =="collin" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "32C med"
    if sto_heute=="32C" and hs_heute =="collin mit Buche" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "32C med"
    if sto_heute=="32V" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "28 med"
    if sto_heute=="33V" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "33m"
    if sto_heute=="40P" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "40Pt"
    if sto_heute=="40P" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "40P med"
    if sto_heute=="42C" and hs_heute =="obersubalpin" and hs_zukunft=="hochmontan" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42C"
    if sto_heute=="47*" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3LV"
    if sto_heute=="47*" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3LV"
    if sto_heute=="47*" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="47*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "33a"
    if sto_heute=="47D" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="47D" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="47D" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="47DRe" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="47H" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as"
    if sto_heute=="47H" and hs_heute =="hochmontan" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as"
    if sto_heute=="47H" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as med"
    if sto_heute=="47M" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "34a"
    if sto_heute=="47Re" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="50*" and hs_heute =="hochmontan" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25b"
    if sto_heute=="55*" and hs_heute =="hochmontan" and hs_zukunft=="mediterran" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q med"
    if sto_heute=="57Bl" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="57Bl" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="57C" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="57C" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="57C" and hs_heute =="obersubalpin" and hs_zukunft=="unter- & obermontan" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "19a"
    if sto_heute=="57V" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25a"
    if sto_heute=="57V" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="58Bl" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25as"
    if sto_heute=="58Bl" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="58C" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="58C" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="58L" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "42Q"
    if sto_heute=="59*" and hs_heute =="obersubalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3a"
    if sto_heute=="59*" and hs_heute =="obersubalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="59*" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3a"
    if sto_heute=="59*" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="59*" and hs_heute =="obersubalpin" and hs_zukunft=="unter- & obermontan" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "4"
    if sto_heute=="60A" and hs_heute =="subalpin" and hs_zukunft=="collin" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "25au"
    if sto_heute=="60A" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4", "R 5", "R Mendrisiotto"]:
        nais_zukunft_out = "3L/4L"
    if sto_heute=="57V" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 4"]:
        nais_zukunft_out = "42V"
    if sto_heute=="57V" and hs_heute =="subalpin" and hs_zukunft=="collin mit Buche" and instandortregion in ["R 5"]:
        nais_zukunft_out = "42t"
    if sto_heute == "46M" and hs_heute in ["hochmontan", "collin mit Buche"] and hs_zukunft == "mediterran" and instandortregion == "R 5":
        nais_zukunft_out = "42V med"
    if sto_heute == "46M" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R 5":
        nais_zukunft_out = "42V"
    if sto_heute == "46M" and hs_heute =="hochmontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R 5":
        nais_zukunft_out = "42V"
    if sto_heute == "46M" and hs_heute =="hochmontan" and hs_zukunft == "unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "3"
    if sto_heute == "46M" and hs_heute =="unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 5":
        nais_zukunft_out = "42V"
    if sto_heute == "42Q" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R 5":
        nais_zukunft_out = "42Q"
    if sto_heute == "42Q" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    #
    if sto_heute == "24" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25a"
    if sto_heute == "25a" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25a"
    if sto_heute == "25a" and hs_heute =="hochmontan" and hs_zukunft == "mediterran" and instandortregion == "R 4":
        nais_zukunft_out = "25a"
    if sto_heute == "58" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "55* collin"
    if sto_heute == "58Bl" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25as"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "59" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        if inslope >=3:#57C
            if codetannenareal<=2:#47M
                nais_zukunft_out = "34a"
            else:
                nais_zukunft_out = "34a"
        else:#57V
            nais_zukunft_out = "42V"
    if sto_heute == "70" and hs_heute in ["obersubalpin", "subalpin"] and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "70" and hs_heute in ["obersubalpin", "subalpin"] and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "71" and hs_heute in ["obersubalpin", "subalpin"] and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "47*Lä" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "48 collin"
    if sto_heute == "AV" and hs_heute in ["obersubalpin"] and hs_zukunft in ["untermontan", "obermontan"] and instandortregion == "R 4":
        nais_zukunft_out = "AV"
    if sto_heute == "32C" and hs_heute in ["hyperinsubrisch"] and hs_zukunft =="collin" and instandortregion == "R 5":
        nais_zukunft_out = "32C collin"
    if sto_heute == "33m" and hs_heute in ["hyperinsubrisch"] and hs_zukunft =="collin" and instandortregion == "R 5":
        nais_zukunft_out = "33m"
    if sto_heute == "42C" and hs_heute in ["hyperinsubrisch"] and hs_zukunft =="collin" and instandortregion == "R 5":
        nais_zukunft_out = "42C"
    if sto_heute == "47*" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "4"
    if sto_heute == "57Bl" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "24*"
    if sto_heute == "57C" and hs_heute =="obersubalpin" and hs_zukunft in ["collin", "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "3L/4L"
    if sto_heute == "57V" and hs_heute =="obersubalpin" and hs_zukunft in ["collin", "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "3L/4L"
    if sto_heute == "57V" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "19a"
    if sto_heute == "58" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "3s"
    if sto_heute == "58Bl" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "47H"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft in ["collin", "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "42Q"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "3s"
    if sto_heute == "70" and hs_heute =="obersubalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "68"
    if sto_heute == "70" and hs_heute =="subalpin" and hs_zukunft in ["collin", "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "42r"
    if sto_heute == "16" and hs_heute =="untermontan" and hs_zukunft =="collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["J","M"]:
            nais_zukunft_out = "39 collin"
        elif instandortregionplain in ["1","2a", "2b","3"]:
            nais_zukunft_out = "40* collin"
        else:
            nais_zukunft_out = "25e collin"
    if sto_heute == "32V" and hs_heute =="obermontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "28 collin"
    if sto_heute == "40*" and hs_heute =="submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute == "41*" and hs_heute =="submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "41* collin"
    if sto_heute == "47H" and hs_heute =="obermontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "25as"
    if sto_heute == "56" and hs_heute =="obermontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["J", "M", "2a", "1"]:
            nais_zukunft_out = "45"
        else:
            nais_zukunft_out = "45"
    if sto_heute == "57S" and hs_heute =="subalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if inslope>=2:
            nais_zukunft_out = "46"
        else:
            nais_zukunft_out = "46*"
    if sto_heute == "57V" and hs_heute =="subalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if inslope>=2:
            nais_zukunft_out = "19"
        else:
            nais_zukunft_out = "46"
    if sto_heute == "58" and hs_heute =="subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "1h"
    if sto_heute == "59" and hs_heute =="obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            nais_zukunft_out = "48 collin"
        else:
            nais_zukunft_out = "22 collin"
    if sto_heute == "59H" and hs_heute =="obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if codetannenareal <= 2:
            if inlage == 4:
                nais_zukunft_out = "19"
            else:
                nais_zukunft_out = "18"
        else:
            nais_zukunft_out = "18"
    if sto_heute == "60" and hs_heute =="subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "20"
    if sto_heute == "67" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "67" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "69" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "69" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "70" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "70" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "71" and hs_heute =="subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "71"
    if sto_heute == "71" and hs_heute =="obermontan" and hs_zukunft == "mediterran" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute == "18w" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["J","M","1","2a"]:
            nais_zukunft_out = "17 collin"
        else:
            nais_zukunft_out = "17"
    if sto_heute == "18w" and hs_heute =="hochmontan" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "18w" and hs_heute =="subalpin" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "32*" and hs_heute =="subalpin" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "32*"
    if sto_heute == "40*" and hs_heute =="submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40* collin"
    if sto_heute == "46M" and hs_heute =="obermontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "46M collin"
        else:
            nais_zukunft_out = "1 collin"
    if sto_heute == "58LLä" and hs_heute =="hochmontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "55* collin"
        else:
            nais_zukunft_out = "1 collin"
    if sto_heute == "58LLä" and hs_heute =="obersubalpin" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "55*Lä"
    if sto_heute == "60*Ta" and hs_heute =="obermontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "67G" and hs_heute =="obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "67G" and hs_heute =="subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "38 collin"
    if sto_heute == "69G" and hs_heute in ["subalpin","obersubalpin"] and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "65 collin"
        else:
            if instandortregionplain in ["J", "M"]:
                nais_zukunft_out = "38 collin"
            else:
                nais_zukunft_out = "40* collin"
    if sto_heute == "70G" and hs_heute in ["subalpin","obersubalpin"] and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "71G" and hs_heute == "obermontan" and hs_zukunft == "mediterran" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45 collin"
    if sto_heute == "71G" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "71G"
    if sto_heute == "59A" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25au"
    if sto_heute == "70G" and hs_heute in ["subalpin", "obersubalpin"] and hs_zukunft in ["collin" , "collin mit Buche"] and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "71G" and hs_heute == "obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "44"
    if sto_heute == "70G" and hs_heute in ["subalpin", "obersubalpin"] and hs_zukunft in ["collin" , "collin mit Buche"] and instandortregion == "R 5":
        nais_zukunft_out = "42r"
    if sto_heute == "70G" and hs_heute == "obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R 5":
        nais_zukunft_out = "68"
    if sto_heute == "46M" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R 5":
        nais_zukunft_out = "42V"
    if sto_heute == "46M" and hs_heute == "unter- & obermontan" and hs_zukunft == "mediterran" and instandortregion == "R 5":
        nais_zukunft_out = "42V med"
    if sto_heute == "57C" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "19"
    if sto_heute == "70G" and hs_heute =="obersubalpin" and hs_zukunft in ["collin" , "collin mit Buche"] and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    if sto_heute == "70G" and hs_heute =="subalpin" and hs_zukunft in ["collin" , "collin mit Buche"] and instandortregion == "R 4":
        nais_zukunft_out = "42r"
    #rcp45
    if sto_heute == "47*Lä" and hs_heute =="subalpin" and hs_zukunft =="unter- & obermontan" and instandortregion == "R 4":
        nais_zukunft_out = "19a"
    if sto_heute == "57C" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "57C"
    if sto_heute == "57V" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "57V"
    if sto_heute == "58" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "58"
    if sto_heute == "58Bl" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "58Bl"
    if sto_heute == "58C" and hs_heute =="obersubalpin" and hs_zukunft =="subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "58C"
    if sto_heute == "56" and hs_heute == "hochmontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute == "58C" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "1h"
    if sto_heute == "59" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "48"
    if sto_heute == "59L" and hs_heute == "obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "1h"
    if sto_heute == "70" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "68"
    if sto_heute == "71" and hs_heute == "obermontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute == "18*" and hs_heute == "hochmontan" and hs_zukunft == "obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "18*"
    if sto_heute == "18*" and hs_heute == "hochmontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if inlage==4:
            nais_zukunft_out = "15"
        else:
            nais_zukunft_out = "14"
    if sto_heute == "18w" and hs_heute == "hochmontan" and hs_zukunft == "obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "18w"
    if sto_heute == "18w" and hs_heute == "hochmontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "18w" and hs_heute == "subalpin" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "17"
    if sto_heute == "40*" and hs_heute == "hochmontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute == "52" and hs_heute == "obermontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        if inlage == 4:
            nais_zukunft_out = "15"
        else:
            nais_zukunft_out = "14"
    if sto_heute == "53*" and hs_heute == "obermontan" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "62"
    if sto_heute == "58LLä" and hs_heute == "obersubalpin" and hs_zukunft == "subalpin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "58LLä"
    if sto_heute == "67G" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b","3"]:
            nais_zukunft_out = "65 collin"
        else:
            nais_zukunft_out = "65 collin"
    if sto_heute == "67G" and hs_heute == "subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute == "69G" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute == "69G" and hs_heute == "subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "65 collin"
    if sto_heute == "70G" and hs_heute == "obersubalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "70G" and hs_heute == "subalpin" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        if instandortregionplain in ["2b", "3"]:
            nais_zukunft_out = "68 collin"
        else:
            nais_zukunft_out = "41* collin"
    if sto_heute == "70G" and hs_heute == "subalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "68"
    if sto_heute == "71G" and hs_heute == "obermontan" and hs_zukunft == "collin mit Buche" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45"
    if sto_heute == "71G" and hs_heute in ["subalpin","obersubalpin"] and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "71G"
    if sto_heute == "70G" and hs_heute == "obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R 5":
        if inradiation ==1:
            nais_zukunft_out = "42r"
        else:
            nais_zukunft_out = "68"
    #rcp26
    if sto_heute == "57Bl" and hs_heute == "obersubalpin" and hs_zukunft == "subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "57Bl"
    if sto_heute == "70" and hs_heute == "obersubalpin" and hs_zukunft == "subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "70"
    #neue Runde
    if sto_heute == "24" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "25a"
    if sto_heute == "32*" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "27"
    if sto_heute == "40P" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "40Pt"
    if sto_heute == "40PBl" and hs_heute == "unter- & obermontan" and hs_zukunft == "collin" and instandortregion == "R 4":
        nais_zukunft_out = "40PBlt"
    if sto_heute == "58" and hs_heute == "obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "58Bl" and hs_heute == "obersubalpin" and hs_zukunft == "collin mit Buche" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "68" and hs_heute == "hochmontan" and hs_zukunft == "untermontan" and instandortregion == "R 4":
        nais_zukunft_out = "68"
    if sto_heute == "AV" and hs_heute == "subalpin" and hs_zukunft in ["untermontan", "obermontan"] and instandortregion == "R 4":
        nais_zukunft_out = "AV"
    if sto_heute == "32*" and hs_heute == "hochmontan" and hs_zukunft =="mediterran" and instandortregion == "R 5":
        nais_zukunft_out = "27"
    if sto_heute == "40PBl" and hs_heute == "hochmontan" and hs_zukunft =="mediterran" and instandortregion == "R 5":
        nais_zukunft_out = "25as"
    if sto_heute in ["58", "58Bl"] and hs_heute == "obersubalpin" and "collin" in hs_zukunft and instandortregion == "R 5":
        nais_zukunft_out = "42Q"
    if sto_heute == "70" and hs_heute == "obersubalpin" and hs_zukunft =="collin mit Buche" and instandortregion == "R 5":
        nais_zukunft_out = "42r"
    if sto_heute == "25*" and hs_heute =="submontan" and hs_zukunft == "collin" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "25* collin"
    if sto_heute == "71" and hs_heute =="obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45 collin"
    if sto_heute == "71" and hs_heute =="obersubalpin" and hs_zukunft == "unter- & obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "45 collin"
    if sto_heute == "32*" and hs_heute =="obermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "32*"
    if sto_heute == "40*" and hs_heute =="collin" and hs_zukunft == "submontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    #rcp26
    if sto_heute == "42Q" and hs_heute =="collin" and hs_zukunft == "hochmontan" and instandortregion == "R 4":
        nais_zukunft_out = "42Q"
    if sto_heute == "70G" and hs_heute == "obersubalpin" and hs_zukunft == "subalpin" and instandortregion == "R 5":
        nais_zukunft_out = "70G"
    if sto_heute == "18*" and hs_heute =="obermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "18*"
    if sto_heute == "18w" and hs_heute =="obermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "18w"
    if sto_heute == "19" and hs_heute =="obermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "19"
    if sto_heute == "40*" and hs_heute =="collin" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute == "40*" and hs_heute =="collin" and hs_zukunft == "obermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    if sto_heute == "40*" and hs_heute =="collin" and hs_zukunft == "untermontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    #LI
    if sto_heute == "24*" and hs_heute =="untermontan" and hs_zukunft == "hochmontan" and instandortregion == "R, J, M, 1, 2, 3":
        nais_zukunft_out = "40*"
    return nais_zukunft_out
def heuteempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft].isin(["a","b"])]
        extrdf3=extrdf2[extrdf2["grtreeid"].notnull()]
        treelist=extrdf3["grtreeid"].unique().tolist()#).replace("[","").replace("]","").replace(",","").replace("'","")
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heutebedingtempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft]=="c"]
        extrdf3=extrdf2[extrdf2["grtreeid"].notnull()]
        treelist=extrdf3["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heutegefaehrdet(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_heute].isin(["a","b","c"])]
        extrdf2=extrdf[extrdf[sto_zukunft]!="a"]
        extrdf3 = extrdf2[extrdf2[sto_zukunft] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_zukunft] != "c"]
        extrdf5=extrdf4[extrdf4["grtreeid"].notnull()]
        treelist=extrdf5["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def heuteachtung(naismatrixdf,sto_heute, sto_zukunft):
    treelist = []
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf = naismatrixdf[naismatrixdf[sto_heute].isin(["a", "b", "c"])]
        extrdf2 = extrdf[extrdf[sto_zukunft].isin(["a", "b", "c"])]
        if len(extrdf2)>0 and "Ailanthus altissima" in extrdf2["Namelat"].unique().tolist():
            treelist = ["Ailanthus altissima"]
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_zukunft].isin(["a","b"])]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        treelist=extrdf4["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftbedingtempfohlen(naismatrixdf,sto_heute, sto_zukunft):
    treelist=[]
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf=naismatrixdf[naismatrixdf[sto_zukunft]=="c"]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        treelist=extrdf4["grtreeid"].unique().tolist()
        if "" in treelist:
            treelist.remove("")
    else:
        treelist=["notinnaismatrix"]
    return treelist
def zukunftachtung(naismatrixdf,sto_heute, sto_zukunft):
    treelist = []
    if sto_heute in nais_matrix_standorte_list and sto_zukunft in nais_matrix_standorte_list:
        extrdf = naismatrixdf[naismatrixdf[sto_zukunft].isin(["a", "b", "c"])]
        extrdf2 = extrdf[extrdf[sto_heute] != "a"]
        extrdf3 = extrdf2[extrdf2[sto_heute] != "b"]
        extrdf4 = extrdf3[extrdf3[sto_heute] != "c"]
        if len(extrdf4)>0 and "Ailanthus altissima" in extrdf4["Namelat"].unique().tolist():
            treelist = ["Ailanthus altissima"]
    else:
        treelist=["notinnaismatrix"]
    return treelist
def logikUebergang(x,y):
    u=""
    if x=="a":
        if y=="a":
            u="a"
        elif y=="b":
            u="a"
        elif y=="c":
            u="b"
        elif y in ["","ex"]:
            u="c"
    elif x=="b":
        if y=="a":
            u="b"
        elif y=="b":
            u="b"
        elif y=="c":
            u="b"
        elif y in ["","ex"]:
            u="c"
    elif x=="c":
        if y=="a":
            u="b"
        elif y=="b":
            u="c"
        elif y=="c":
            u="c"
        elif y in ["","ex"]:
            u=""
    elif x=="ex":
        if y=="a":
            u="c"
        elif y=="b":
            u="c"
        elif y=="c":
            u=""
        elif y in ["","ex"]:
            u=""
    elif x=="":
        if y=="a":
            u="c"
        elif y=="b":
            u="c"
        elif y=="c":
            u=""
        elif y in ["","ex"]:
            u=""
    return u
def uebergangstandortbedeutung(baumart, standort1column, standort2column):
    outue=""
    bedeutung1=str(naismatrix_gr_df.loc[naismatrix_gr_df[naismatrix_gr_df["grtreeid"] == baumart].index, str(standort1column)].values[0])
    bedeutung2=str(naismatrix_gr_df.loc[naismatrix_gr_df[naismatrix_gr_df["grtreeid"] == baumart].index, str(standort2column)].values[0])
    if bedeutung1 in ["a"] and bedeutung2 in ["a", "b"]:
        outue="a"
    elif bedeutung1 in ["a"] and bedeutung2 in ["c"]:
        outue="b"
    elif bedeutung1 in ["a"] and bedeutung2 not in ["a","b","c"]:
        outue="c"
    elif bedeutung1 in ["b"] and bedeutung2 in ["a","b","c"]:
        outue="b"
    elif bedeutung1 in ["b"] and bedeutung2 not in ["a","b","c"]:
        outue="c"
    elif bedeutung1 in ["c"] and bedeutung2 in ["a"]:
        outue="b"
    elif bedeutung1 in ["c"] and bedeutung2 in ["b","c"]:
        outue="c"
    elif bedeutung1 in ["c"] and bedeutung2 not in ["a","b","c"]:
        outue="ex"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 in ["a","b"]:
        outue="c"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 in ["c"]:
        outue="ex"
    elif bedeutung1 not in ["a","b","c"] and bedeutung2 not in ["a","b","c"]:
        outue="ex"
    return outue
#*************************************

#input data
codeworkspace="E:/Masterarbeit/ccwbe_kohler_MA/ccwbe_kohler_MA"
projectspace="E:/Masterarbeit/GIS"
#naismatrixdf=pd.read_excel(codeworkspace+"/"+"Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx", dtype="str", engine='openpyxl')
#projectionswegedf=pd.read_excel(codeworkspace+"/"+"L_Projektionswege_im_Klimawandel_18022020_export.xlsx", dtype="str", engine='openpyxl')
#gr_tree_abbreviations_df=pd.read_excel(codeworkspace+"/"+"Baumarten_LFI_export.xls", dtype=str)
#gr_tree_abbreviations_extract_df=gr_tree_abbreviations_df[gr_tree_abbreviations_df["Abkürzung_BK"].notnull()]
#climatescenario="rcp45"
climatescenario="rcp85"



#*******************************************
#projections pathways Projektionswege Data cleaning
#*******************************************
for index, row in projectionswegedf.iterrows():
    sto=row["Standortstyp_heute"]
    if "  " in sto:
        sto=sto.replace("  ", " ")
        projectionswegedf.loc[index, "Standortstyp_heute"]=sto
    if sto[-1]==" ":
        stonew=sto[:-1]
        projectionswegedf.loc[index, "Standortstyp_heute"]=stonew
for index, row in projectionswegedf.iterrows():
    stoz = row["Standortstyp_Zukunft"]
    if "  " in stoz:
        stoz=stoz.replace("  ", " ")
        projectionswegedf.loc[index, "Standortstyp_Zukunft"]=stoz
    if stoz[-1] == " ":
        stoznew = stoz[:-1]
        projectionswegedf.loc[index, "Standortstyp_Zukunft"] = stoznew
for index, row in projectionswegedf.iterrows():
    storeg = row["Standortsregionen"]
    if storeg == "R, J, M, 1, 2, 3 osa bis co":
        projectionswegedf.loc[index, "Standortsregionen"]="R, J, M, 1, 2, 3"
    if storeg == "R J, M,1, 2 Beginn co ":
        projectionswegedf.loc[index, "Standortsregionen"]="R, J, M, 1, 2, 3"
    if storeg == "R 5 ":
        projectionswegedf.loc[index, "Standortsregionen"]="R 5"
    if storeg == "R 4 ":
        projectionswegedf.loc[index, "Standortsregionen"]="R 4"
for index, row in projectionswegedf.iterrows():
    if row["Hoehenstufe_Zukunft"]=="hochmontan Reliktareal der Tanne":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"] = "hochmontan"
        projectionswegedf.loc[index, "Tannenareal_Zukunft"] = "Reliktareal"
    if row["Hoehenstufe_Zukunft"]=="hochmontan Hauptareal der Tanne":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"] = "hochmontan"
        projectionswegedf.loc[index, "Tannenareal_Zukunft"] = "Hauptareal"
    if row["Hoehenstufe_Zukunft"]=="hochmontan Nebenareal der Tanne":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"] = "hochmontan"
        projectionswegedf.loc[index, "Tannenareal_Zukunft"] = "Nebenareal"
#list forest types
standortstypen_projektionspfade_heute_list=projectionswegedf["Standortstyp_heute"].unique().tolist()
standortstypen_projektionspfade_zukunft_list=projectionswegedf["Standortstyp_Zukunft"].unique().tolist()
#correct some entries with "\n" in altitudinal vegetation belts
for index, row in projectionswegedf.iterrows():
    if "\n" in row["Hoehenstufe_heute"]:
        projectionswegedf.loc[index, "Hoehenstufe_heute"]=row["Hoehenstufe_heute"].replace("\n","")
#list altitudinal vegetation belts
hoehenstufen_projektionspfade_heute_list=projectionswegedf["Hoehenstufe_heute"].unique().tolist()
hoehenstufen_projektionspfade_zukunft_list=projectionswegedf["Hoehenstufe_Zukunft"].unique().tolist()
#correct names of future altiutudinal vegetation belts
for index, row in projectionswegedf.iterrows():
    if " Zukunft" in row["Hoehenstufe_Zukunft"]:
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"]=row["Hoehenstufe_Zukunft"].replace(" Zukunft","")
#change other wrong values
for index, row in projectionswegedf.iterrows():
    if row["Hoehenstufe_heute"]=="Obersubalpin":
        projectionswegedf.loc[index, "Hoehenstufe_heute"]="obersubalpin"
    if row["Hoehenstufe_heute"]=="hyperinsubrisch ":
        projectionswegedf.loc[index, "Hoehenstufe_heute"]="hyperinsubrisch"
for index, row in projectionswegedf.iterrows():
    if row["Hoehenstufe_Zukunft"]=="hyperinsubrisch Zukunft":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"]="hyperinsubrisch"
    if row["Hoehenstufe_Zukunft"]=="collin mit Buche Zukunft":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"]="collin mit Buche"
    if row["Hoehenstufe_Zukunft"]=="collin Zukunft":
        projectionswegedf.loc[index, "Hoehenstufe_Zukunft"]="collin"
for index, row in projectionswegedf.iterrows():
    if row["Hangneigung"]=="> 70%":
        projectionswegedf.loc[index, "Hangneigung"]=4
    if row["Hangneigung"]=="< 70%":
        projectionswegedf.loc[index, "Hangneigung"]=3
    if row["Hangneigung"]=="> als 60% ":
        projectionswegedf.loc[index, "Hangneigung"]=3
    if row["Hangneigung"]=="< als 60% ":
        projectionswegedf.loc[index, "Hangneigung"]=2
    if row["Hangneigung"]=="> 20%":
        projectionswegedf.loc[index, "Hangneigung"]=2
    if row["Hangneigung"]=="< 20%":
        projectionswegedf.loc[index, "Hangneigung"]=1
    else:
        projectionswegedf.loc[index, "Hangneigung"] = 0
#list altitudinal vegetation belts
hoehenstufen_projektionspfade_heute_list=projectionswegedf["Hoehenstufe_heute"].unique().tolist()
hoehenstufen_projektionspfade_zukunft_list=projectionswegedf["Hoehenstufe_Zukunft"].unique().tolist()
#check Standortsregionen
standortsregionen_projektionspfade_list=projectionswegedf["Standortsregionen"].unique().tolist()

#standortsregionen_combination_list=combinations_df["Standortre"].unique().tolist()
#exemption no mosaic/uebergang
kein_mosaic_uebergang_list=["3*/4*", "3L/4L", "3L/4L hyp", "3L/4L  med", "3L/4L med"]#, "50*(51)"]#, "67/67G","69/69G", "70/70G","71/71G"]

#pairs of changes in altitudinal vegetation belts
pairsofchangesinaltitudinalvegetationbelts_inprojektionspfade=[]
for index, row in projectionswegedf.iterrows():
    if [row["Hoehenstufe_heute"],row["Hoehenstufe_Zukunft"]] not in pairsofchangesinaltitudinalvegetationbelts_inprojektionspfade:
        pairsofchangesinaltitudinalvegetationbelts_inprojektionspfade.append([row["Hoehenstufe_heute"],row["Hoehenstufe_Zukunft"]])
#list of Standortregion
standortsregion_list_inprojektionspfade=projectionswegedf["Standortsregion"].unique().tolist()
#check if NAIS Standortstyp in NAISmatrix is not in Projektionspfade:
projektionspfadestandortstyp_heute_notin_NAISmatrix=[]
for sto in standortstypen_projektionspfade_heute_list:
    if sto not in nais_matrix_standorte_list:
        projektionspfadestandortstyp_heute_notin_NAISmatrix.append(sto)
projektionspfadestandortstyp_zukunft_notin_NAISmatrix=[]
for sto in standortstypen_projektionspfade_zukunft_list:
    if sto not in nais_matrix_standorte_list:
        projektionspfadestandortstyp_zukunft_notin_NAISmatrix.append(sto)
#correct wrong values of Standortstyp Zukunft
for index, row in projectionswegedf.iterrows():
    if row["Standortstyp_Zukunft"]=="41*collin":
        projectionswegedf.loc[index, "Standortstyp_Zukunft"]="41* collin"
    if row["Standortstyp_Zukunft"]=="43Scollin":
        projectionswegedf.loc[index, "Standortstyp_Zukunft"]="43S collin"
    if "  " in row["Standortstyp_Zukunft"]:
        print(row["Standortstyp_Zukunft"])


#******************************************************************************************************
#Baumartenempfehlungen
#******************************************************************************************************
grtreeid_list=naismatrixdf["Abkuerzung"].unique().tolist()
len(grtreeid_list)
grtreeid_list.sort()
gr_treetypes_LFI=grtreeid_list.copy()
for item in ["BUL", "FUL", "KA",""]:#"ES"
    if item in gr_treetypes_LFI:
        gr_treetypes_LFI.remove(item)
len(gr_treetypes_LFI)
joblib.dump(gr_treetypes_LFI, projectspace+"/Modellergebnisse/"+"gr_treetypes_LFI.sav")

naismatrix_gr_df = naismatrixdf[naismatrixdf["Abkuerzung"].isin(gr_treetypes_LFI)]
len(naismatrix_gr_df)
joblib.dump(naismatrix_gr_df, projectspace+"/Modellergebnisse/"+"naismatrix_gr_df.sav")
ausnahmenausserhalbbuchenareal=['21*', '23*', '25a', '25as', '25b', '25f', '25au', '26', '26h','29A','29C','33a', '33b', '33m', '34a', '34b', '35Q', '40Pt', '40PBlt','42C', '42V', '42t', '46', '46*', '47', '47D', '47M', '47*', '48','91']
buchenarealstoreg=['1','2a','5a','5b', 'J','M','Me']
ausnahmenausserhalbbuchenarealstoreg=['2b','3','4']
buchenausschlusshoehenstufenzukunft=['collin', 'hochmontan','subalpin', 'obersubalpin']
naisstandortstypeninmatrixlist=naismatrix_gr_df.columns.tolist()[8:-1]
ausnahmentannenreliktareal=['21*','23','24','24*','24*Fe','25a','25as','25b','25f','25au','26','26h','26w','27h','27*','33a','33b','33m','34a','34b','35Q','40P','40PBl','40Pt','40PBlt','42V','42t','47H']

#Baumartenbedeutungen
print("Berechne Baumartenbedeutungen ...")
#create a copy of the combinations data frame
combinations_df_bedeutung=combinations_df.copy()
layercolumnslist=combinations_df_bedeutung.columns.tolist()
for col in gr_treetypes_LFI:
    #print(col)
    combinations_df_bedeutung[col+"heu1"]=""
    combinations_df_bedeutung[col + "heu2"] = ""
for col in gr_treetypes_LFI:
    #print(col)
    combinations_df_bedeutung[col+"zuk1"]=""
    combinations_df_bedeutung[col + "zuk2"] = ""

#kein Uebergang
print("kein Uebergang ...")
for standorttyp in naisstandortstypeninmatrixlist:
    #print(standorttyp)
    for baumart in gr_treetypes_LFI:
        baumartbedeutung=naismatrix_gr_df.loc[naismatrix_gr_df[naismatrix_gr_df["Abkuerzung"]==baumart].index,standorttyp].values[0]
        if baumartbedeutung in ["a", "b","c"]:
            combinations_df_bedeutung.loc[combinations_df_bedeutung[combinations_df_bedeutung["ta"]==standorttyp].index, baumart + "heu1"] = baumartbedeutung
            combinations_df_bedeutung.loc[combinations_df_bedeutung[combinations_df_bedeutung["taue"] == standorttyp].index, baumart + "heu2"] = baumartbedeutung
            combinations_df_bedeutung.loc[combinations_df_bedeutung[combinations_df_bedeutung["naiszuk1"] == standorttyp].index, baumart + "zuk1"] = baumartbedeutung
            combinations_df_bedeutung.loc[combinations_df_bedeutung[combinations_df_bedeutung["naiszuk2"] == standorttyp].index, baumart + "zuk2"] = baumartbedeutung
#Uebergang
print("Uebergang ...")
for baumart in gr_treetypes_LFI:
    #print(baumart)
    combinations_df_bedeutung[baumart+"heuUE"]=""
for baumart in gr_treetypes_LFI:
    #print(baumart)
    combinations_df_bedeutung[baumart+"zukUE"]=""
for baumart in gr_treetypes_LFI:
    #print(baumart)
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart+"heu1"].isin(["a"])) & (combinations_df_bedeutung[baumart+"heu2"].isin(["a", "b"])))].index, baumart+"heuUE"] = "a"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["a", "b"])))].index, baumart + "zukUE"] = "a"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["c"])))].index, baumart + "heuUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["c"])))].index, baumart + "zukUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["", "ex"])))].index, baumart + "heuUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["a"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["", "ex"])))].index, baumart + "zukUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["b"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["a", "b", "c"])))].index, baumart + "heuUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["b"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["a", "b", "c"])))].index, baumart + "zukUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["b"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["", "ex"])))].index, baumart + "heuUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["b"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["", "ex"])))].index, baumart + "zukUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["c"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["a"])))].index, baumart + "heuUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["c"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["a"])))].index, baumart + "zukUE"] = "b"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["c"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["b", "c"])))].index, baumart + "heuUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["c"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["b", "c"])))].index, baumart + "zukUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "heu1"].isin(["", "ex"])) & (
        combinations_df_bedeutung[baumart + "heu2"].isin(["a", "b"])))].index, baumart + "heuUE"] = "c"
    combinations_df_bedeutung.loc[combinations_df_bedeutung[((combinations_df_bedeutung["ue"] == 1) & (combinations_df_bedeutung[baumart + "zuk1"].isin(["", "ex"])) & (
        combinations_df_bedeutung[baumart + "zuk2"].isin(["a", "b"])))].index, baumart + "zukUE"] = "c"

#correct beech vaules in excemption areas
baumart = "BU"
for index, row in combinations_df_bedeutung.iterrows():
    if row["storeg"] in ausnahmenausserhalbbuchenarealstoreg and row["ta"] in ausnahmenausserhalbbuchenareal:
        combinations_df_bedeutung.loc[index, baumart + "heu1"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["storeg"] in ausnahmenausserhalbbuchenarealstoreg and row["taue"] in ausnahmenausserhalbbuchenareal:
        combinations_df_bedeutung.loc[index, baumart + "heu2"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["storeg"] in ausnahmenausserhalbbuchenarealstoreg and row["hszukcor"] in ["collin", "hochmontan","subalpin", "obersubalpin"] and row["naiszuk1"] in ausnahmenausserhalbbuchenareal:
        combinations_df_bedeutung.loc[index, baumart + "zuk1"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "zukUE"] = ""
    if row["storeg"] in ausnahmenausserhalbbuchenarealstoreg and row["hszukcor"] in ["collin", "hochmontan","subalpin", "obersubalpin"] and row["naiszuk2"] in ausnahmenausserhalbbuchenareal:
        combinations_df_bedeutung.loc[index, baumart + "zuk2"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "zukUE"] = ""

#correct TA in excemption areas
baumart = 'TA'
for index, row in combinations_df_bedeutung.iterrows():
    if row["taheute"] == 3 and row["ta"] in ausnahmentannenreliktareal:
        combinations_df_bedeutung.loc[index, baumart + "heu1"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["subcode"] == 3 and row["ta"] in ausnahmentannenreliktareal:
        combinations_df_bedeutung.loc[index, baumart + "heu1"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["taheute"] == 3 and row["taue"] in ausnahmentannenreliktareal:
        combinations_df_bedeutung.loc[index, baumart + "heu2"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""
    if row["subcode"] == 3 and row["taue"] in ausnahmentannenreliktareal:
        combinations_df_bedeutung.loc[index, baumart + "heu2"] = ""
        if row["ue"]==1:
            combinations_df_bedeutung.loc[index, baumart + "heuUE"] = ""

#rename column TUL-->TU
#combinations_df_bedeutung.rename(columns = {'TULheute1':'TUheute1'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULheute2':'TUheute2'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULzukunft1':'TUzukunft1'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULzukunft2':'TUzukunft2'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULheuteUE':'TUheuteUE'}, inplace = True)
#combinations_df_bedeutung.rename(columns = {'TULzukunftUE':'TUzukunftUE'}, inplace = True)

#combinations_df_bedeutung.to_csv(projectspace+"/"+climatescenario.lower()+"_combinations_df_baumartenbedeutungen.csv")
joblib.dump(combinations_df_bedeutung, projectspace+"/Modellergebnisse/"+climatescenario.lower()+"_combinations_df_baumartenbedeutungen.sav")
#combinations_df_bedeutung.to_sql("grnaistahsstoregclip6190"+climatescenario+"_baumartenbedeutungen", engine)
#combinations_df_bedeutung.to_postgis(name="sg_"+climatescenario+'_baumartenbedeutungen', con=engine)
#combinations_df_bedeutung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenbedeutungen.shp")
#combinations_df_bedeutung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenbedeutungen.gpkg", layer="sg_"+climatescenario+"_baumartenbedeutungen", driver="GPKG")
#sqlstatement='SELECT * FROM public.grnaistahsstoregclip6190'+climatescenario+'_zukuenftigestandorte;'
#combinations_df=pd.read_sql_query(sqlstatement,con=engine)
#sqlstatement='SELECT * FROM public.grnaistahsstoregclip6190'+climatescenario+'_baumartenbedeutungen;'
#combinations_df_bedeutung=pd.read_sql_query(sqlstatement,con=engine)
#gr_treetypes_LFI=joblib.load(projectspace+"/"+"gr_treetypes_LFI.sav")
len(combinations_df_bedeutung)
len(combinations_df)

#iterate and calculate Baumartenempfehlungen
print("Berechne Baumartenempfehlungen ...")
#add columns to main layer
combinations_df_baumartenempfehlung=combinations_df_bedeutung.copy()
layercolumnslist=combinations_df_baumartenempfehlung.columns.tolist()
for col in gr_treetypes_LFI:
    combinations_df_baumartenempfehlung[col]=-999

for col in gr_treetypes_LFI:
    #print(col)
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0)&(combinations_df_baumartenempfehlung[col+"zuk1"].isin(["a","b"]))&(combinations_df_baumartenempfehlung[col+"heu1"].isin(["a","b","c"]))),col]=1
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0) & (combinations_df_baumartenempfehlung[col + "zuk1"].isin(["c"])) & (combinations_df_baumartenempfehlung[col + "heu1"].isin(["a", "b", "c"]))), col] = 2
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0) & (~combinations_df_baumartenempfehlung[col + "zuk1"].isin(["a", "b","c"])) & (combinations_df_baumartenempfehlung[col + "heu1"].isin(["a", "b", "c"]))), col] = 3
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0) & (combinations_df_baumartenempfehlung[col + "zuk1"].isin(["a", "b"])) & (~combinations_df_baumartenempfehlung[col + "heu1"].isin(["a", "b", "c"]))), col] = 4
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"]==0) & (combinations_df_baumartenempfehlung[col + "zuk1"].isin(["c"])) & (~combinations_df_baumartenempfehlung[col + "heu1"].isin(["a", "b", "c"]))), col] = 5
    #uebergang
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (combinations_df_baumartenempfehlung[col + "zukUE"].isin(["a", "b"])) & (combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 1
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (combinations_df_baumartenempfehlung[col + "zukUE"].isin(["c"])) & (combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 2
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (~combinations_df_baumartenempfehlung[col + "zukUE"].isin(["a", "b", "c"])) & (combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 3
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (combinations_df_baumartenempfehlung[col + "zukUE"].isin(["a", "b"])) & (~combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 4
    combinations_df_baumartenempfehlung.loc[((combinations_df_baumartenempfehlung["ue"] == 1) & (combinations_df_baumartenempfehlung[col + "zukUE"].isin(["c"])) & (~combinations_df_baumartenempfehlung[col + "heuUE"].isin(["a", "b", "c"]))), col] = 5

layercolumnslist=combinations_df_baumartenempfehlung.columns.tolist()

#joblib.dump(gr_treetypes_LFI, projectspace+"/"+"gr_treetypes_LFI.sav")
for col in gr_treetypes_LFI:
    #print(col)
    combinations_df_baumartenempfehlung.loc[combinations_df_baumartenempfehlung[col].isna()==True, col]=-999
    if (col + "heu1") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "heu1", axis=1, inplace=True)
    if (col + "heu2") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "heu2", axis=1, inplace=True)
    if (col + "zuk1") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "zuk1", axis=1, inplace=True)
    if (col + "zuk2") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "zuk2", axis=1, inplace=True)
    if (col + "heuUE") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "heuUE", axis=1, inplace=True)
    if (col + "zukUE") in layercolumnslist:
        combinations_df_baumartenempfehlung.drop(columns=col+ "zukUE", axis=1, inplace=True)

#save
#combinations_df_baumartenempfehlung.to_csv(projectspace+"/"+climatescenario.lower()+"_combinations_df_baumartenempfehlungen.csv")
joblib.dump(combinations_df_baumartenempfehlung, projectspace+"/Modellergebnisse/be_"+climatescenario.lower()+"_baumartenempfehlungen.sav")
#combinations_df_baumartenempfehlung.to_sql("li"+climatescenario+"_baumartenempfehlungen", engine)
#combinations_df_baumartenempfehlung.to_postgis(name="sg_"+climatescenario+'_baumartenempfehlungen', con=engine)


#******************************************************************************************************
#Sensitive Standorte
#******************************************************************************************************
print("Berechne Sensitive Standorte ...")
combinations_df_senstivestandorte=combinations_df_bedeutung.copy()
combinations_df_senstivestandorte["sensi3ba"]=-9999
combinations_df_senstivestandorte["sensi4ba"]=-9999
combinations_df_senstivestandorte["lenzukab"]=-9999
combinations_df_senstivestandorte["lenheua"]=-9999
combinations_df_senstivestandorte["lenheub"]=-9999
for index, row in combinations_df_senstivestandorte.iterrows():
    #if index%10000==0:
    #    print(index)
    #print(row["joinstr"])
    uebergang=row["ue"]
    baumartenzukunftablist=[]
    baumartenheutealist = []
    baumartenheuteblist = []
    sensitiverstandort3=row["sensi3ba"]
    sensitiverstandort4=row["sensi4ba"]
    if uebergang==0:
        for baumart in gr_treetypes_LFI:
            if row[baumart+"zuk1"] in ["a","b"]:
                baumartenzukunftablist.append(baumart)
        for baumartheutea in baumartenzukunftablist:
            if row[baumartheutea+"heu1"] =="a":
                baumartenheutealist.append(baumartheutea)
        for baumartheuteb in baumartenzukunftablist:
            if row[baumartheuteb + "heu1"] == "b":
                baumartenheuteblist.append(baumartheuteb)
    elif uebergang==1:
        for baumart in gr_treetypes_LFI:
            if row[baumart+"zukUE"] in ["a", "b"]:
                baumartenzukunftablist.append(baumart)
        for baumartheutea in baumartenzukunftablist:
            if row[baumartheutea+"heuUE"] =="a":
                baumartenheutealist.append(baumartheutea)
        for baumartheuteb in baumartenzukunftablist:
            if row[baumartheuteb + "heuUE"] == "b":
                baumartenheuteblist.append(baumartheuteb)
    if len(baumartenheutealist)>0:
        sensitiverstandort3 = 0
        sensitiverstandort4 = 0
    if len(baumartenheutealist)==0 and len(baumartenheuteblist)>=3:
        sensitiverstandort3 = 1
    elif len(baumartenheutealist)==0 and len(baumartenheuteblist)<3:
        sensitiverstandort3 = 2
    if len(baumartenheutealist)==0 and len(baumartenheuteblist)>=4:
        sensitiverstandort4 = 1
    elif len(baumartenheutealist)==0 and len(baumartenheuteblist)<4:
        sensitiverstandort4 = 2
    combinations_df_senstivestandorte.loc[index, "lenzukab"] = len(baumartenheutealist)
    combinations_df_senstivestandorte.loc[index, "lenheua"] = len(baumartenheutealist)
    combinations_df_senstivestandorte.loc[index, "lenheub"] = len(baumartenheuteblist)
    combinations_df_senstivestandorte.loc[index, "sensi3ba"]=sensitiverstandort3
    combinations_df_senstivestandorte.loc[index, "sensi4ba"] = sensitiverstandort4

#delete columns not needed anymore
columnstodelete=[]
for col in gr_treetypes_LFI:
    #print(col)
    columnstodelete.append(col)
    columnstodelete.append(col+"heu1")
    columnstodelete.append(col + "heu2")
    columnstodelete.append(col + "zuk1")
    columnstodelete.append(col + "zuk2")
    columnstodelete.append(col + "heuUE")
    columnstodelete.append(col + "zukUE")
for col in columnstodelete:
    if col in combinations_df_senstivestandorte.columns.tolist():
        combinations_df_senstivestandorte.drop(columns=col, axis=1, inplace=True)
#layercolumnslist=combinations_df_senstivestandorte.columns.tolist()

#write the output
print("write the output ...")
combinations_df_senstivestandorte.columns
joblib.dump(combinations_df_senstivestandorte, projectspace+"/sg_"+climatescenario.lower()+"_sensitivestandorte.sav")
combinations_df_senstivestandorte.to_file(projectspace+"/Modellergebnisse/"+"be_"+climatescenario+"_sensitivestandorte.shp")
#combinations_df_senstivestandorte.to_file(projectspace+"/"+"sg_"+climatescenario+"_sensitivestandorte.gpkg", layer="sg_"+climatescenario+"_sensitivestandorte", driver="GPKG")
combinations_df.columns
#combinations_df.to_file(projectspace+"/Modellergebnisse/"+"be_"+climatescenario+"_zukuenftigestandorte.shp")
#combinations_df.to_file(projectspace+"/"+"sg_"+climatescenario+"_zukuenftigestandorte.gpkg", layer="sg_"+climatescenario+"_zukuenftigestandorte", driver="GPKG")
#combinations_df=joblib.load(projectspace+"/Modellergebnisse/"+climatescenario.lower()+"_combinations_df_futureSTO.sav")
#combinations_df_bedeutung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenbedeutungen.shp")
#combinations_df_bedeutung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenbedeutungen.gpkg", layer="sg_"+climatescenario+"_baumartenbedeutungen", driver="GPKG")
combinations_df_baumartenempfehlung.columns
combinations_df_baumartenempfehlung.to_file(projectspace+"/Modellergebnisse/"+"be_"+climatescenario+"_baumartenempfehlungen.shp")
#combinations_df_baumartenempfehlung.to_file(projectspace+"/"+"sg_"+climatescenario+"_baumartenempfehlungen.gpkg", layer="sg_"+climatescenario+"_baumartenempfehlungen", driver="GPKG")



