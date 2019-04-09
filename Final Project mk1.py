# Alex Scott 3/6/19

import arcpy
import os
arcpy.env.workspace = r"C:\Users\ascott2\Documents\MyProject2\MyProject2.gdb"
arcpy.env.overwriteOutput = True

# simplifying table columns 

def copy_with_fields(in_fc, out_fc, keep_fields):
    in_fc = r'C:\Users\ascott2\Documents\MyProject2\MyProject2.gdb\ParcelOwner_Clip_housez'
    out_fc = r'C:\Users\ascott2\Documents\MyProject2\MyProject2.gdb\ParcelOwner_CLip_housez_simple'
    keep_fields = ["OBJECTID_1", "SHAPE", "PARCELNUM", "LOCADDRESS", "NAME", "MAILINGADDRESS", "SHAPE_Area"]
    fmap = arcpy.FieldMappings()
    fmap.addTable(in_fc)

    # get all fields
    fields = {f.name: f for f in arcpy.ListFields(in_fc)}


    # clean up field map
    for fname, fld in fields.items():
        if fld.type not in ('OID', 'Geometry') and 'shape' not in fname.lower():
            if fname not in keep_fields:
                fmap.removeFieldMap(fmap.findFieldMapIndex(fname))

    # copy features
    path, name = os.path.split(out_fc)
    arcpy.FeatureClassToFeatureClass_conversion(in_fc, path, name, field_mapping=fmap)
    return out_fc


if __name__ == '__main__':
    fc = r'C:\Users\ascott2\Documents\MyProject2\MyProject2.gdb\ParcelOwner_Clip_housez'
    new = r'C:\Users\ascott2\Documents\MyProject2\MyProject2.gdb\ParcelOwner_CLip_housez_simple'
    fields = ["OBJECTID_1", "SHAPE", "PARCELNUM", "LOCADDRESS", "NAME", "MAILINGADDRESS", "SHAPE_Area"] #only these fields and other required fields will be included
    copy_with_fields(fc, new, fields) #not sure what this chunk does but I'm scared to remove it
wherec = "MAILINGADDRESS LIKE '% STE %' OR MAILINGADDRESS LIKE '% UNIT %' OR MAILINGADDRESS LIKE '% APT %' \
           OR MAILINGADDRESS LIKE '% LOT %' OR MAILINGADDRESS LIKE '% OFFICE %'" #sql statement

newfile = r"C:\Users\ascott2\Documents\MyProject2\MyProject2.gdb\ParcelOwner_CLip_housez_simple"
terms = ["STE", "UNIT", "APT", "LOT", "OFFICE"]
print(terms)
fieldName = ["MAILINGADDRESS"]
# updating mailing addrs format to match actual address format
with arcpy.da.UpdateCursor(in_table=newfile, field_names=fieldName, where_clause=wherec) as cursor:
    for row in cursor:
        print(str(row[0]))
        if row[0].find(' STE ') > -1:
            row[0] = row[0].replace(' STE ', ' ')
            print(row[0])
        elif row[0].find(' UNIT ') > -1:
            row[0] = row[0].replace(' UNIT ', ' ')
            print(row[0])
        elif row[0].find(' APT ') > -1:
            row[0] = row[0].replace(' APT ', ' ')
            print(row[0])
        elif row[0].find(' LOT ') > -1:
            row[0] = row[0].replace(' LOT ', ' ')
            print(row[0])
        elif row[0].find(' OFFICE ') > -1:
            row[0] = row[0].replace(' OFFICE ', ' ')
            print(row[0])
        cursor.updateRow(row)
# compare actual address and mailing address
counter = 1
fieldNameCompare = ["LOCADDRESS", "MAILINGADDRESS"]
with arcpy.da.SearchCursor(in_table=newfile, field_names=fieldNameCompare) as cursor:
    for row in cursor:
        if row[0] == row[1]:
            counter = counter + 1
            print(counter)
total = arcpy.GetCount_management(newfile)
# results statements
print(total)
percent = 100*(int(counter) / int(total[0]))
totalrhomes = int(total[0]) - int(counter)
print(totalrhomes)
print(str(percent))
print("the total number of homes in Fort Collins is " + str(total[0]))
print("The total number of homes owned by people who do not live there is" + str(counter))
print("the percentage of homes owned by people not living in those homes is: " + str(percent))
