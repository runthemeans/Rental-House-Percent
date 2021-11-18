#!/usr/bin/env python
# coding: utf-8

# In[2]:


import arcpy
import os
workspace = raw_input("Input your workspace GDB: ")
print("is this workspace correct?")
print(workspace)
checkvar = raw_input("Y/N: ")
yes = "Y"
if checkvar == yes:
    print("workspace verified")
elif checkvar != yes:
    workspace = raw_input("reenter workspace address: ")
arcpy.env.workspace = r'workspace'
arcpy.env.overwriteOutput = True

infeature = raw_input("Input your features to be changed: ")
outfeature = raw_input("Input the address of the feature to be created: ")
print("Are these files correct?")
print(infeature)
print(outfeature)
checkvarTwo = raw_input("Y/N ")
if checkvarTwo == yes:
    print("files verified")
elif checkvarTwo != yes:
    infeature = raw_input("please reenter your feature to be changed: ")
    outfeature = raw_input("please reenter your feature to be created: ")
keep_fields = ["OBJECTID_1", "SHAPE", "PARCELNUM", "LOCADDRESS", "NAME", "MAILINGADDRESS", "SHAPE_Area"]
def copy_with_fields(in_fc, out_fc, keep_fields):

    fmap = arcpy.FieldMappings()
    fmap.addTable(in_fc)  # takes orginal parcel layer and creates new one with smaller attribute table

    # get all fields
    fields = {f.name: f for f in arcpy.ListFields(in_fc)}
    print(fields)


    # clean up field map
    for fname, fld in fields.items():
        if fld.type not in ('OID', 'Geometry') and 'shape' not in fname.lower():
            if fname not in keep_fields:
                fmap.removeFieldMap(fmap.findFieldMapIndex(fname))

    # copy features
    path, name = os.path.split(out_fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_fc, path, name, field_mapping=fmap)
    return out_fc
copy_with_fields(infeature, outfeature, keep_fields)

wherec = "MAILINGADDRESS LIKE '% STE %' OR MAILINGADDRESS LIKE '% UNIT %' OR MAILINGADDRESS LIKE '% APT %' \
           OR MAILINGADDRESS LIKE '% LOT %' OR MAILINGADDRESS LIKE '% OFFICE %'" #sql statement


terms = ["STE", "UNIT", "APT", "LOT", "OFFICE"]
print(terms)
fieldName = ["MAILINGADDRESS"]
# updating mailing addrs format to match actual address format
with arcpy.da.UpdateCursor(in_table=outfeature, field_names=fieldName, where_clause=wherec) as cursor:
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
# compare actual address and mailing address
counter = 0
fieldNameCompare = ["LOCADDRESS", "MAILINGADDRESS"]
with arcpy.da.SearchCursor(in_table=outfeature, field_names=fieldNameCompare) as cursor:
    for row in cursor:
        if row[0] == row[1]:
            counter = counter + 1
        elif row[0] != row[1]:
            counter = counter + 0
total = arcpy.GetCount_management(outfeature)
totalfloat = float(total[0])

# results statements

totalrhomes = int(total[0]) - int(counter)
percent = (float(totalrhomes)/ totalfloat)*100

print("Rentals available " + str(totalrhomes))
print("the total number of homes in Fort Collins is: " + str(totalfloat))
print("The total number of homes owned by people who do live in those homes is: " + str(counter))
print("the percentage of homes owned by people not living in those homes is: " + str(percent))

# In[ ]:




