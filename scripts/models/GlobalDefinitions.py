# enums
kFront, kBack, kLeft, kRight = range(4)
side_names = ['front', 'back', 'left', 'right']

# formatting of building parts
building_root_format        = "{}"                   # NewBuilding_grp

floors_root_format          = "{}_floors"            # NewBuilding_floors
floor_walls_root_format     = "{}_walls_{}"          # NewBuilding_floor_1_walls_right
floor_corner_root_format    = "{}_corners"           # NewBuilding_floor_1_corners

floor_format         = "{}_floor_{}"                 # NewBuilding_floor_1
floor_wall_format    = "{}_floor_{}_{}_wall_{}"      # NewBuilding_floor_1_right_wall_1
floor_corner_format  = "{}_floor_{}_{}_corner"       # newBuilding_floor_1_right_corner

roof_root_format            = "{}_roof"              # NewBuilding_roof
roof_tiles_root_format      = "{}_tiles"             # NewBuilding_roof_tiles
roof_corners_root_format    = "{}_corners"           # NewBuilding_roof_corners
roof_edges_root_format       = "{}_edges_{}"         # NewBuilding_floor_1_right_wall_1

roof_tile_format    = "{}_roof_tile_{}_{}"           # NewBuilding_roof_tile_1_1
roof_corner_format  = "{}_roof_{}_corner"            # NewBuilding_roof_right_corner
roof_edge_format    = "{}_roof_{}_edge_{}"           # NewBuilding_roof_right_edge_1
