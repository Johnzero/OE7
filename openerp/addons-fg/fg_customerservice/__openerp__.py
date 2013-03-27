# -*- encoding: utf-8 -*-

{
    "name": "富光售后服务",
    "version": "1.0",
    "category" : "富光",
    "description": """富光售后支持模块""",
    "author": "富光",
    "website": "www.fuguang.com",
    "depends": ["base","fg_picking"],
    "init_xml": [],
    "update_xml": [
                "security/group.xml",
                "security/ir.model.access.csv",
                "wizard/change_name.xml",
                "service_view.xml",],
    "demo_xml": [],
    "installable": True,
    "active": False,
    "application":True,
}