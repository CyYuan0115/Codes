# -*- coding: utf-8 -*-
import arcpy
from arcpy.sa import *
import os


def process_Centerline(base_path):
    # 设置环境
    arcpy.env.workspace = base_path
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.XYTolerance = "0.0001 Meters"
    arcpy.env.scratchWorkspace = r"D:\LargeDiskSpace"  # 设置足够空间的临时文件夹
    arcpy.env.tileSize = "4096 4096"  # 设置更大的瓦片大小
    arcpy.env.parallelProcessingFactor = "100%"  # 使用所有CPU核心

    # 输入和输出
    input_feature = os.path.join(base_path, "River_Break.shp")
    output_raster = os.path.join(base_path, "euclidean_allocation.tif")
    clip_feature = os.path.join(base_path, "Final_Vector_Clean.shp")

    # 设置处理参数
    cell_size = 0.0003  # 栅格单元大小

    # 执行欧式分配
    allocation_raster = EucAllocation(input_feature, cell_size=cell_size)

    # 保存输出栅格
    allocation_raster.save(output_raster)
    print("Euclidean allocation raster created with cell size:", cell_size)

    # 栅格转面
    polygon_output = os.path.join(base_path, "allocation_polygon.shp")
    arcpy.RasterToPolygon_conversion(output_raster, polygon_output, "NO_SIMPLIFY")

    # 要素转线
    line_output = os.path.join(base_path, "allocation_line.shp")
    arcpy.PolygonToLine_management(polygon_output, line_output)

    # 使用clip_feature进行裁剪
    clipped_line_output = os.path.join(base_path, "clipped_centerline.shp")
    arcpy.Clip_analysis(line_output, clip_feature, clipped_line_output)

    print("Clipped centerline created based on input shapefile.")

    # 删除不再需要的过程文件
    # arcpy.Delete_management(output_raster)
    arcpy.Delete_management(polygon_output)
    arcpy.Delete_management(line_output)

# process_Centerline(r'D:\工作内容\Channel shift\test\2023')
