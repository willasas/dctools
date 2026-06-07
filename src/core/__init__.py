"""核心功能模块"""

from .folder_creator import create_single_folder, batch_create_folders
from .file_renamer import batch_rename_files, preview_rename, batch_move_files, preview_move
from .duplicate_remover import remove_duplicates, preview_duplicates, get_duplicates_details
from .excel_exporter import export_to_excel, batch_export_folders
from .folder_info import get_folder_info, analyze_folder_structure
from .image_property_editor import batch_add_property, batch_remove_properties, add_media_property, remove_media_properties

__all__ = [
    "create_single_folder",
    "batch_create_folders",
    "batch_rename_files",
    "preview_rename",
    "batch_move_files",
    "preview_move",
    "remove_duplicates",
    "preview_duplicates",
    "get_duplicates_details",
    "export_to_excel",
    "batch_export_folders",
    "get_folder_info",
    "analyze_folder_structure",
    "batch_add_property",
    "batch_remove_properties",
    "add_media_property",
    "remove_media_properties"
]
