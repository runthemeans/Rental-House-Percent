#!/usr/bin/env python
# coding: utf-8

# In[2]:


import arcpy
import os
workspace = input("Input your workspace GDB: ") #"D:\Documents\College\FRCC GIS\GIS_140\GeoGoonies\Final_Data\GIS_ParcelOwnerGDB\PythonTesting.gdb"
infeatureinput = input("Input your features to be changed: ") #"D:\Documents\College\FRCC GIS\GIS_140\GeoGoonies\Final_Data\GIS_ParcelOwnerGDB\PythonTesting.gdb\GIS_ParcelOwner_ZoningClip"
outfeatureinput = input("Input the address of the feature to be created: ") #"D:\Documents\College\FRCC GIS\GIS_140\GeoGoonies\Final_Data\GIS_ParcelOwnerGDB\PythonTesting.gdb\GIS_ParcelOwner_ZoningClipSimple" #
infeaturepath = os.path.join(workspace, infeatureinput)
outfeaturepath = os.path.join(workspace, outfeatureinput)

#Create a file address function here to accept more file names and concat them to the gdb file address


 #makes all of the user input match path format so all tools will run
#layer = arcpy.GetParameterAsText(0)
#pathvar = arcpy.Describe(workspace)
#path = pathvar.path
print("is this workspace correct?")
print(workspace)
checkvar = input("Y/N: ")
yes = "y"
y = yes.lower()
x = checkvar.lower()
if x == y:
    print("workspace verified")
elif x != y:
    workspace = input("reenter workspace address: ")
arcpy.env.workspace = r'workspace'
arcpy.env.overwriteOutput = True
print("Are these file names correct?")
print(infeaturepath)
print(outfeaturepath)
checkvarTwo = input("Y/N ")
z = checkvarTwo.lower()
if z == y:
    print("files verified")
elif z != y:
    infeatureinput = input("please reenter your feature to be changed: ")
    outfeatureinput = input("please reenter your feature to be created: ")
    infeaturepath = os.path.join(workspace, infeatureinput)
    outfeaturepath = os.path.join(workspace, outfeatureinput)



keep_fields = ["OBJECTID_1", "SHAPE", "PARCELNUM", "LOCADDRESS", "NAME", "MAILINGADDRESS", "SHAPE_Area"]
input("Continue to simplify fields?")
def copy_with_fields(in_fc, out_fc, keep_fields):

    #fieldtable = arcpy.FieldMap()
    fmap = arcpy.FieldMappings()
    #fieldtable.addInputField(in_fc, keep_fields)
    fmap.addTable(in_fc)  # takes orginal parcel layer and creates new one with smaller attribute table

    # get all fields
    fields = {f.name: f for f in arcpy.ListFields(in_fc)}
    print(fields)
    input("Press Enter if these fields are correct")

    # clean up field map
    for fname, fld in fields.items():
        if fld.type not in ('OID', 'Geometry') and 'shape' not in fname.lower():
            if fname not in keep_fields:
                fmap.removeFieldMap(fmap.findFieldMapIndex(fname))

    # copy features
    path, name = os.path.split(out_fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_fc, path, name, field_mapping=fmap)
    return out_fc
copy_with_fields(infeaturepath, outfeaturepath, keep_fields)

input("Continue?")

wherec = "MAILINGADDRESS LIKE '% STE %' OR MAILINGADDRESS LIKE '% UNIT %' OR MAILINGADDRESS LIKE '% APT %' \
           OR MAILINGADDRESS LIKE '% LOT %' OR MAILINGADDRESS LIKE '% OFFICE %'" #sql statement


terms = ["STE", "UNIT", "APT", "LOT", "OFFICE"]
print(terms)
input("These are the terms to remove. Continue?")
fieldName = ["MAILINGADDRESS"]
# updating mailing addrs format to match actual address format
with arcpy.da.UpdateCursor(in_table=outfeaturepath, field_names=fieldName, where_clause=wherec) as cursor:
    for row in cursor:
        if row[0].find(' STE ') > -1:
            row[0] = row[0].replace(' STE ', ' ')
        elif row[0].find(' UNIT ') > -1:
            row[0] = row[0].replace(' UNIT ', ' ')
        elif row[0].find(' APT ') > -1:
            row[0] = row[0].replace(' APT ', ' ')
        elif row[0].find(' LOT ') > -1:
            row[0] = row[0].replace(' LOT ', ' ')
        elif row[0].find(' OFFICE ') > -1:
            row[0] = row[0].replace(' OFFICE ', ' ')
        cursor.updateRow(row)
result = "ownLivYN"
arcpy.management.AddField(outfeaturepath, result, "SHORT")
# compare actual address and mailing address
counter = 0

fieldNameCompare = ["LOCADDRESS", "MAILINGADDRESS"]
with arcpy.da.SearchCursor(in_table=outfeaturepath, field_names=fieldNameCompare) as cursor:
    for row in cursor:
        if row[0] == row[1]:
            counter = counter + 1
        elif row[0] != row[1]:
            counter = counter + 0
total = arcpy.GetCount_management(outfeaturepath)
totalfloat = float(total[0])

#assigns a 1 or zero based on the criteria
arcpy.management.CalculateField(in_table=outfeaturepath, field="ownLivYN", expression="1 if !LOCADDRESS! == !MAILINGADDRESS! else 0",\
                                expression_type="PYTHON3", code_block="", field_type="SHORT", enforce_domains="NO_ENFORCE_DOMAINS")
# results statements

totalrhomes = int(total[0]) - int(counter)
percent = (float(totalrhomes)/ totalfloat)*100

print("Rentals available in Larimer County " + str(totalrhomes))
print("The total number of homes in Larimer County is: " + str(totalfloat))
print("The total number of homes owned by people who live in those homes is: " + str(counter))
print("the percentage of homes owned by people not living in those homes is: " + str(percent))

resultfile = open("D:\Documents\College\FRCC GIS\GIS_140\GeoGoonies\Final_Data\ResultsHousing.txt", "w+")

print("These results are saved at: " + str(resultfile))

resultfile.write("Total rentals available in Larimer County: " + str(totalrhomes) + "\n" +"The total number of homes in Larimer County is: " + str(totalfloat) + "\n"\
           "The total number of homes owned by people who live in those homes is: " + str(counter) + "\n" + "the percentage of homes owned by people not living in those homes is: " \
           + str(percent))
resultfile.close()

# In[ ]:




