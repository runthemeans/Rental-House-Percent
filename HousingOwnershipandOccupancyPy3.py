#!/usr/bin/env python
# coding: utf-8

# In[2]:


import arcpy
import os
workspace = input("Input your workspace GDB file path: ")
infeatureinput = input("Input your features to be changed: ")
outfeatureinput = input("Input the address of the feature to be created: ")
infeaturepath = os.path.join(workspace, infeatureinput)
outfeaturepath = os.path.join(workspace, outfeatureinput)

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
arcpy.env.workspace = workspace
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

#clipping county parcels
#clipfeature = input("Please input the zoning file to clip")
#clipfeaturepath = os.path.join(workspace, clipfeature)
#clippedfeature = arcpy.analysis.Clip(infeaturepath, clipfeaturepath, outfeaturepath)
selectionfile = "FinalSelectionOut"
selectionfilepath = os.path.join(workspace,selectionfile)
#seclect to clean up parcels
sqlstate = "ACCTTYPE = 'MH Park' OR ACCTTYPE = 'Mobile Home' OR ACCTTYPE = 'Multiple Unit' OR ACCTTYPE = 'Residential'"
select = arcpy.management.SelectLayerByAttribute(infeaturepath, "NEW_SELECTION", sqlstate)
#export to database
arcpy.CopyFeatures_management(select, selectionfile)
#arcpy.conversion.FeatureClassToGeodatabase(outfeaturepath, workspace)
censustracts = os.path.join(workspace, "CensusTractsCounty2020")
sjoinOut = os.path.join(workspace, "parcelsWithTracts")
arcpy.analysis.SpatialJoin(selectionfilepath, censustracts, sjoinOut)


keep_fields = ["OBJECTID_1", "SHAPE", "PARCELNUM", "LOCADDRESS", "NAME", "MAILINGADDRESS", "SHAPE_Area", "LOCCITY",\
               "GISID", "LOCZIPCODE", "GEOID", "INTPTLAT", "INTPTLON", "OBJECTID_2", "BLKGRPCE"]
input("Continue to simplify fields?")
def copy_with_fields(in_fc, out_fc, keep_fields):

    #fieldtable = arcpy.FieldMap()
    fmap = arcpy.FieldMappings()
    #fieldtable.addInputField(in_fc, keep_fields)
    fmap.addTable(in_fc)  # takes orginal parcel layer and creates new one with smaller attribute table

    # get all fields
    fields = {f.name: f for f in arcpy.ListFields(in_fc)}
    print(keep_fields)
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
copy_with_fields(sjoinOut, outfeaturepath, keep_fields)


input("Continue to analysis?")

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
#result = "OwnerOcc"
#arcpy.management.AddField(outfeaturepath, result, "SHORT")
# compare actual address and mailing address
counter = 0

fieldNameCompare = ["LOCADDRESS", "MAILINGADDRESS"]
with arcpy.da.SearchCursor(in_table=outfeaturepath, field_names=fieldNameCompare) as cursor:
    for row in cursor:
        if row[0] == row[1]:
            counter = counter + 0
        elif row[0] != row[1]:
            counter = counter + 1
total = arcpy.GetCount_management(outfeaturepath)
totalfloat = float(total[0])

#assigns a 1 or zero based on the criteria
arcpy.management.CalculateField(in_table=outfeaturepath, field="RentCount", expression="1 if !LOCADDRESS! == !MAILINGADDRESS! else 0",\
                                expression_type="PYTHON3", code_block="", field_type="SHORT", enforce_domains="NO_ENFORCE_DOMAINS")
def generate_field_map(inputtable, fields_to_preserve):
    '''Create a FieldMappings object to use in Spatial Join.  For our application, we only want to preserve a few fields
    for informational purposes.  We expect all these field values to be the same, so use the "First" rule so the output
    polygon will just keep the same value as the inputs.  All other fields in the input data will not be transferred to
    the output.
    Params:
    in_time_lapse_polys: Time lapse polygon feature class from which to retrieve the fields
    fields_to_preserve: A list of field names we want to keep for the output.
    '''
    field_mappings = arcpy.FieldMappings()
    for field in fields_to_preserve:
        fmap = arcpy.FieldMap()
        fmap.addInputField(inputtable, field)
        fmap.mergeRule = "Sum"
        field_mappings.addFieldMap(fmap)
    return field_mappings


censustractswithvalues = os.path.join(workspace, "CensustractsWithData")

onefield = ["RentCount", "Shape_Area"]

keep_fields = ["OBJECTID", "Shape", "Join_Count", "GEOID", "RentCount", "Shape_Area"]
fieldmap = generate_field_map(outfeaturepath, onefield)
arcpy.SpatialJoin_analysis(censustracts, outfeaturepath, censustractswithvalues, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmap)

finaltracts = os.path.join(workspace, "FinalCensusTracts")
copy_with_fields(censustractswithvalues, finaltracts, keep_fields)
arcpy.management.CalculateField(in_table=finaltracts, field="Percent", expression="(!RentCount! / !Join_Count!)*100",\
                                expression_type="PYTHON3", code_block="", field_type="SHORT", enforce_domains="NO_ENFORCE_DOMAINS")

# results statements

totalOwnerhomes = int(total[0]) - int(counter)
percent = (float(counter) / totalfloat) * 100

print("Rentals available in Larimer County " + str(counter))
print("The total number of homes in Larimer County is: " + str(totalfloat))
print("The total number of homes owned by people who live in those homes is: " + str(totalOwnerhomes))
print("the percentage of homes that are rentals: " + str(percent))

resultfile = open("D:\Documents\College\FRCC GIS\GIS_140\GeoGoonies\Final_Data\ResultsHousing.txt", "w+")

print("These results are saved at: " + str(resultfile))
print("Output files are saved in: " + str(workspace))
input("Enter to Finish")

resultfile.write("Total rentals available in Larimer County: " + str(counter) + "\n" +"The total number of homes in Larimer County is: " + str(totalfloat) + "\n"\
           "The total number of homes owned by people who live in those homes is: " + str(totalOwnerhomes) + "\n" + "the percentage of homes that are rentals: " \
           + str(percent))
resultfile.close()

# In[ ]:




