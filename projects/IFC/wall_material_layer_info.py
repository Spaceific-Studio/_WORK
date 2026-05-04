import ifcopenshell
from ifcopenshell.util import element as ifcopenshell_element
import re

ifc_file = ifcopenshell.open(r"C:\Users\GercakD\DC\ACCDocs\PVS\X_Pracovní\Project Files\TEST_VYKAZOVANI_SKLADEB\STENA_VYKAZ-Custom-Material_volume.ifc")
ifc_walls = ifc_file.by_type('IFCWALL')

def parse_material_descriptions(descriptions_text):
    """Parse the KOMENTARE_MULTILINE text to extract individual material descriptions"""
    descriptions_dict = {}
    
    if not descriptions_text:
        return descriptions_dict
    
    # Split by pattern like "01 - ", "02 - ", etc.
    entries = re.split(r'\d{2}\s*-\s*', descriptions_text)
    
    for i, entry in enumerate(entries[1:], 1):  # Skip first empty split
        # Split entry by semicolon to get material name and description
        parts = entry.split(';', 1)
        if len(parts) >= 1:
            material_info = parts[0].strip()
            material_desc = parts[1].strip() if len(parts) > 1 else None
            
            # Extract material name (before the dash and mm)
            material_match = re.match(r'([^-]+)\s*-\s*(\d+\s*mm)', material_info)
            if material_match:
                material_name = material_match.group(1).strip()
                descriptions_dict[material_name] = material_desc
    
    return descriptions_dict

def get_wall_material_descriptions_from_type(ifc_element):
    """Extract material descriptions from wall type's property sets (KOMENTARE_MULTILINE)"""
    descriptions_text = None
    
    try:
        # Get the wall type
        if hasattr(ifc_element, 'IsTypedBy') and ifc_element.IsTypedBy:
            for rel in ifc_element.IsTypedBy:
                element_type = rel.RelatingType
                if hasattr(element_type, 'HasPropertySets') and element_type.HasPropertySets:
                    for prop_set in element_type.HasPropertySets:
                        if hasattr(prop_set, 'HasProperties'):
                            for prop in prop_set.HasProperties:
                                prop_name = prop.Name if hasattr(prop, 'Name') else ""
                                
                                if 'KOMENTARE' in prop_name or 'COMMENT' in prop_name.upper():
                                    prop_value = None
                                    if hasattr(prop, 'NominalValue'):
                                        prop_value = prop.NominalValue.wrappedValue if hasattr(prop.NominalValue, 'wrappedValue') else prop.NominalValue
                                    descriptions_text = prop_value
    except Exception as e:
        pass
    
    return descriptions_text

def get_ifc_materials_and_thickness(ifc_element, material_descriptions=None):
    material_thickness_list = []
    ifc_material = ifcopenshell_element.get_material(ifc_element)
    if ifc_material:
        
        if ifc_material.is_a('IfcMaterial'):
            # If the material is an IfcMaterial entity, append its name, thickness, and description
            material_name = ifc_material.Name if hasattr(ifc_material, 'Name') else None
            material_thickness = ifc_material.Thickness if hasattr(ifc_material, 'Thickness') else None
            material_description = material_descriptions.get(material_name) if material_descriptions else None
            material_thickness_list.append((material_name, material_thickness, material_description))
        elif ifc_material.is_a('IfcMaterialLayerSet'):
            # If the material is a layer set, loop over the layers and append their names, thicknesses, and descriptions
            for layer in ifc_material.MaterialLayers:
                material_name = layer.Material.Name if hasattr(layer.Material, 'Name') else None
                material_thickness = layer.LayerThickness if hasattr(layer, 'LayerThickness') else None
                material_description = material_descriptions.get(material_name) if material_descriptions else None
                material_thickness_list.append((material_name, material_thickness, material_description))
        else:
            # If the material is not an IfcMaterial or a layer set, just append its type and None values
            material_thickness_list.append((type(ifc_material).__name__, None, None))
    else:
        # If no material is found, append None for all
        material_thickness_list.append((None, None, None))
    return material_thickness_list

