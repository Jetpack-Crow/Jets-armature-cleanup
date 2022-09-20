#Works on an armature you have active in object mode. I've been mostly using 
#game models imported as .fbx, but as near as I can tell, .dae and the rest work fine.
#Also, make sure all the bones you care about affecting are in the first armature layer

import bpy
from bpy import context

bl_info = {
    "name": "Armature Import Cleanup",
    "description": "Some tools for cleaning up models imported as .FBX or .DAE",
    "author": "Jetpack Crow",
    "version": (1, 00),
    "blender": (2, 93, 0),
    "location": "Object Mode > N Panel > Armature Cleanup",
    "category": "Object",
}

def string_minus_index(test_str, index):
    
    new_str = ""
  
    for i in range(len(test_str)):
        if i != index:
            new_str = new_str + test_str[i]
            
    #print("\tNew string is " + new_str)
    
    return new_str

def bone_to_layer(bone, layer): #puts bone in that layer
    bone.layers[layer] = True
    for i in range(0, 31):
        if i != layer:
            bone.layers[i] = False  #And removes it from all the other layers.
            # This is fiddly but it's because it won't let me set all layers
            # to false at once
             
def children_to_layer(rootbone, layer): #Relocates all the children of given bone
    i = 0
    print("sorting children of " + rootbone.name + " to layer " + str(layer))
    for bone in rootbone.children_recursive[:]:
        if bone.layers[0]:  #But only from layer 0. If they were already sorted based on
            bone_to_layer(bone, layer)   #other criteria, they'll stay where they were
            i = i + 1
    print("moved " + str(i) + " bones")
    return i
    
def getChildren(myObject):         
    return myObject.children 

def bone_usefulness(bone):
    
    obj = bpy.context.active_object
    activeArmature = obj.data
    
    meshes = getChildren(obj)
    #deforming = False
    for item in meshes:
        for g in item.vertex_groups[:]:
            if g.name == bone.name:
                print(bone.name + " deforms " + item.name)
                return True
    #if deforming:
     #   return True

    for child in bone.children:   #Recursive, lets a bone stay useful if children are
        if bone_usefulness(child):
            print(bone.name + " may have a use, because " + child.name + " does")
            return True
    return False

left_list = ["left", "Left", " L ", " l ", "-L-", "-l-"]
left_prefixes = ["L_", "l_", "L.", "l."]
right_list = ["right", "Right", " R ", " r ", "-R-", "-r-"]
right_prefixes = ["R_", "r_", "R.", "r."]

def matches_with_error(key, target):
    offset = obj.dimensions.z * 0.001
    
    upperbound = target + offset
    lowerbound = target - offset
    
    if (key <= upperbound) and (key >= lowerbound):
        #print(str(key) + " is within " + str(offset) + " of target " + str(target))
        return True
    else:
        #print(str(key) + " does not match " + str(target))
        return False
    
def round_to_nearest(key):
    base = obj.dimensions.z * 0.001
    
    nearest_multiple = base * round(key/base)
    #print(str(key) + " rounded to nearest " + str(base) + " = " + str(nearest_multiple))
    return nearest_multiple 

def add_to_bone_dictionary(x_val, bone):
    print(bone.name + " to table")
    if x_val in bones_table.keys():
        #print("val already in bones table")
        
        if isinstance(bones_table[x_val], list):
            #print("already a list")
            bones_table[x_val].append(bone)
        else:
            #print("making it a list")
            bones_list = [ bones_table[x_val], bone ]
            bones_table[x_val] = bones_list
    else:
        #print("val not in bones table")
        bones_table.update({x_val: [bone]})
    

