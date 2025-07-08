# -*- coding: utf-8 -*-
########################################################################################
import arcpy
from arcpy.sa import *
import os
########################################################################################
# 函数封装
from Func.S1_ProProcessing import preprocess_rivers
from Func.S2_RiverToLine import process_river_toline
from Func.S3_Centerline import process_Centerline
from Func.S4_Line_Correction import connect_river_lines
from Func.S5_Channel_Shift import analyze_Channel_Shift

from Para_Cal.P1_Point_DisTance import analyze_channel_shift_Point_Dis
from Para_Cal.P2_Avg_Shift import analyze_channel_shift_AvgLen
from Para_Cal.P3_Shift_Area import analyze_channel_shift_Area
from Para_Cal.P4_Curvature_of_Area import analyze_channel_shift_curvature
from Para_Cal.P5_River_Width import analyze_River_Width
from Para_Cal.P6_Meander_Ratio import analyze_channel_shift_Metrics
########################################################################################
# 参数设置

base = r"H:\Figure2\Red River shapefile\Buffer"
base_path = os.path.join(base, "Time2")
input_shp_name = "River Time 2.shp"

past = "Time1"

recent = "Time2"

river_name = "clipped_centerline.shp"
name = 'Significant_Areas.shp'
flag = 2

########################################################################################
if flag == 1:
    preprocess_rivers(base_path, input_shp_name)  # 数据预处理

    process_river_toline(base_path)  # 河流封闭要素开放

    process_Centerline(base_path)  # 中心线生成

    #connect_river_lines(base_path)  # 可选，连接中心线，减少断裂线
if flag == 2:
    analyze_Channel_Shift(base, past, recent, river_name,name)

if flag == 3:
    # Channel Shift 区域交点距离
    Point_Dis = analyze_channel_shift_Point_Dis(base, past, recent, river_name, name)
    print("Distances between significant areas and intersection points:", Point_Dis)
    print("Number of distances calculated:", len(Point_Dis))

    # Channel Shift 区域平均迁移距离
    avg_distance = analyze_channel_shift_AvgLen(base, past, recent, river_name, name)
    print("Average distances for all areas:", avg_distance)
    print("Number of distances calculated:", len(avg_distance))

    # Channel Shift 区域面积
    areas = analyze_channel_shift_Area(base, past, recent, river_name, name)
    print("Areas for all areas:", areas)
    print("Number of Areas calculated:", len(areas))

    # Channel Shift 区域中心线弯曲度
    curvature_ratios = analyze_channel_shift_curvature(base, past, recent, river_name, name)
    print("Calculated curvature ratios for intersected areas:", curvature_ratios)
    print("Number of curvature calculated:", len(curvature_ratios))

    # 河流宽度计算
    area, total_length_m, average_width = analyze_River_Width(base, past, river_name)
    print(f"面积：{area:.2f} 平方米")
    print(f"裁剪后的中心线长度：{total_length_m:.2f} 米")
    print(f"平均宽度：{average_width:.2f} 米")

    #河流弯道比计算
    curvature_radii, meander_ratios = analyze_channel_shift_Metrics(base, past, recent, river_name, name)
    # 打印结果
    print("Calculated curvature radii:", curvature_radii)
    print("Calculated meander ratios:", meander_ratios)
    print("Number of curvature radii:", len(curvature_radii))
    print("Number of meander ratios:", len(meander_ratios))