def get_element_area_and_volume(ifc_element):
    """Get area and volume of an IFC element by calculating from geometry"""
    area = None
    volume = None
    
    try:
        # Try using ifcopenshell.util.element functions first
        area = ifcopenshell_element.get_area(ifc_element)
        volume = ifcopenshell_element.get_volume(ifc_element)
        if area is not None or volume is not None:
            return area, volume
    except:
        pass
    
    # Alternative approach: Extract from representation geometry
    try:
        if hasattr(ifc_element, 'Representation') and ifc_element.Representation:
            rep = ifc_element.Representation
            
            for rep_item in rep.Representations:
                # Get representation type and items
                rep_type = rep_item.RepresentationType
                
                if hasattr(rep_item, 'Items'):
                    items = rep_item.Items
                    
                    # Try to extract dimensions from geometric items
                    for item in items:
                        item_type = item.is_a()
                        
                        # Handle ExtrudedAreaSolid (common for walls)
                        if item_type == 'IfcExtrudedAreaSolid':
                            try:
                                # Get the profile (SweptArea) - this is the cross-section
                                profile = item.SweptArea
                                # Get the height (Depth) of extrusion
                                height = item.Depth
                                
                                # If profile is a rectangle, calculate area and volume
                                if profile.is_a() == 'IfcRectangleProfileDef':
                                    width = profile.XDim if hasattr(profile, 'XDim') else None
                                    depth = profile.YDim if hasattr(profile, 'YDim') else None
                                    if width and depth:
                                        area = width * depth  # Cross-sectional area
                                        volume = width * depth * height
                                        return area, volume
                            except:
                                pass
                        
                        # Handle other geometry types
                        elif item_type == 'IfcFacetedBrepWithVoids' or item_type == 'IfcFacetedBrep':
                            try:
                                # For complex geometries, try to get surface area from faces
                                if hasattr(item, 'Outer') and item.Outer:
                                    outer_shell = item.Outer
                                    if hasattr(outer_shell, 'CfsFaces'):
                                        # Count faces to estimate complexity
                                        num_faces = len(outer_shell.CfsFaces) if outer_shell.CfsFaces else 0
                            except:
                                pass
    except Exception as e:
        pass
    
    return area, volume

def get_revit_parameters(ifc_element):
    """Extract Revit-specific parameters: ALL_MODEL_TYPE_MARK and Assembly Code"""
    type_mark = None
    id_number = None
    assembly_code = None
    
    # First check element's Tag attribute which contains the element ID
    try:
        element_info = ifc_element.get_info()
        # Tag attribute contains the element ID number
        if 'Tag' in element_info and element_info['Tag']:
            id_number = element_info['Tag']
    except:
        pass
    
    try:
        # Check element instance properties
        if hasattr(ifc_element, 'HasPropertySets') and ifc_element.HasPropertySets:
            for prop_set in ifc_element.HasPropertySets:
                if hasattr(prop_set, 'HasProperties'):
                    for prop in prop_set.HasProperties:
                        prop_name = prop.Name if hasattr(prop, 'Name') else ""
                        prop_value = None
                        
                        if hasattr(prop, 'NominalValue'):
                            prop_value = prop.NominalValue.wrappedValue if hasattr(prop.NominalValue, 'wrappedValue') else prop.NominalValue
                        
                        # Look for ALL_MODEL_MARK
                        if 'ALL_MODEL_MARK' in prop_name:
                            id_number = prop_value
                        
                        # Look for Assembly Code
                        if 'ASSEMBLY' in prop_name:
                            assembly_code = prop_value
    except Exception as e:
        pass
    
    try:
        # Check element type properties
        if hasattr(ifc_element, 'IsTypedBy') and ifc_element.IsTypedBy:
            for rel in ifc_element.IsTypedBy:
                element_type = rel.RelatingType
                if hasattr(element_type, 'HasPropertySets') and element_type.HasPropertySets:
                    for prop_set in element_type.HasPropertySets:
                        if hasattr(prop_set, 'HasProperties'):
                            for prop in prop_set.HasProperties:
                                prop_name = prop.Name if hasattr(prop, 'Name') else ""
                                prop_value = None
                                
                                if hasattr(prop, 'NominalValue'):
                                    prop_value = prop.NominalValue.wrappedValue if hasattr(prop.NominalValue, 'wrappedValue') else prop.NominalValue
                                
                                # Look for Type Mark / ALL_MODEL_TYPE_MARK
                                if 'ALL_MODEL_TYPE_MARK' in prop_name or prop_name == 'Type Mark':
                                    type_mark = prop_value
                                
                                # Look for ALL_MODEL_MARK in type
                                if 'ALL_MODEL_MARK' in prop_name and id_number is None:
                                    id_number = prop_value
                                
                                # Look for Assembly Code
                                if 'ASSEMBLY' in prop_name or prop_name == 'Assembly Code':
                                    assembly_code = prop_value
    except Exception as e:
        pass
    
    return type_mark, id_number, assembly_code

walls_data = []
for wall in ifc_walls:
    # Get descriptions from wall type
    descriptions_text = get_wall_material_descriptions_from_type(wall)
    material_descriptions = parse_material_descriptions(descriptions_text)
    
    materials_and_thickness = get_ifc_materials_and_thickness(wall, material_descriptions)
    area, volume = get_element_area_and_volume(wall)
    type_mark, id_number, assembly_code = get_revit_parameters(wall)
    wall_tag = wall.get_info()['Name']
    
    print(f"Wall: {wall_tag}")
    print(f"  Type Mark: {type_mark}, ID Number: {id_number}, Assembly Code: {assembly_code}")
    print(f"  Area: {area}, Volume: {volume}")
    
    wall_data = {
        'name': wall_tag,
        'type_mark': type_mark,
        'id_number': id_number,
        'assembly_code': assembly_code,
        'materials': materials_and_thickness,
        'area': area,
        'volume': volume
    }
    walls_data.append(wall_data)

print("\n=== RESULTS ===")
import json
print(json.dumps(walls_data, indent=2, ensure_ascii=False))