#this also needs to split at " L " or " R "
def symmetrySplit():
    
    print("Symmetrizing\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    unmovedlist = []
    movedlist = []
    for bone in activeArmature.bones[:]:
        
        match = False
        
        newname = bone.name
        
        for key in left_list:
            if key in bone.name:
                #print("left true")
                bonesplit = bone.name.split(key)
                newname = str(bonesplit[0] + bonesplit[1] + ".L")
                newname = ' '.join(newname.split())
                match = True
                
        for key in right_list:
            if key in bone.name:
                #print("right true")
                bonesplit = bone.name.split(key)
                newname = str(bonesplit[0] + bonesplit[1] + ".R")
                newname = ' '.join(newname.split())
                match = True
                
        if not match:
            for key in left_prefixes:
                if bone.name.startswith(key):
                    #print("left true")
                    bonesplit = bone.name.split(key)
                    newname = str(bonesplit[0] + bonesplit[1] + ".L")
                    newname = ' '.join(newname.split())
                    match = True
            for key in right_prefixes:
                if bone.name.startswith(key):
                    #print("left true")
                    bonesplit = bone.name.split(key)
                    newname = str(bonesplit[0] + bonesplit[1] + ".R")
                    newname = ' '.join(newname.split())
                    match = True
    
        if match:
            print("new name = " + newname)
            bone.name = newname
            movedlist.append(bone)
        else:
            unmovedlist.append(bone)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nSymmetry [stage 1] Done\n")
    
    print("total of " + str(len(unmovedlist)) + " bones unaffected")


    #print("Potential 'center' bones:")
    
    for outer_loop in unmovedlist:
        
        outer_name = outer_loop.name
        
        if outer_name[-2] == '.':
            # If it's already been set, just skip this one and move to the next bone
            continue
        
        for inner_loop in unmovedlist:
            
            inner_name = inner_loop.name
            
            if inner_name[-2] == '.':
                # If it's already been set, just skip this one and move to the next bone
                continue
            
            match = True
            
            direction_differ = False
            directionindex = 0
            
            
            if len(outer_name) != len(inner_name):
                # Name length mismatch, can't be a match this way.
                continue
            if outer_loop == inner_loop:
                #these are the same bone, skip it
                continue # to the next bone in the list
            
            for element in range(0, len(outer_name)):
                if outer_name[element] == inner_name[element]:
                    # The strings match at this index.
                    continue # to the next character
                else: # If they don't match, BUT the 
                    
                    if (    (outer_name[element].lower() == 'l' or outer_name[element].lower() == 'r')
                            and (inner_name[element].lower() == 'l' or inner_name[element].lower() == 'r')):
                        if direction_differ:
                            # if there has already been one established L or R, though,
                            # then they don't match after all.
                            match = False
                            break # out of the letters list and conclude the word
                        else:
                            directionindex = element
                            direction_differ = True
                    else:
                        match = False
                        break # out of the letters list and conclude the word
                    
            # And now we're out of the for loop. Traversed the entire word, let's see what we're
            # working with.
            if match and direction_differ:
                # This means that the word overall is a match, there's just a single character that
                # differs on R/L
                
                new_name = string_minus_index(outer_name, directionindex)
                
                movedlist.append(outer_name)
                movedlist.append(inner_name)
                
                if outer_name[directionindex].lower() == 'l':
                    print('\t', outer_name, "is left")
                    outer_loop.name = new_name + '.L'
                    inner_loop.name = new_name + '.R'
                else:
                    print('\t', outer_name, "is right")
                    outer_loop.name = new_name + '.R'
                    inner_loop.name = new_name + '.L'
                    
    
    return len(movedlist)

def locationmatch():
    global bones_table
    bones_table = {}
    
    bones_changed = 0
    
    for target in activeArmature.bones:

        if (      (target.name[-1].lower() == 'l') or (target.name[-1].lower() == 'r')
                    and (target.name[-2] == '.')) :
            print(target.name + " already ends in ." + target.name[-1])
        elif (  matches_with_error(target.head_local[0], 0.0)
                and matches_with_error(target.tail_local[0], 0.0)):
            print(target.name + " is at center")
        else:
            x_value = abs(target.head_local[0])
            #print(target.name + " abs x is " + str(x_value))
            x_rounded = round_to_nearest(x_value)
            #print("rounded to " + str(x_rounded))
            
            add_to_bone_dictionary(x_rounded, target)
            
            
    
    for key, value in bones_table.items():
        print('at x', key, ':')
        if isinstance(value, list):
            for printbone in value:
                print('\t', printbone.name)
                
            #for matchbone in value:
                # Check the Y values of each bone to see if they match, and
                # then potentially pair them off
            if len(value) == 2:
                firstbone = value[0]
                secondbone = value[1]
                
                if (matches_with_error(firstbone.head_local[2], secondbone.head_local[2])
                    and matches_with_error(firstbone.head_local[1], secondbone.head_local[1])):
                    print("\t\tthese two share Y and Z, are a likely match")
                
                    
                    #newbasename = firstbone.name + value[1].name
                    newbasename = ""
                    
                    differFirst = ""
                    differSecond = ""
                    
                    if len(firstbone.name) == len(secondbone.name):
                        for element in range(0, len(firstbone.name)):
                            if firstbone.name[element] == secondbone.name[element]:
                                newbasename = newbasename + (firstbone.name[element])
                            else:
                                differFirst = differFirst + firstbone.name[element]
                                differSecond = differSecond + secondbone.name[element]
                        newbasename = newbasename + '_' + differFirst + '_' + differSecond
                            
                        
                    
                    print("\t\tPairing them off, new names : " + newbasename)
                    bones_changed = bones_changed + 2
                    
                    if value[0].tail_local[0] > value[1].tail_local[0]:
                        value[0].name = newbasename + ".L"
                        value[1].name = newbasename + ".R"
                    else:
                        value[0].name = newbasename + ".R"
                        value[1].name = newbasename + ".L"
            
            
        else:
            print('\t', value.name)
            print('\t Single bone at this X')
    
    print()
    
    return bones_changed

def layerSort(key, layer):
    print("Sorting key " + key + " to layer " + str(layer)+ "\n~~~~~~~~~~~~~~~~~")
    i = 0
    for bone in activeArmature.bones[:]:
        if key in bone.name.lower():
            bone_to_layer(bone, layer)
            i = i+1
    print("\nLayer sort done")
    print(str(i) + " bones to layer " + str(layer) + "\n")
    if i > 0:
        obj.sort_layer = obj.sort_layer - 1
    return i 

def rootSet():
    
    root = activeArmature.bones[0]   #Takes root bone of armature
    print("root bone = " + root.name)

    root_matrix_final =  obj.matrix_world @ root.matrix_local #Calculates global location
    print(root_matrix_final)  

    context.scene.cursor.matrix = root_matrix_final
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')   #Puts the 3d cursor at root bone
    print("set origin to root bone")                  #And puts origin to 3d cursor

def check_children(source, key):
    for bone in source.children_recursive[:]:
        if key in bone.name.lower():
            return True
    print("key " + key + " not found in children of " + source.name)
    return False

def headbone():   #Takes the first place in the neck/head chain where it starts to split apart
                # theoretically into face bits. If your model doesn't have complicated face
                # bits, this may do nothing.
    keyslist = ["head", "neck", "face"]                
                
    for bone in activeArmature.bones[:]:
        for word in keyslist:
            if word in bone.name.lower():
                print(bone.name + " has " + str(len(bone.children)) + " children")
                if len(bone.children) > 2:   
                    if check_children(bone, "arm"):
                        print(bone.name + " is parent of arm")
                        #One model I checked had the shoulders connected to the 
                        # neck for some reason, so this is just here to head that
                        # off.
                    #elif check_children(bone, "neck"):
                    #    print(bone.name + " is parent of neck")
                    else:
                        headroot = bone
                        print("headroot is " + headroot.name)
                        print()
                        return headroot
                break #Don't bother to keep checking this bone if it matches one 
                     # of the keys. move on
        
    print("No head bone located.")
    return None

def armbone(direction):  #Takes the first place in the hand chain where it starts to split
                         #apart, theoretically into fingers
    keyslist = ["hand", "wrist"]                     
                         
    for bone in activeArmature.bones[:]:
        for word in keyslist:
            if word in bone.name.lower():
                if bone.name.endswith(direction):
                    print(bone.name + " has " + str(len(bone.children)) + " children")
                    
                    if len(bone.children) > 2:
                        handroot = bone
                        print("handroot is " + handroot.name)
                        print()
                        return handroot
                break #Don't bother to keep checking this bone if it matches one 
                     # of the keys. move on
    print("No " + direction + " hand bone located.")
    return None

def remove_bone(posebone):  # Posebone name is passed as a string, because it doesn't
                            # work on the same bone indexes anymore when you're
                            # actively removing bones
    #print("removing bone " + posebone)
    #print("compare to:", end=' ')
    
    original_mode = bpy.context.mode
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    #print("set edit mode")
    
    #activeArmature.edit_bones.remove(activeArmature.edit_bones[posebone])
    
    try:
        activeArmature.edit_bones.remove(activeArmature.edit_bones[posebone])
        print(posebone, end=', ')
    except:
        print("\n!!! Couldn't remove " + posebone)
            
    bpy.ops.object.mode_set(mode=original_mode)
    #print("set object mode")

def remove_useless():
    hitlist = []
    print("remove_useless start")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    for bone in activeArmature.bones[:]:
        #print(bone.name)
        if not bone_usefulness(bone):
            print("-> " + bone.name + " is useless")
            #remove_bone(bone)
            hitlist.append(bone.name)
    
    print("total list to remove:")
    for i in hitlist:
        print(i, end=', ')
    print()
    print("removing: ")
    for i in hitlist:
        remove_bone(i)

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    
    return len(hitlist)

#scene = context.scene
#obj = bpy.context.active_object
#activeArmature = obj.data

"""try:

    # Takes bones that include this key in names, moves them to given layer.
    # If a model's got hair or a jacket or a skirt or something you'd like separated,
    # just add them in here
    layerSort("unused", 15)
    layerSort("adj", 13)
    layerSort("roll", 12)
    layerSort("end", 11)
    layerSort("twist", 14)
    
    layerSort("jacket", 31)
    layerSort("skirt", 30)
    layerSort("hair", 29)
    
    righthand = armbone(".R")
    if righthand != None:
        print("right hand bone is: " + righthand.name)
        children_to_layer(righthand, 16)

    lefthand = armbone(".L")
    if lefthand != None:
        print("left hand bone is: " + lefthand.name)
        children_to_layer(lefthand, 17)


except(AttributeError):
    print("Failed: " + obj.name + " may not be an armature")"""
    
class symmetry_by_name(bpy.types.Operator):
    """Try to pair up bones based on names."""
    
    bl_idname = "object.armature_cleanup_symmetry_names"
    bl_label = "Symmetry by Names"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        
        obj = bpy.context.active_object
        activeArmature = obj.data
        
        #if activeArmature.
        edit_number = symmetrySplit()
        
        message = "Rig symmetrized, " + str(edit_number) + " bones changed"
        self.report({'INFO'}, message)
        
        return {'FINISHED'}    
    
class symmetry_by_position(bpy.types.Operator):
    """Try to pair up bones based on positions."""
    
    bl_idname = "object.armature_cleanup_symmetry_position"
    bl_label = "Symmetry by Location"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        
        obj = bpy.context.active_object
        activeArmature = obj.data
        
        #if activeArmature.
        edit_number = locationmatch()
        
        message = "Rig symmetrized, " + str(edit_number) + " bones changed"
        self.report({'INFO'}, message)
        
        return {'FINISHED'}        
    
class visibility_to_front(bpy.types.Operator):
    """Put the armature's display settings to front."""
    
    bl_idname = "object.armature_vis_to_front"
    bl_label = "Visibility to front"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        obj = bpy.context.active_object
        activeArmature = obj.data
        
        print("setting armature to show in front")
        message = "Setting armature to show in front"
        obj.show_in_front = True
        
        self.report({'INFO'}, message)
        
        return {'FINISHED'}    

class prune_useless_bones(bpy.types.Operator):
    """Remove any bones that don't affect the meshes at all."""
    bl_idname = "object.prune_bones"
    bl_label = "Prune bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('prune operator')
        
        obj = bpy.context.active_object
        activeArmature = obj.data
        
        message = "Removed " + str(remove_useless()) + " bones"
        remove_useless()
        
        self.report({'INFO'}, message)
        
        return {'FINISHED'} 
    
    
class origin_to_root(bpy.types.Operator):
    """Sets the object's origin to the armature's root bone."""
    
    bl_idname = "object.origin_to_root"
    bl_label = "Origin to root"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        obj = bpy.context.active_object
        activeArmature = obj.data
        
        rootSet()
        
        message = "Set object origin to armature root bone."
        self.report({'INFO'}, message)
        
        return {'FINISHED'} 

class key_sort(bpy.types.Operator):
    """Sorts bones with a given key in the name into a given layer"""
    bl_idname = "object.armature_key_sort"
    bl_label = "Key Sort"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        string_key = obj.sort_key
        
        destination_layer = obj.sort_layer
        
        i = layerSort(string_key, destination_layer)
        
        message = "Moved " + str(i) + " bones to layer " + str(destination_layer)
        self.report({'INFO'}, message)
        
        return {'FINISHED'} 
    
    
class head_sort(bpy.types.Operator):
    """Autodetect the model's head and move face bones out of the way."""
    
    bl_idname = "object.armature_head_sort"
    bl_label = "Detect Head"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        i = 0
        
        headroot = headbone()
        if headroot != None:
            print("head bone is: " + headroot.name)
            i = children_to_layer(headroot, 1)
            
        message = "Moved " + str(i) + " bones to layer 1"
        
        self.report({'INFO'}, message)
            
        return {'FINISHED'} 
    
class hands_sort(bpy.types.Operator):
    """Autodetect the model's hands and move finger bones out of the way."""
    
    bl_idname = "object.armature_hands_sort"
    bl_label = "Detect Hands"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        i = 0
        
        righthand = armbone(".R")
        if righthand != None:
            print("right hand bone is: " + righthand.name)
            i = i + children_to_layer(righthand, 16)

        lefthand = armbone(".L")
        if lefthand != None:
            print("left hand bone is: " + lefthand.name)
            i = i + children_to_layer(lefthand, 17)
            
        message = "Moved " + str(i) + " bones to layers 16 and 17"
        
        self.report({'INFO'}, message)
        
        return {'FINISHED'}
    
class blends_to_opaque(bpy.types.Operator):
    """Sets the blend modes of all materials on a mesh (or all an armature's children" to opaque."""
    
    bl_idname = "object.blends_to_opaque"
    bl_label = "Materials Opaque"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        print("all mats to opaque")
        
        return {'FINISHED'}

def survey(obj):
    maxWeight = {}
    for i in obj.vertex_groups:
        maxWeight[i.index] = 0

    for v in obj.data.vertices:
        for g in v.groups:
            gn = g.group
            w = obj.vertex_groups[g.group].weight(v.index)
            if (maxWeight.get(gn) is None or w>maxWeight[gn]):
                maxWeight[gn] = w
    # print("weight group"%gn)
    return maxWeight
    
class remove_useless_groups(bpy.types.Operator):
    """Removes all the empty vertex groups on a selected mesh."""
    bl_idname = "object.remove_useless_groups"
    bl_label = "Prune vertex groups"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        print("remove useless")
        
        maxWeight = survey(obj)
        
        ka = []
        ka.extend(maxWeight.keys())
        ka.sort(key=lambda gn: -gn)
        print (ka)
        
        numberPruned = 0
        
        for gn in ka:
            if maxWeight[gn]<=0:
                numberPruned = numberPruned + 1
                print ("delete %d"%gn)
                obj.vertex_groups.remove(obj.vertex_groups[gn])
        
        message = str(numberPruned) + " empty vertex groups removed"
        self.report({'INFO'}, message)
        
        return {'FINISHED'}

class print_center_bones(bpy.types.Operator):
    """Shows all the bones on a mesh that don't have a symmetric 'pair.' Hopefully just the centers."""
    
    bl_idname = "object.show_centers"
    bl_label = "Print Unpaired Bones"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print("Likely center bones:")
        centernumber = 0
        
        for bone in activeArmature.bones:
            if bone.name[-2] != '.':
                print(bone.name)
                centernumber = centernumber + 1
        
        #print("bones")
        
        message = str(centernumber) + " bones"
        
        self.report({'INFO'}, message)
        
        return {'FINISHED'}
    
def set_shape_keys(mesh, boolOption):
    
    mute = boolOption
    try:
        object_keys = mesh.shape_keys
        
        for key in object_keys.key_blocks:
            key.mute = mute
        return True
    except:
        #print("Object does not have shape keys established.")
        return False
    
class mute_shape_keys(bpy.types.Operator):
    """Mutes all the shape keys on the active mesh"""
    
    bl_idname = "object.mute_shape_keys"
    bl_label = "Mute Shapes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        mesh = obj.data
        
        if not (set_shape_keys(mesh, True)):
            message = "Object does not have shape keys established."
            self.report({'INFO'}, message)
        
        return {'FINISHED'}
    
class unmute_shape_keys(bpy.types.Operator):
    """Unmutes all the shape keys on the active mesh"""
    
    bl_idname = "object.unmute_shape_keys"
    bl_label = "Unmute Shapes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        mesh = obj.data
        
        if not (set_shape_keys(mesh, False)):
            message = "Object does not have shape keys established."
            self.report({'INFO'}, message)
        
        return {'FINISHED'}
    
            
class github_link(bpy.types.Operator):
    
    """Check this out for updates or to report any issues you find"""
    bl_idname = "object.autogrip_discussion_link"
    bl_label = "Github Link"
    
    def execute(self, context):
        
        import webbrowser
        import imp
        webbrowser.open("https://github.com/Jetpack-Crow/Jets-armature-cleanup")  
        
        return {'FINISHED'}    
    
class ArmatureCleanupPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Armature Cleanup"
    bl_idname = "SCENE_PT_cleanup"
    
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Armature Cleanup"
    #bl_context = "objectmode"

    def draw(self, context):

        layout = self.layout

        scene = context.scene
        
        global obj
        obj = bpy.context.active_object
        global activeArmature
        activeArmature = obj.data
        
        
        row = layout.row()
        row.operator("object.transform_apply")
        
        if type(activeArmature) is bpy.types.Armature:
            
            row = layout.row()
            row.label(text="Active armature: {}".format(activeArmature.name))
            
            row = layout.row()
            row.operator(visibility_to_front.bl_idname)
            
            row = layout.row()
            row.operator(prune_useless_bones.bl_idname)
            row.operator(origin_to_root.bl_idname)
            
            row = layout.row()
            
            row.operator(head_sort.bl_idname)
            row.operator(hands_sort.bl_idname)
            
            
            row = layout.row()
            row.prop(obj, "sort_key")
            
            row = layout.row()
            row.prop(obj, "sort_layer")
            
            row = layout.row()
            row.operator(key_sort.bl_idname)
            
            row = layout.row()
            row.operator(symmetry_by_name.bl_idname)
            
            row = layout.row()
            row.operator(symmetry_by_position.bl_idname)
            
            
        elif type(activeArmature) is bpy.types.Mesh:
            row = layout.row()
            row.label(text="Active mesh: {}".format(obj.name))
            
            row = layout.row()
            row.operator(remove_useless_groups.bl_idname)
            
            row = layout.row()
            row.operator(mute_shape_keys.bl_idname)
            
            row.operator(unmute_shape_keys.bl_idname)
            
            row = layout.row()
            row.operator(github_link.bl_idname)

classes = [ArmatureCleanupPanel, symmetry_by_name, visibility_to_front, 
    prune_useless_bones, origin_to_root, head_sort, key_sort, hands_sort,
    blends_to_opaque, symmetry_by_position, print_center_bones,
    remove_useless_groups, mute_shape_keys, unmute_shape_keys, github_link]

def register():
    print("registering")
    
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Object.sort_key = bpy.props.StringProperty(
    
        name="Layer sort key",
        description="Enter a string that appears in the names of some bones",
        default = "twist"
    )
    
    bpy.types.Object.sort_layer = bpy.props.IntProperty(
    
        name="Layer sort destination",
        description="Enter the # of the layer to sort to",
        default = 31
    )


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    
    
    del bpy.types.Object.sort_key
    del bpy.types.Object.sort_layer


if __name__ == "__main__":
    register()