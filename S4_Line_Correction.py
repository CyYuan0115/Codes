# -*- coding: utf-8 -*-
import arcpy
import os

def connect_river_lines(base_path):
    arcpy.env.workspace = base_path
    arcpy.env.overwriteOutput = True

    # 输入的线要素类路径（生成临时副本以保护原始文件）
    input_line_feature = os.path.join(base_path, "clipped_centerline.shp")
    temp_line_feature = os.path.join(base_path, "temp_clipped_centerline.shp")
    projected_line_feature = os.path.join(base_path, "projected_temp_clipped_centerline.shp")
    arcpy.CopyFeatures_management(input_line_feature, temp_line_feature)
    print("Created temporary copy of the input line feature.")

    # 设置投影为 Albers 等积投影
    albers_projection = arcpy.SpatialReference("North America Albers Equal Area Conic")
    arcpy.Project_management(temp_line_feature, projected_line_feature, albers_projection)
    print("Projected the temporary line feature to Albers Equal Area Conic projection.")

    # 提取所有线要素的端点
    endpoints = os.path.join(base_path, "endpoints.shp")
    arcpy.FeatureVerticesToPoints_management(projected_line_feature, endpoints, "BOTH_ENDS")
    print("Extracted endpoints of all lines.")

    # 使用拓扑检查孤立端点，仅保留“断裂点”
    arcpy.MakeFeatureLayer_management(endpoints, "endpoints_layer")
    arcpy.SelectLayerByLocation_management("endpoints_layer", "BOUNDARY_TOUCHES", projected_line_feature, invert_spatial_relationship=True)
    isolated_points = os.path.join(base_path, "isolated_endpoints.shp")
    arcpy.CopyFeatures_management("endpoints_layer", isolated_points)
    print("Isolated endpoints identified as breakpoints.")

    # 创建一个空的线要素类用于存放连接线，并添加长度字段
    connection_lines = os.path.join(base_path, "temp_connections.shp")
    arcpy.CreateFeatureclass_management(base_path, "temp_connections.shp", "POLYLINE",
                                        spatial_reference=projected_line_feature)
    arcpy.AddField_management(connection_lines, "Length", "DOUBLE")
    print("Created temporary connection lines feature class.")

    # 使用游标读取端点，计算最短连接线，并将它们存储
    points = [row[0] for row in arcpy.da.SearchCursor(isolated_points, ["SHAPE@XY"])]
    while len(points) > 1:
        min_distance = float('inf')
        closest_pair = None
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dist = ((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2) ** 0.5
                if dist < min_distance:
                    min_distance = dist
                    closest_pair = (points[i], points[j])

        # 如果找到合适的点对，则创建连接线
        if closest_pair and min_distance <= 100:  # 保证连接不超过100米
            array = arcpy.Array([arcpy.Point(*closest_pair[0]), arcpy.Point(*closest_pair[1])])
            polyline = arcpy.Polyline(array)
            line_length = polyline.length  # 计算线段长度

            # 检查线长度并在条件满足时插入
            if line_length <= 100:
                with arcpy.da.InsertCursor(connection_lines, ["SHAPE@", "Length"]) as cursor:
                    cursor.insertRow([polyline, line_length])

            # 移除已连接的点
            points.remove(closest_pair[0])
            points.remove(closest_pair[1])
        else:
            break  # 如果没有找到任何可连接的点对，终止循环

    print("Completed connecting closest breakpoints with lines.")

    # 合并原始线要素和新创建的连接线
    output_line_feature = os.path.join(base_path, "Connected_River.shp")
    arcpy.Merge_management([projected_line_feature, connection_lines], output_line_feature)
    print("Merged original lines and connection lines.")

    # 清理临时文件
    arcpy.Delete_management(endpoints)
    arcpy.Delete_management(connection_lines)
    arcpy.Delete_management(isolated_points)
    arcpy.Delete_management(temp_line_feature)
    arcpy.Delete_management(projected_line_feature)
    print("Cleaned up temporary files.")

    print("All lines have been connected and merged into:", output_line_feature)

# 示例用法
# connect_river_lines(r'D:\工作内容\Channel shift\test\2023')
