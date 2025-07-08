# -*- coding: utf-8 -*-

import arcpy
from arcpy.sa import *
import os


def preprocess_rivers(base_path, input_shp_name):
    arcpy.env.workspace = base_path  # 设置工作环境
    arcpy.env.overwriteOutput = True

    input_vector_path = os.path.join(base_path, input_shp_name)
    buffered_path = os.path.join(base_path, "Buffered_Rivers.shp")
    output_vector_clean_path = os.path.join(base_path, "Final_Vector_Clean.shp")

    # 确保Spatial Analyst扩展模块已授权
    arcpy.CheckOutExtension("Spatial")

    # 添加面积字段
    arcpy.management.AddField(input_vector_path, "AREA_SQM", "DOUBLE")

    # 计算面积
    arcpy.management.CalculateField(input_vector_path, "AREA_SQM", "!shape.area!", "PYTHON_9.3")

    # 计算所有要素的总面积
    total_area = 0
    with arcpy.da.SearchCursor(input_vector_path, ["AREA_SQM"]) as cursor:
        for row in cursor:
            total_area += row[0]

    # 计算0.5%的总面积阈值
    threshold_area = total_area * 0.005

    # 筛选条件：面积大于阈值的要素
    expression = f"AREA_SQM > {threshold_area}"

    # 删除可能存在的临时图层
    if arcpy.Exists("lyr"):
        arcpy.management.Delete("lyr")

    arcpy.management.MakeFeatureLayer(input_vector_path, "lyr")
    arcpy.management.SelectLayerByAttribute("lyr", "NEW_SELECTION", expression)

    # 创建缓冲区
    arcpy.Buffer_analysis("lyr", buffered_path, "1 Meters", "FULL", "ROUND", "NONE")

    # 使用EliminatePolygonPart消除面积小于50%或100000平方米的面部件
    arcpy.EliminatePolygonPart_management(
        in_features=buffered_path,
        out_feature_class=output_vector_clean_path,
        condition="AREA_OR_PERCENT",
        part_area_percent="50",
        part_area="0.005",
        part_option="ANY"
    )

    # 保存所有符合条件的要素
    arcpy.management.CopyFeatures("lyr", output_vector_clean_path)

    print("所有操作完成，结果保存到：", output_vector_clean_path)

    # 清理临时图层
    arcpy.Delete_management("lyr")
    arcpy.Delete_management(buffered_path)

# preprocess_rivers(r"D:\工作内容\Channel shift\Missibi\GSW_Ununion","Missibi_1980s.shp")
