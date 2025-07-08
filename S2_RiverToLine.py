# -*- coding: utf-8 -*-

import arcpy
import os


def process_river_toline(base_path):
    arcpy.env.workspace = base_path
    input_river_polygon = os.path.join(base_path, "Final_Vector_Clean.shp")
    river_break = os.path.join(base_path, "River_Break.shp")

    # 确保输出的河岸线要素类存在，并添加区分左右岸的字段
    if not arcpy.Exists(river_break):
        arcpy.CreateFeatureclass_management(
            out_path=base_path,
            out_name='River_Break.shp',
            geometry_type='POLYLINE',
            template=None,
            spatial_reference=arcpy.Describe(input_river_polygon).spatialReference)
        arcpy.AddField_management(river_break, "Bank", "TEXT")

    # 遍历每一个多边形要素，创建缓冲区，提取轮廓线并分割
    with arcpy.da.SearchCursor(input_river_polygon, ["SHAPE@"]) as polygon_cursor:
        for polygon_row in polygon_cursor:
            # 为每个多边形创建缓冲区
            buffered_polygon = arcpy.Buffer_analysis(polygon_row[0], arcpy.Geometry(), "1 Meters", "FULL", "ROUND",
                                                     "NONE")

            # 提取缓冲区的轮廓线
            temp_outline = arcpy.PolygonToLine_management(buffered_polygon[0], arcpy.Geometry())

            bank_lines = {'Left': None, 'Right': None}
            bank_lengths = {'Left': 0, 'Right': 0}

            for line in temp_outline:
                if line and line.pointCount > 2:
                    points = [point for part in line for point in part]
                    # 找到最西、最东、最南和最北的点
                    west_most_point = min(points, key=lambda point: point.X)
                    east_most_point = max(points, key=lambda point: point.X)
                    south_most_point = min(points, key=lambda point: point.Y)
                    north_most_point = max(points, key=lambda point: point.Y)

                    # 判断河流主要走向
                    if abs(east_most_point.X - west_most_point.X) >= abs(north_most_point.Y - south_most_point.Y):
                        min_point, max_point = west_most_point, east_most_point
                    else:
                        min_point, max_point = south_most_point, north_most_point

                    min_index = points.index(min_point)
                    max_index = points.index(max_point)

                    if min_index <= max_index:
                        left_points = points[min_index:max_index + 1]
                        right_points = points[max_index:] + points[:min_index + 1]
                    else:
                        left_points = points[max_index:min_index + 1]
                        right_points = points[min_index:] + points[:max_index + 1]

                    # 创建左右岸的多段线几何
                    left_line = arcpy.Polyline(arcpy.Array(left_points), line.spatialReference)
                    right_line = arcpy.Polyline(arcpy.Array(right_points), line.spatialReference)

                    # 只保留最长的线
                    if left_line.length > bank_lengths['Left']:
                        bank_lines['Left'] = left_line
                        bank_lengths['Left'] = left_line.length
                    if right_line.length > bank_lengths['Right']:
                        bank_lines['Right'] = right_line
                        bank_lengths['Right'] = right_line.length

            # 使用 InsertCursor 将最长的左右岸线存储到 river_break
            with arcpy.da.InsertCursor(river_break, ["SHAPE@", "Bank"]) as river_cursor:
                if bank_lines['Left']:
                    river_cursor.insertRow([bank_lines['Left'], 'Left'])
                if bank_lines['Right']:
                    river_cursor.insertRow([bank_lines['Right'], 'Right'])

    print("操作完成")
# process_river_toline(r'D:\工作内容\Channel shift\test\2023')
